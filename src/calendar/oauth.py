"""
OAuth authentication manager for calendar providers.

This module provides a provider-agnostic OAuth authentication flow for calendar
integration, including secure credential storage, token refresh, and validation.
"""

import os
import json
import base64
import time
import uuid
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

from .interfaces import AuthResult, AuthStatus
from .exceptions import AuthError, ValidationError

# Configure logger
logger = logging.getLogger(__name__)


class OAuthConfig:
    """
    OAuth configuration for a calendar provider.
    
    Attributes:
        client_id (str): OAuth client ID.
        client_secret (str): OAuth client secret.
        auth_url (str): Authorization URL.
        token_url (str): Token URL.
        redirect_uri (str): Redirect URI for OAuth callback.
        scopes (List[str]): List of OAuth scopes.
        additional_params (Dict[str, str]): Additional authorization parameters.
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
        redirect_uri: str,
        scopes: List[str],
        additional_params: Optional[Dict[str, str]] = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.additional_params = additional_params or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert OAuth configuration to dictionary."""
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'auth_url': self.auth_url,
            'token_url': self.token_url,
            'redirect_uri': self.redirect_uri,
            'scopes': self.scopes,
            'additional_params': self.additional_params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OAuthConfig':
        """Create OAuth configuration from dictionary."""
        return cls(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            auth_url=data['auth_url'],
            token_url=data['token_url'],
            redirect_uri=data['redirect_uri'],
            scopes=data['scopes'],
            additional_params=data.get('additional_params', {})
        )


class CredentialStorage:
    """
    Secure storage for OAuth credentials using AES-256 encryption.
    
    This class handles encryption and decryption of OAuth tokens and credentials
    using AES-256 encryption with user-specific keys derived using PBKDF2.
    """
    
    # Constants for encryption
    KEY_LENGTH = 32  # 256 bits
    SALT_LENGTH = 16
    IV_LENGTH = 16
    ITERATIONS = 100000
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize credential storage.
        
        Args:
            storage_path (Optional[str]): Path to store encrypted credentials.
                If None, uses default location in user's home directory.
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Default to a hidden directory in user's home
            self.storage_path = Path.home() / '.bills_tracker' / 'credentials'
        
        # Create directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # User key is derived from machine-specific information
        # This is a simplified approach - in production, consider more secure key management
        self._user_key = None
    
    def _get_user_key(self, password: Optional[str] = None) -> bytes:
        """
        Get or create user-specific encryption key.
        
        Args:
            password (Optional[str]): Optional password for key derivation.
                If None, uses machine-specific information.
                
        Returns:
            bytes: User-specific encryption key.
        """
        if self._user_key is not None:
            return self._user_key
        
        # If password is provided, use it for key derivation
        if password:
            # Generate a salt if it doesn't exist
            salt_path = self.storage_path / 'salt.bin'
            if salt_path.exists():
                salt = salt_path.read_bytes()
            else:
                salt = get_random_bytes(self.SALT_LENGTH)
                salt_path.write_bytes(salt)
            
            # Derive key using PBKDF2
            self._user_key = PBKDF2(
                password.encode('utf-8'),
                salt,
                dkLen=self.KEY_LENGTH,
                count=self.ITERATIONS
            )
        else:
            # Use machine-specific information for key derivation
            # This is a simplified approach - in production, use a more secure method
            machine_id = self._get_machine_id()
            salt = uuid.getnode().to_bytes(8, 'big')  # MAC address as salt
            
            # Derive key using PBKDF2
            self._user_key = PBKDF2(
                machine_id.encode('utf-8'),
                salt,
                dkLen=self.KEY_LENGTH,
                count=self.ITERATIONS
            )
        
        return self._user_key
    
    def _get_machine_id(self) -> str:
        """
        Get a unique machine identifier.
        
        Returns:
            str: Unique machine identifier.
        """
        # Try to get a stable machine ID
        # This is a simplified approach - in production, use a more robust method
        try:
            if os.name == 'nt':  # Windows
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Microsoft\Cryptography") as key:
                    return winreg.QueryValueEx(key, "MachineGuid")[0]
            elif os.path.exists('/etc/machine-id'):  # Linux
                with open('/etc/machine-id', 'r') as f:
                    return f.read().strip()
            elif os.path.exists('/var/lib/dbus/machine-id'):  # Linux (alternative)
                with open('/var/lib/dbus/machine-id', 'r') as f:
                    return f.read().strip()
            elif os.path.exists('/usr/sbin/system_profiler'):  # macOS
                import subprocess
                result = subprocess.run(['system_profiler', 'SPHardwareDataType'], 
                                       capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Hardware UUID' in line:
                        return line.split(':')[1].strip()
        except Exception as e:
            logger.warning(f"Failed to get machine ID: {e}")
        
        # Fallback to a combination of hostname and username
        return f"{os.getlogin()}@{os.uname().nodename}" if hasattr(os, 'uname') else f"{os.getlogin()}@{os.environ.get('COMPUTERNAME', 'unknown')}"
    
    def encrypt(self, data: Dict[str, Any], password: Optional[str] = None) -> bytes:
        """
        Encrypt data using AES-256.
        
        Args:
            data (Dict[str, Any]): Data to encrypt.
            password (Optional[str]): Optional password for encryption.
                
        Returns:
            bytes: Encrypted data.
        """
        # Convert data to JSON string
        json_data = json.dumps(data).encode('utf-8')
        
        # Get user key
        key = self._get_user_key(password)
        
        # Generate random IV
        iv = get_random_bytes(self.IV_LENGTH)
        
        # Create cipher and encrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(json_data, AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        
        # Combine IV and encrypted data
        return iv + encrypted_data
    
    def decrypt(self, encrypted_data: bytes, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Decrypt data using AES-256.
        
        Args:
            encrypted_data (bytes): Encrypted data.
            password (Optional[str]): Optional password for decryption.
                
        Returns:
            Dict[str, Any]: Decrypted data.
        """
        # Get user key
        key = self._get_user_key(password)
        
        # Extract IV from encrypted data
        iv = encrypted_data[:self.IV_LENGTH]
        actual_encrypted_data = encrypted_data[self.IV_LENGTH:]
        
        # Create cipher and decrypt
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded_data = cipher.decrypt(actual_encrypted_data)
        
        try:
            # Unpad and convert to JSON
            decrypted_data = unpad(decrypted_padded_data, AES.block_size)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            raise AuthError(f"Failed to decrypt data: {e}")
    
    def store_credentials(self, provider_id: str, user_id: str, credentials: Dict[str, Any], password: Optional[str] = None) -> bool:
        """
        Store encrypted credentials for a provider and user.
        
        Args:
            provider_id (str): Calendar provider ID.
            user_id (str): User ID or email.
            credentials (Dict[str, Any]): Credentials to store.
            password (Optional[str]): Optional password for encryption.
                
        Returns:
            bool: True if successful.
        """
        try:
            # Create filename from provider and user ID
            filename = f"{provider_id}_{base64.urlsafe_b64encode(user_id.encode()).decode()}.enc"
            file_path = self.storage_path / filename
            
            # Encrypt and store credentials
            encrypted_data = self.encrypt(credentials, password)
            file_path.write_bytes(encrypted_data)
            
            return True
        except Exception as e:
            logger.error(f"Failed to store credentials: {e}")
            return False
    
    def retrieve_credentials(self, provider_id: str, user_id: str, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve encrypted credentials for a provider and user.
        
        Args:
            provider_id (str): Calendar provider ID.
            user_id (str): User ID or email.
            password (Optional[str]): Optional password for decryption.
                
        Returns:
            Optional[Dict[str, Any]]: Decrypted credentials or None if not found.
        """
        try:
            # Create filename from provider and user ID
            filename = f"{provider_id}_{base64.urlsafe_b64encode(user_id.encode()).decode()}.enc"
            file_path = self.storage_path / filename
            
            # Check if file exists
            if not file_path.exists():
                return None
            
            # Read and decrypt credentials
            encrypted_data = file_path.read_bytes()
            return self.decrypt(encrypted_data, password)
        except Exception as e:
            logger.error(f"Failed to retrieve credentials: {e}")
            return None
    
    def delete_credentials(self, provider_id: str, user_id: str) -> bool:
        """
        Delete stored credentials for a provider and user.
        
        Args:
            provider_id (str): Calendar provider ID.
            user_id (str): User ID or email.
                
        Returns:
            bool: True if successful.
        """
        try:
            # Create filename from provider and user ID
            filename = f"{provider_id}_{base64.urlsafe_b64encode(user_id.encode()).decode()}.enc"
            file_path = self.storage_path / filename
            
            # Delete file if it exists
            if file_path.exists():
                file_path.unlink()
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete credentials: {e}")
            return False
    
    def list_providers(self) -> List[str]:
        """
        List all providers with stored credentials.
        
        Returns:
            List[str]: List of provider IDs.
        """
        providers = set()
        for file_path in self.storage_path.glob('*.enc'):
            try:
                provider_id = file_path.name.split('_')[0]
                providers.add(provider_id)
            except Exception:
                continue
        
        return list(providers)
    
    def list_users(self, provider_id: str) -> List[str]:
        """
        List all users with stored credentials for a provider.
        
        Args:
            provider_id (str): Calendar provider ID.
                
        Returns:
            List[str]: List of user IDs.
        """
        users = []
        for file_path in self.storage_path.glob(f'{provider_id}_*.enc'):
            try:
                encoded_user = file_path.name.split('_')[1].split('.')[0]
                user_id = base64.urlsafe_b64decode(encoded_user).decode('utf-8')
                users.append(user_id)
            except Exception:
                continue
        
        return users


class OAuthManager:
    """
    Provider-agnostic OAuth authentication manager.
    
    This class handles OAuth authentication flows for different calendar providers,
    including token refresh, validation, and secure storage.
    """
    
    def __init__(self, credential_storage: Optional[CredentialStorage] = None):
        """
        Initialize OAuth manager.
        
        Args:
            credential_storage (Optional[CredentialStorage]): Credential storage instance.
                If None, creates a new instance.
        """
        self.credential_storage = credential_storage or CredentialStorage()
        self.provider_configs: Dict[str, OAuthConfig] = {}
        self.auth_states: Dict[str, Dict[str, Any]] = {}
    
    def register_provider(self, provider_id: str, config: OAuthConfig) -> bool:
        """
        Register a calendar provider with OAuth configuration.
        
        Args:
            provider_id (str): Provider identifier.
            config (OAuthConfig): OAuth configuration.
                
        Returns:
            bool: True if successful.
        """
        if not provider_id or not provider_id.strip():
            raise ValidationError("Provider ID is required", "provider_id")
        
        self.provider_configs[provider_id.lower()] = config
        return True
    
    def get_provider_config(self, provider_id: str) -> Optional[OAuthConfig]:
        """
        Get OAuth configuration for a provider.
        
        Args:
            provider_id (str): Provider identifier.
                
        Returns:
            Optional[OAuthConfig]: OAuth configuration or None if not found.
        """
        return self.provider_configs.get(provider_id.lower())
    
    def initiate_auth_flow(self, provider_id: str) -> Tuple[str, str]:
        """
        Initiate OAuth authentication flow.
        
        Args:
            provider_id (str): Provider identifier.
                
        Returns:
            Tuple[str, str]: (auth_url, state) where auth_url is the URL to redirect the user to
                and state is a unique state identifier for this flow.
        """
        provider_id = provider_id.lower()
        config = self.get_provider_config(provider_id)
        if not config:
            raise AuthError(f"Provider '{provider_id}' not registered")
        
        # Generate state parameter for CSRF protection
        state = str(uuid.uuid4())
        
        # Store state for later verification
        self.auth_states[state] = {
            'provider_id': provider_id,
            'created_at': datetime.now().isoformat()
        }
        
        # Build authorization URL
        params = {
            'client_id': config.client_id,
            'redirect_uri': config.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(config.scopes),
            'state': state,
            'access_type': 'offline',  # Request refresh token
            'prompt': 'consent'  # Force consent screen for refresh token
        }
        
        # Add additional parameters
        params.update(config.additional_params)
        
        # Build query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{config.auth_url}?{query_string}"
        
        return auth_url, state
    
    def handle_auth_callback(self, code: str, state: str) -> AuthResult:
        """
        Handle OAuth callback with authorization code.
        
        Args:
            code (str): Authorization code from callback.
            state (str): State parameter from callback.
                
        Returns:
            AuthResult: Authentication result.
        """
        # Verify state parameter
        if state not in self.auth_states:
            raise AuthError("Invalid state parameter")
        
        # Get provider ID from state
        provider_data = self.auth_states.pop(state)
        provider_id = provider_data['provider_id']
        
        # Get provider configuration
        config = self.get_provider_config(provider_id)
        if not config:
            raise AuthError(f"Provider '{provider_id}' not registered")
        
        # Exchange code for tokens
        try:
            import requests
            
            # Prepare token request
            token_data = {
                'client_id': config.client_id,
                'client_secret': config.client_secret,
                'code': code,
                'redirect_uri': config.redirect_uri,
                'grant_type': 'authorization_code'
            }
            
            # Make token request
            response = requests.post(config.token_url, data=token_data)
            response.raise_for_status()
            token_info = response.json()
            
            # Extract tokens
            access_token = token_info.get('access_token')
            refresh_token = token_info.get('refresh_token')
            expires_in = token_info.get('expires_in', 3600)  # Default to 1 hour
            
            if not access_token:
                raise AuthError("No access token in response")
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Get user information
            user_info = self._get_user_info(provider_id, access_token)
            
            # Store tokens securely
            if user_info and 'email' in user_info:
                credentials = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_at': expires_at.isoformat(),
                    'user_info': user_info
                }
                
                self.credential_storage.store_credentials(provider_id, user_info['email'], credentials)
            
            # Return authentication result
            return AuthResult(
                status=AuthStatus.SUCCESS,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                user_info=user_info
            )
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return AuthResult(
                status=AuthStatus.FAILED,
                error_message=str(e)
            )
    
    def refresh_token(self, provider_id: str, user_id: str) -> AuthResult:
        """
        Refresh OAuth access token.
        
        Args:
            provider_id (str): Provider identifier.
            user_id (str): User ID or email.
                
        Returns:
            AuthResult: Authentication result.
        """
        provider_id = provider_id.lower()
        
        # Get provider configuration
        config = self.get_provider_config(provider_id)
        if not config:
            raise AuthError(f"Provider '{provider_id}' not registered")
        
        # Get stored credentials
        credentials = self.credential_storage.retrieve_credentials(provider_id, user_id)
        if not credentials:
            return AuthResult(
                status=AuthStatus.FAILED,
                error_message=f"No credentials found for {provider_id}/{user_id}"
            )
        
        # Check if refresh token exists
        refresh_token = credentials.get('refresh_token')
        if not refresh_token:
            return AuthResult(
                status=AuthStatus.FAILED,
                error_message="No refresh token available"
            )
        
        # Refresh token
        try:
            import requests
            
            # Prepare refresh request
            refresh_data = {
                'client_id': config.client_id,
                'client_secret': config.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            # Make refresh request
            response = requests.post(config.token_url, data=refresh_data)
            response.raise_for_status()
            token_info = response.json()
            
            # Extract new access token
            access_token = token_info.get('access_token')
            new_refresh_token = token_info.get('refresh_token', refresh_token)  # Some providers don't return a new refresh token
            expires_in = token_info.get('expires_in', 3600)  # Default to 1 hour
            
            if not access_token:
                raise AuthError("No access token in response")
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Update stored credentials
            credentials['access_token'] = access_token
            credentials['refresh_token'] = new_refresh_token
            credentials['expires_at'] = expires_at.isoformat()
            
            self.credential_storage.store_credentials(provider_id, user_id, credentials)
            
            # Return authentication result
            return AuthResult(
                status=AuthStatus.SUCCESS,
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_at=expires_at,
                user_info=credentials.get('user_info')
            )
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return AuthResult(
                status=AuthStatus.FAILED,
                error_message=str(e)
            )
    
    def get_valid_token(self, provider_id: str, user_id: str) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            provider_id (str): Provider identifier.
            user_id (str): User ID or email.
                
        Returns:
            Optional[str]: Valid access token or None if not available.
        """
        provider_id = provider_id.lower()
        
        # Get stored credentials
        credentials = self.credential_storage.retrieve_credentials(provider_id, user_id)
        if not credentials:
            return None
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(credentials.get('expires_at', '2000-01-01T00:00:00'))
        if datetime.now() >= expires_at:
            # Token is expired, refresh it
            result = self.refresh_token(provider_id, user_id)
            if result.is_success:
                return result.access_token
            return None
        
        # Token is still valid
        return credentials.get('access_token')
    
    def revoke_access(self, provider_id: str, user_id: str) -> bool:
        """
        Revoke OAuth access and delete stored credentials.
        
        Args:
            provider_id (str): Provider identifier.
            user_id (str): User ID or email.
                
        Returns:
            bool: True if successful.
        """
        provider_id = provider_id.lower()
        
        # Get stored credentials
        credentials = self.credential_storage.retrieve_credentials(provider_id, user_id)
        if not credentials:
            return True  # Nothing to revoke
        
        # Get access token
        access_token = credentials.get('access_token')
        if not access_token:
            # No token to revoke, just delete credentials
            return self.credential_storage.delete_credentials(provider_id, user_id)
        
        # Attempt to revoke token (provider-specific)
        try:
            self._revoke_token(provider_id, access_token)
        except Exception as e:
            logger.warning(f"Failed to revoke token: {e}")
        
        # Delete stored credentials
        return self.credential_storage.delete_credentials(provider_id, user_id)
    
    def validate_token(self, provider_id: str, token: str) -> bool:
        """
        Validate an access token.
        
        Args:
            provider_id (str): Provider identifier.
            token (str): Access token to validate.
                
        Returns:
            bool: True if token is valid.
        """
        provider_id = provider_id.lower()
        
        try:
            # Provider-specific token validation
            if provider_id == 'google':
                return self._validate_google_token(token)
            elif provider_id == 'outlook':
                return self._validate_outlook_token(token)
            else:
                # Generic validation by making a test API call
                return self._validate_generic_token(provider_id, token)
        except Exception as e:
            logger.warning(f"Token validation error: {e}")
            return False
    
    def list_connected_accounts(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all connected calendar accounts.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary of provider IDs to lists of user info.
        """
        result = {}
        
        # Get all providers with stored credentials
        providers = self.credential_storage.list_providers()
        
        for provider_id in providers:
            result[provider_id] = []
            
            # Get all users for this provider
            users = self.credential_storage.list_users(provider_id)
            
            for user_id in users:
                # Get user info from stored credentials
                credentials = self.credential_storage.retrieve_credentials(provider_id, user_id)
                if credentials and 'user_info' in credentials:
                    result[provider_id].append(credentials['user_info'])
        
        return result
    
    def _get_user_info(self, provider_id: str, access_token: str) -> Dict[str, Any]:
        """
        Get user information using access token.
        
        Args:
            provider_id (str): Provider identifier.
            access_token (str): Access token.
                
        Returns:
            Dict[str, Any]: User information.
        """
        try:
            import requests
            
            # Provider-specific user info endpoints
            if provider_id == 'google':
                response = requests.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                response.raise_for_status()
                data = response.json()
                return {
                    'id': data.get('sub'),
                    'email': data.get('email'),
                    'name': data.get('name'),
                    'picture': data.get('picture')
                }
            elif provider_id == 'outlook':
                response = requests.get(
                    'https://graph.microsoft.com/v1.0/me',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                response.raise_for_status()
                data = response.json()
                return {
                    'id': data.get('id'),
                    'email': data.get('userPrincipalName'),
                    'name': data.get('displayName')
                }
            else:
                # Generic implementation - return empty dict
                return {}
        except Exception as e:
            logger.warning(f"Failed to get user info: {e}")
            return {}
    
    def _revoke_token(self, provider_id: str, token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            provider_id (str): Provider identifier.
            token (str): Access token to revoke.
                
        Returns:
            bool: True if successful.
        """
        try:
            import requests
            
            # Provider-specific revocation endpoints
            if provider_id == 'google':
                response = requests.post(
                    'https://oauth2.googleapis.com/revoke',
                    params={'token': token}
                )
                return response.status_code == 200
            elif provider_id == 'outlook':
                # Microsoft Graph doesn't have a standard revocation endpoint
                # Token will expire naturally
                return True
            else:
                # Generic implementation - assume success
                return True
        except Exception:
            return False
    
    def _validate_google_token(self, token: str) -> bool:
        """
        Validate a Google OAuth token.
        
        Args:
            token (str): Access token to validate.
                
        Returns:
            bool: True if token is valid.
        """
        try:
            import requests
            
            response = requests.get(
                'https://oauth2.googleapis.com/tokeninfo',
                params={'access_token': token}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _validate_outlook_token(self, token: str) -> bool:
        """
        Validate a Microsoft Outlook OAuth token.
        
        Args:
            token (str): Access token to validate.
                
        Returns:
            bool: True if token is valid.
        """
        try:
            import requests
            
            response = requests.get(
                'https://graph.microsoft.com/v1.0/me',
                headers={'Authorization': f'Bearer {token}'}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def _validate_generic_token(self, provider_id: str, token: str) -> bool:
        """
        Validate a token using a generic approach.
        
        Args:
            provider_id (str): Provider identifier.
            token (str): Access token to validate.
                
        Returns:
            bool: True if token is valid.
        """
        # This is a placeholder - in a real implementation, you would
        # make a lightweight API call to validate the token
        return True
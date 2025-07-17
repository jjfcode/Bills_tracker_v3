"""
Unit tests for OAuth manager.

This module tests the OAuth manager functionality, including credential storage,
token management, and authentication flow.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

from src.calendar.oauth import OAuthManager, OAuthConfig, CredentialStorage
from src.calendar.interfaces import AuthStatus
from src.calendar.exceptions import AuthError, ValidationError


class TestOAuthConfig(unittest.TestCase):
    """Test OAuth configuration class."""
    
    def test_oauth_config_creation(self):
        """Test creating an OAuth configuration."""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            auth_url="https://example.com/auth",
            token_url="https://example.com/token",
            redirect_uri="http://localhost:8080/callback",
            scopes=["calendar.read", "calendar.write"],
            additional_params={"access_type": "offline"}
        )
        
        self.assertEqual(config.client_id, "test_client_id")
        self.assertEqual(config.client_secret, "test_client_secret")
        self.assertEqual(config.auth_url, "https://example.com/auth")
        self.assertEqual(config.token_url, "https://example.com/token")
        self.assertEqual(config.redirect_uri, "http://localhost:8080/callback")
        self.assertEqual(config.scopes, ["calendar.read", "calendar.write"])
        self.assertEqual(config.additional_params, {"access_type": "offline"})
    
    def test_oauth_config_to_dict(self):
        """Test converting OAuth configuration to dictionary."""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            auth_url="https://example.com/auth",
            token_url="https://example.com/token",
            redirect_uri="http://localhost:8080/callback",
            scopes=["calendar.read", "calendar.write"],
            additional_params={"access_type": "offline"}
        )
        
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict["client_id"], "test_client_id")
        self.assertEqual(config_dict["client_secret"], "test_client_secret")
        self.assertEqual(config_dict["auth_url"], "https://example.com/auth")
        self.assertEqual(config_dict["token_url"], "https://example.com/token")
        self.assertEqual(config_dict["redirect_uri"], "http://localhost:8080/callback")
        self.assertEqual(config_dict["scopes"], ["calendar.read", "calendar.write"])
        self.assertEqual(config_dict["additional_params"], {"access_type": "offline"})
    
    def test_oauth_config_from_dict(self):
        """Test creating OAuth configuration from dictionary."""
        config_dict = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "auth_url": "https://example.com/auth",
            "token_url": "https://example.com/token",
            "redirect_uri": "http://localhost:8080/callback",
            "scopes": ["calendar.read", "calendar.write"],
            "additional_params": {"access_type": "offline"}
        }
        
        config = OAuthConfig.from_dict(config_dict)
        
        self.assertEqual(config.client_id, "test_client_id")
        self.assertEqual(config.client_secret, "test_client_secret")
        self.assertEqual(config.auth_url, "https://example.com/auth")
        self.assertEqual(config.token_url, "https://example.com/token")
        self.assertEqual(config.redirect_uri, "http://localhost:8080/callback")
        self.assertEqual(config.scopes, ["calendar.read", "calendar.write"])
        self.assertEqual(config.additional_params, {"access_type": "offline"})


class TestCredentialStorage(unittest.TestCase):
    """Test credential storage class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for credential storage
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage_path = self.temp_dir.name
        self.storage = CredentialStorage(self.storage_path)
        
        # Sample credentials
        self.sample_credentials = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": datetime.now().isoformat(),
            "user_info": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User"
            }
        }
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
    
    @patch.object(CredentialStorage, '_get_user_key')
    def test_encrypt_decrypt(self, mock_get_user_key):
        """Test encrypting and decrypting data."""
        # Mock user key
        mock_get_user_key.return_value = b'0' * 32  # 32 bytes key
        
        # Encrypt data
        encrypted = self.storage.encrypt(self.sample_credentials)
        
        # Decrypt data
        decrypted = self.storage.decrypt(encrypted)
        
        # Verify decrypted data matches original
        self.assertEqual(decrypted["access_token"], self.sample_credentials["access_token"])
        self.assertEqual(decrypted["refresh_token"], self.sample_credentials["refresh_token"])
        self.assertEqual(decrypted["expires_at"], self.sample_credentials["expires_at"])
        self.assertEqual(decrypted["user_info"]["email"], self.sample_credentials["user_info"]["email"])
    
    @patch.object(CredentialStorage, '_get_user_key')
    def test_store_retrieve_credentials(self, mock_get_user_key):
        """Test storing and retrieving credentials."""
        # Mock user key
        mock_get_user_key.return_value = b'0' * 32  # 32 bytes key
        
        # Store credentials
        result = self.storage.store_credentials("google", "test@example.com", self.sample_credentials)
        self.assertTrue(result)
        
        # Retrieve credentials
        retrieved = self.storage.retrieve_credentials("google", "test@example.com")
        
        # Verify retrieved credentials match original
        self.assertEqual(retrieved["access_token"], self.sample_credentials["access_token"])
        self.assertEqual(retrieved["refresh_token"], self.sample_credentials["refresh_token"])
        self.assertEqual(retrieved["expires_at"], self.sample_credentials["expires_at"])
        self.assertEqual(retrieved["user_info"]["email"], self.sample_credentials["user_info"]["email"])
    
    @patch.object(CredentialStorage, '_get_user_key')
    def test_delete_credentials(self, mock_get_user_key):
        """Test deleting credentials."""
        # Mock user key
        mock_get_user_key.return_value = b'0' * 32  # 32 bytes key
        
        # Store credentials
        self.storage.store_credentials("google", "test@example.com", self.sample_credentials)
        
        # Delete credentials
        result = self.storage.delete_credentials("google", "test@example.com")
        self.assertTrue(result)
        
        # Verify credentials are deleted
        retrieved = self.storage.retrieve_credentials("google", "test@example.com")
        self.assertIsNone(retrieved)
    
    @patch.object(CredentialStorage, '_get_user_key')
    def test_list_providers(self, mock_get_user_key):
        """Test listing providers."""
        # Mock user key
        mock_get_user_key.return_value = b'0' * 32  # 32 bytes key
        
        # Store credentials for multiple providers
        self.storage.store_credentials("google", "test1@example.com", self.sample_credentials)
        self.storage.store_credentials("outlook", "test2@example.com", self.sample_credentials)
        
        # List providers
        providers = self.storage.list_providers()
        
        # Verify providers list
        self.assertIn("google", providers)
        self.assertIn("outlook", providers)
    
    @patch.object(CredentialStorage, '_get_user_key')
    def test_list_users(self, mock_get_user_key):
        """Test listing users for a provider."""
        # Mock user key
        mock_get_user_key.return_value = b'0' * 32  # 32 bytes key
        
        # Store credentials for multiple users
        self.storage.store_credentials("google", "test1@example.com", self.sample_credentials)
        self.storage.store_credentials("google", "test2@example.com", self.sample_credentials)
        
        # List users
        users = self.storage.list_users("google")
        
        # Verify users list
        self.assertIn("test1@example.com", users)
        self.assertIn("test2@example.com", users)


class TestOAuthManager(unittest.TestCase):
    """Test OAuth manager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create mock credential storage
        self.credential_storage = MagicMock()
        self.oauth_manager = OAuthManager(self.credential_storage)
        
        # Sample OAuth configuration
        self.google_config = OAuthConfig(
            client_id="google_client_id",
            client_secret="google_client_secret",
            auth_url="https://accounts.google.com/o/oauth2/auth",
            token_url="https://oauth2.googleapis.com/token",
            redirect_uri="http://localhost:8080/callback",
            scopes=["https://www.googleapis.com/auth/calendar"],
            additional_params={"access_type": "offline", "prompt": "consent"}
        )
        
        # Register provider
        self.oauth_manager.register_provider("google", self.google_config)
    
    def test_register_provider(self):
        """Test registering a provider."""
        # Register a new provider
        result = self.oauth_manager.register_provider("outlook", OAuthConfig(
            client_id="outlook_client_id",
            client_secret="outlook_client_secret",
            auth_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            redirect_uri="http://localhost:8080/callback",
            scopes=["https://graph.microsoft.com/calendars.readwrite"],
            additional_params={}
        ))
        
        self.assertTrue(result)
        self.assertIn("outlook", self.oauth_manager.provider_configs)
    
    def test_get_provider_config(self):
        """Test getting provider configuration."""
        # Get existing provider config
        config = self.oauth_manager.get_provider_config("google")
        self.assertEqual(config.client_id, "google_client_id")
        
        # Get non-existent provider config
        config = self.oauth_manager.get_provider_config("nonexistent")
        self.assertIsNone(config)
    
    def test_initiate_auth_flow(self):
        """Test initiating authentication flow."""
        # Initiate auth flow
        auth_url, state = self.oauth_manager.initiate_auth_flow("google")
        
        # Verify auth URL contains required parameters
        self.assertIn("https://accounts.google.com/o/oauth2/auth", auth_url)
        self.assertIn("client_id=google_client_id", auth_url)
        self.assertIn("redirect_uri=http://localhost:8080/callback", auth_url)
        self.assertIn("response_type=code", auth_url)
        self.assertIn("scope=https://www.googleapis.com/auth/calendar", auth_url)
        self.assertIn(f"state={state}", auth_url)
        self.assertIn("access_type=offline", auth_url)
        self.assertIn("prompt=consent", auth_url)
        
        # Verify state is stored
        self.assertIn(state, self.oauth_manager.auth_states)
        self.assertEqual(self.oauth_manager.auth_states[state]["provider_id"], "google")
    
    def test_initiate_auth_flow_invalid_provider(self):
        """Test initiating auth flow with invalid provider."""
        with self.assertRaises(AuthError):
            self.oauth_manager.initiate_auth_flow("nonexistent")
    
    @patch('requests.post')
    def test_handle_auth_callback(self, mock_post):
        """Test handling authentication callback."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        # Set up auth state
        state = "test_state"
        self.oauth_manager.auth_states[state] = {
            "provider_id": "google",
            "created_at": datetime.now().isoformat()
        }
        
        # Mock user info
        self.oauth_manager._get_user_info = MagicMock(return_value={
            "id": "user123",
            "email": "test@example.com",
            "name": "Test User"
        })
        
        # Handle auth callback
        result = self.oauth_manager.handle_auth_callback("test_code", state)
        
        # Verify result
        self.assertEqual(result.status, AuthStatus.SUCCESS)
        self.assertEqual(result.access_token, "new_access_token")
        self.assertEqual(result.refresh_token, "new_refresh_token")
        
        # Verify token request
        mock_post.assert_called_once_with(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": "google_client_id",
                "client_secret": "google_client_secret",
                "code": "test_code",
                "redirect_uri": "http://localhost:8080/callback",
                "grant_type": "authorization_code"
            }
        )
        
        # Verify credentials storage
        self.credential_storage.store_credentials.assert_called_once()
        args = self.credential_storage.store_credentials.call_args[0]
        self.assertEqual(args[0], "google")
        self.assertEqual(args[1], "test@example.com")
        self.assertEqual(args[2]["access_token"], "new_access_token")
        self.assertEqual(args[2]["refresh_token"], "new_refresh_token")
    
    def test_handle_auth_callback_invalid_state(self):
        """Test handling auth callback with invalid state."""
        with self.assertRaises(AuthError):
            self.oauth_manager.handle_auth_callback("test_code", "invalid_state")
    
    @patch('requests.post')
    def test_refresh_token(self, mock_post):
        """Test refreshing token."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        # Set up stored credentials
        self.credential_storage.retrieve_credentials.return_value = {
            "access_token": "old_access_token",
            "refresh_token": "old_refresh_token",
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "user_info": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Refresh token
        result = self.oauth_manager.refresh_token("google", "test@example.com")
        
        # Verify result
        self.assertEqual(result.status, AuthStatus.SUCCESS)
        self.assertEqual(result.access_token, "new_access_token")
        self.assertEqual(result.refresh_token, "old_refresh_token")  # No new refresh token in response
        
        # Verify token request
        mock_post.assert_called_once_with(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": "google_client_id",
                "client_secret": "google_client_secret",
                "refresh_token": "old_refresh_token",
                "grant_type": "refresh_token"
            }
        )
        
        # Verify credentials storage
        self.credential_storage.store_credentials.assert_called_once()
        args = self.credential_storage.store_credentials.call_args[0]
        self.assertEqual(args[0], "google")
        self.assertEqual(args[1], "test@example.com")
        self.assertEqual(args[2]["access_token"], "new_access_token")
        self.assertEqual(args[2]["refresh_token"], "old_refresh_token")
    
    def test_refresh_token_no_credentials(self):
        """Test refreshing token with no stored credentials."""
        # Set up no stored credentials
        self.credential_storage.retrieve_credentials.return_value = None
        
        # Refresh token
        result = self.oauth_manager.refresh_token("google", "test@example.com")
        
        # Verify result
        self.assertEqual(result.status, AuthStatus.FAILED)
        self.assertIn("No credentials found", result.error_message)
    
    def test_refresh_token_no_refresh_token(self):
        """Test refreshing token with no refresh token."""
        # Set up stored credentials without refresh token
        self.credential_storage.retrieve_credentials.return_value = {
            "access_token": "old_access_token",
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "user_info": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Refresh token
        result = self.oauth_manager.refresh_token("google", "test@example.com")
        
        # Verify result
        self.assertEqual(result.status, AuthStatus.FAILED)
        self.assertIn("No refresh token", result.error_message)
    
    def test_get_valid_token_valid(self):
        """Test getting valid token that doesn't need refresh."""
        # Set up stored credentials with valid token
        self.credential_storage.retrieve_credentials.return_value = {
            "access_token": "valid_access_token",
            "refresh_token": "refresh_token",
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "user_info": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Get valid token
        token = self.oauth_manager.get_valid_token("google", "test@example.com")
        
        # Verify token
        self.assertEqual(token, "valid_access_token")
    
    def test_get_valid_token_expired(self):
        """Test getting valid token that needs refresh."""
        # Set up stored credentials with expired token
        self.credential_storage.retrieve_credentials.return_value = {
            "access_token": "expired_access_token",
            "refresh_token": "refresh_token",
            "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "user_info": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Mock refresh_token method
        self.oauth_manager.refresh_token = MagicMock(return_value=MagicMock(
            is_success=True,
            access_token="new_access_token"
        ))
        
        # Get valid token
        token = self.oauth_manager.get_valid_token("google", "test@example.com")
        
        # Verify token
        self.assertEqual(token, "new_access_token")
        self.oauth_manager.refresh_token.assert_called_once_with("google", "test@example.com")
    
    def test_get_valid_token_no_credentials(self):
        """Test getting valid token with no stored credentials."""
        # Set up no stored credentials
        self.credential_storage.retrieve_credentials.return_value = None
        
        # Get valid token
        token = self.oauth_manager.get_valid_token("google", "test@example.com")
        
        # Verify token
        self.assertIsNone(token)
    
    def test_revoke_access(self):
        """Test revoking access."""
        # Set up stored credentials
        self.credential_storage.retrieve_credentials.return_value = {
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "expires_at": datetime.now().isoformat(),
            "user_info": {
                "id": "user123",
                "email": "test@example.com",
                "name": "Test User"
            }
        }
        
        # Mock _revoke_token method
        self.oauth_manager._revoke_token = MagicMock(return_value=True)
        
        # Revoke access
        result = self.oauth_manager.revoke_access("google", "test@example.com")
        
        # Verify result
        self.assertTrue(result)
        self.oauth_manager._revoke_token.assert_called_once_with("google", "access_token")
        self.credential_storage.delete_credentials.assert_called_once_with("google", "test@example.com")
    
    def test_revoke_access_no_credentials(self):
        """Test revoking access with no stored credentials."""
        # Set up no stored credentials
        self.credential_storage.retrieve_credentials.return_value = None
        
        # Revoke access
        result = self.oauth_manager.revoke_access("google", "test@example.com")
        
        # Verify result
        self.assertTrue(result)
        self.credential_storage.delete_credentials.assert_not_called()
    
    def test_list_connected_accounts(self):
        """Test listing connected accounts."""
        # Set up providers and users
        self.credential_storage.list_providers.return_value = ["google", "outlook"]
        self.credential_storage.list_users.side_effect = lambda provider: {
            "google": ["user1@example.com", "user2@example.com"],
            "outlook": ["user3@example.com"]
        }[provider]
        
        # Set up credentials
        self.credential_storage.retrieve_credentials.side_effect = lambda provider, user: {
            ("google", "user1@example.com"): {
                "user_info": {"email": "user1@example.com", "name": "User 1"}
            },
            ("google", "user2@example.com"): {
                "user_info": {"email": "user2@example.com", "name": "User 2"}
            },
            ("outlook", "user3@example.com"): {
                "user_info": {"email": "user3@example.com", "name": "User 3"}
            }
        }.get((provider, user))
        
        # List connected accounts
        accounts = self.oauth_manager.list_connected_accounts()
        
        # Verify accounts
        self.assertEqual(len(accounts["google"]), 2)
        self.assertEqual(accounts["google"][0]["email"], "user1@example.com")
        self.assertEqual(accounts["google"][1]["email"], "user2@example.com")
        self.assertEqual(len(accounts["outlook"]), 1)
        self.assertEqual(accounts["outlook"][0]["email"], "user3@example.com")


if __name__ == '__main__':
    unittest.main()
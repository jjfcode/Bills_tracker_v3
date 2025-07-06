import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

# Authentication configuration
AUTH_ENABLED = True  # Set to False to disable authentication
# You can also set this via environment variable: AUTH_ENABLED=false
if os.environ.get('AUTH_ENABLED', '').lower() == 'false':
    AUTH_ENABLED = False
SESSION_DURATION_HOURS = 24
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Database schema for users and sessions
USERS_SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP
);
'''

SESSIONS_SCHEMA = '''
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
'''

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class AuthManager:
    """Manages user authentication and sessions"""
    
    def __init__(self, db_file='bills_tracker.db'):
        self.db_file = db_file
        self.current_user = None
        self.current_session = None
        self._initialize_auth_tables()
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _initialize_auth_tables(self):
        """Initialize authentication tables"""
        if not AUTH_ENABLED:
            return
            
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(USERS_SCHEMA)
        cursor.execute(SESSIONS_SCHEMA)
        
        # Create default admin user if no users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self._create_default_admin()
        
        conn.commit()
        conn.close()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_username = "admin"
        admin_password = "admin123"  # Should be changed on first login
        admin_email = "admin@bills-tracker.local"
        
        self.register_user(
            username=admin_username,
            password=admin_password,
            email=admin_email,
            role="admin"
        )
        print(f"Default admin user created: {admin_username}/{admin_password}")
        print("IMPORTANT: Change the default password after first login!")
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for secure password hashing
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000  # 100k iterations
        )
        password_hash = hash_obj.hex()
        return password_hash, salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        password_hash, _ = self._hash_password(password, salt)
        return password_hash == stored_hash
    
    def register_user(self, username: str, password: str, email: str = None, role: str = "user") -> bool:
        """Register a new user"""
        if not AUTH_ENABLED:
            return True
            
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise AuthenticationError("Username already exists")
            
            # Check if email already exists (if provided)
            if email:
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    raise AuthenticationError("Email already exists")
            
            # Hash password
            password_hash, salt = self._hash_password(password)
            
            # Insert user
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, role))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            if conn:
                conn.close()
            raise AuthenticationError(f"Registration failed: {str(e)}")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and create session"""
        if not AUTH_ENABLED:
            # Return mock user data when auth is disabled
            return {
                'user_id': 1,
                'username': 'guest',
                'email': None,
                'role': 'user',
                'session_token': 'no-auth'
            }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get user data
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, role, is_active,
                       failed_login_attempts, locked_until
                FROM users WHERE username = ?
            ''', (username,))
            
            user_row = cursor.fetchone()
            if not user_row:
                raise AuthenticationError("Invalid username or password")
            
            user_data = dict(user_row)
            
            # Check if account is active
            if not user_data['is_active']:
                raise AuthenticationError("Account is deactivated")
            
            # Check if account is locked
            if user_data['locked_until']:
                locked_until = datetime.fromisoformat(user_data['locked_until'])
                if datetime.now() < locked_until:
                    remaining = locked_until - datetime.now()
                    raise AuthenticationError(f"Account is locked. Try again in {int(remaining.total_seconds() / 60)} minutes")
                else:
                    # Unlock account
                    cursor.execute('''
                        UPDATE users SET failed_login_attempts = 0, locked_until = NULL
                        WHERE id = ?
                    ''', (user_data['id'],))
            
            # Verify password
            if not self._verify_password(password, user_data['password_hash'], user_data['salt']):
                # Increment failed login attempts
                failed_attempts = user_data['failed_login_attempts'] + 1
                cursor.execute('''
                    UPDATE users SET failed_login_attempts = ?
                    WHERE id = ?
                ''', (failed_attempts, user_data['id']))
                
                # Lock account if too many failed attempts
                if failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    locked_until = datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    cursor.execute('''
                        UPDATE users SET locked_until = ?
                        WHERE id = ?
                    ''', (locked_until.isoformat(), user_data['id']))
                    conn.commit()
                    conn.close()
                    raise AuthenticationError(f"Too many failed attempts. Account locked for {LOCKOUT_DURATION_MINUTES} minutes")
                
                conn.commit()
                conn.close()
                raise AuthenticationError("Invalid username or password")
            
            # Reset failed login attempts and update last login
            cursor.execute('''
                UPDATE users SET failed_login_attempts = 0, last_login = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), user_data['id']))
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=SESSION_DURATION_HOURS)
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_data['id'], session_token, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            return {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data['role'],
                'session_token': session_token
            }
            
        except Exception as e:
            if conn:
                conn.close()
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token and return user data"""
        if not AUTH_ENABLED:
            return {
                'user_id': 1,
                'username': 'guest',
                'email': None,
                'role': 'user'
            }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get session and user data
            cursor.execute('''
                SELECT s.user_id, s.expires_at, u.username, u.email, u.role, u.is_active
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ?
            ''', (session_token,))
            
            session_row = cursor.fetchone()
            if not session_row:
                conn.close()
                return None
            
            session_data = dict(session_row)
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                # Delete expired session
                cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
                conn.commit()
                conn.close()
                return None
            
            # Check if user is still active
            if not session_data['is_active']:
                # Delete session for inactive user
                cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
                conn.commit()
                conn.close()
                return None
            
            conn.close()
            
            return {
                'user_id': session_data['user_id'],
                'username': session_data['username'],
                'email': session_data['email'],
                'role': session_data['role']
            }
            
        except Exception as e:
            if conn:
                conn.close()
            return None
    
    def logout(self, session_token: str) -> bool:
        """Logout user by deleting session"""
        if not AUTH_ENABLED:
            return True
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        if not AUTH_ENABLED:
            return True
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get current password hash
            cursor.execute("SELECT password_hash, salt FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            if not user_row:
                raise AuthenticationError("User not found")
            
            # Verify current password
            if not self._verify_password(current_password, user_row['password_hash'], user_row['salt']):
                raise AuthenticationError("Current password is incorrect")
            
            # Hash new password
            new_password_hash, new_salt = self._hash_password(new_password)
            
            # Update password
            cursor.execute('''
                UPDATE users SET password_hash = ?, salt = ?
                WHERE id = ?
            ''', (new_password_hash, new_salt, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            if conn:
                conn.close()
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Password change failed: {str(e)}")
    
    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        if not AUTH_ENABLED:
            return {
                'id': 1,
                'username': 'guest',
                'email': None,
                'role': 'user',
                'created_at': datetime.now().isoformat()
            }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, role, created_at, last_login
                FROM users WHERE id = ?
            ''', (user_id,))
            
            user_row = cursor.fetchone()
            conn.close()
            
            if user_row:
                return dict(user_row)
            return None
            
        except Exception:
            return None
    
    def is_admin(self, user_data: Optional[Dict[str, Any]]) -> bool:
        """Check if user has admin role"""
        if not AUTH_ENABLED:
            return True
        return user_data and user_data.get('role') == 'admin'
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions from database"""
        if not AUTH_ENABLED:
            return
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now().isoformat(),))
            conn.commit()
            conn.close()
        except Exception:
            pass

# Global auth manager instance
auth_manager = AuthManager() 
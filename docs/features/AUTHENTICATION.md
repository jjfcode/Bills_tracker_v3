# User Authentication

The Bills Tracker v3 application includes optional user authentication to secure your bill data and provide multi-user support.

## Features

- **User Registration**: Create new user accounts
- **Secure Login**: Password-based authentication with session management
- **Password Management**: Change passwords securely
- **Session Management**: Automatic session expiration and cleanup
- **Account Lockout**: Protection against brute force attacks
- **Role-Based Access**: Admin and user roles
- **Optional Authentication**: Can be disabled for single-user setups

## Default Credentials

When you first run the application with authentication enabled, a default admin user is created:

- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Important**: Change the default password immediately after first login!

## Configuration

### Enable/Disable Authentication

Authentication is enabled by default. To disable it:

1. **Environment Variable** (recommended):
   ```bash
   export AUTH_ENABLED=false
   python main_desktop.py
   ```

2. **Code Configuration**:
   Edit `src/core/auth.py` and set:
   ```python
   AUTH_ENABLED = False
   ```

### Authentication Settings

You can customize authentication behavior in `src/core/auth.py`:

```python
SESSION_DURATION_HOURS = 24        # How long sessions last
MAX_LOGIN_ATTEMPTS = 5             # Failed attempts before lockout
LOCKOUT_DURATION_MINUTES = 30      # How long accounts are locked
```

## User Roles

### User Role
- Can view and manage bills
- Can manage categories
- Can change their own password
- Cannot manage other users

### Admin Role
- All user permissions
- Can create new users
- Can manage all users
- Can access admin settings

## Security Features

### Password Security
- Passwords are hashed using PBKDF2 with SHA-256
- 100,000 iterations for strong security
- Unique salt for each password
- Minimum 6 characters required

### Session Security
- Secure random session tokens
- Automatic session expiration
- Session cleanup on logout
- Protection against session hijacking

### Account Protection
- Failed login attempt tracking
- Automatic account lockout
- Account deactivation support
- Secure password change process

## Database Schema

The authentication system adds two tables to the database:

### Users Table
```sql
CREATE TABLE users (
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
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Usage

### First Time Setup
1. Run the application
2. Login with default admin credentials
3. Change the admin password
4. Create additional users as needed

### Daily Usage
1. Login with your credentials
2. Use the application normally
3. Logout when finished
4. Sessions automatically expire after 24 hours

### Admin Functions
- **Create Users**: Go to Settings → User Management → Create New User
- **Change Password**: Click "Change Password" in the sidebar
- **Logout**: Click "Logout" in the sidebar

## Troubleshooting

### Can't Login
- Check username and password
- Account may be locked due to failed attempts
- Wait for lockout period to expire
- Contact admin if account is deactivated

### Authentication Disabled
- Set `AUTH_ENABLED = False` in `src/core/auth.py`
- Or set environment variable `AUTH_ENABLED=false`
- Application will run without login requirement

### Database Issues
- Delete `bills_tracker.db` to reset database
- Default admin user will be recreated
- All data will be lost

## Security Best Practices

1. **Change Default Password**: Always change the default admin password
2. **Strong Passwords**: Use strong, unique passwords
3. **Regular Updates**: Keep the application updated
4. **Secure Environment**: Run on a secure, private machine
5. **Backup Data**: Regularly backup your database file
6. **Logout**: Always logout when finished
7. **Session Management**: Be aware of session timeouts

## API Reference

### AuthManager Class

```python
from src.core.auth import auth_manager

# Login
user_data = auth_manager.login(username, password)

# Register
auth_manager.register_user(username, password, email, role)

# Validate session
user_data = auth_manager.validate_session(session_token)

# Logout
auth_manager.logout(session_token)

# Change password
auth_manager.change_password(user_id, current_password, new_password)

# Check if admin
is_admin = auth_manager.is_admin(user_data)
```

### AuthenticationError Exception

```python
from src.core.auth import AuthenticationError

try:
    auth_manager.login(username, password)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
``` 
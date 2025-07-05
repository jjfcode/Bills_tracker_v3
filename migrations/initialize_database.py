#!/usr/bin/env python3
"""
Database Initialization Script
Creates all necessary tables for the Bills Tracker application
"""

import sqlite3
import os
import sys
import hashlib
import secrets
from datetime import datetime

# Add src to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.core.db import (
    CATEGORIES_SCHEMA, PAYMENT_METHODS_SCHEMA, BILLS_SCHEMA, TEMPLATES_SCHEMA,
    get_db_connection
)

# Authentication tables schema
USERS_SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
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

def hash_password(password, salt=None):
    """Hash a password with salt using SHA-256"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt
    salted_password = password + salt
    
    # Hash using SHA-256
    password_hash = hashlib.sha256(salted_password.encode()).hexdigest()
    
    return password_hash, salt

def initialize_database():
    """Initialize the database with all required tables"""
    print("Initializing Bills Tracker database...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create all tables
    print("Creating tables...")
    cursor.execute(CATEGORIES_SCHEMA)
    cursor.execute(PAYMENT_METHODS_SCHEMA)
    cursor.execute(BILLS_SCHEMA)
    cursor.execute(TEMPLATES_SCHEMA)
    cursor.execute(USERS_SCHEMA)
    cursor.execute(SESSIONS_SCHEMA)
    
    # Insert default categories
    print("Adding default categories...")
    default_categories = [
        ("Utilities", "#ff6b6b", "Electricity, water, gas, internet"),
        ("Housing", "#4ecdc4", "Rent, mortgage, property taxes"),
        ("Transportation", "#45b7d1", "Car payment, insurance, fuel"),
        ("Insurance", "#96ceb4", "Health, life, auto insurance"),
        ("Entertainment", "#feca57", "Streaming, games, hobbies"),
        ("Food & Dining", "#ff9ff3", "Groceries, restaurants"),
        ("Healthcare", "#54a0ff", "Medical bills, prescriptions"),
        ("Education", "#5f27cd", "Tuition, books, courses"),
        ("Shopping", "#00d2d3", "Clothing, electronics, general"),
        ("Other", "#c8d6e5", "Miscellaneous expenses")
    ]
    
    for name, color, description in default_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, color, description) 
            VALUES (?, ?, ?)
        ''', (name, color, description))
    
    # Insert default payment methods
    print("Adding default payment methods...")
    default_payment_methods = [
        ("Auto-Pay", "Automatic payment from bank account", 1),
        ("Manual Bank Transfer", "Manual bank transfer or online payment", 0),
        ("Credit Card", "Payment via credit card", 0),
        ("Check", "Payment by check", 0),
        ("Cash", "Cash payment", 0),
        ("Digital Wallet", "Apple Pay, Google Pay, etc.", 0),
        ("Direct Debit", "Direct debit from account", 1),
        ("Other", "Other payment methods", 0)
    ]
    
    for name, description, is_automatic in default_payment_methods:
        cursor.execute('''
            INSERT OR IGNORE INTO payment_methods (name, description, is_automatic) 
            VALUES (?, ?, ?)
        ''', (name, description, is_automatic))
    
    # Create default admin user
    print("Creating default admin user...")
    admin_username = "admin"
    admin_email = "admin@billstracker.com"
    admin_password = "admin123"
    
    # Check if admin user already exists
    cursor.execute('SELECT id FROM users WHERE username = ?', (admin_username,))
    if not cursor.fetchone():
        password_hash, salt = hash_password(admin_password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, salt, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (admin_username, admin_email, password_hash, salt, 1))
        print(f"Created admin user: {admin_username} / {admin_password}")
    else:
        print("Admin user already exists")
    
    conn.commit()
    conn.close()
    
    print("Database initialization completed successfully!")
    print("\nDefault credentials:")
    print(f"Username: {admin_username}")
    print(f"Password: {admin_password}")
    print("\nYou can now run the application with: python main_desktop.py")

if __name__ == "__main__":
    initialize_database() 
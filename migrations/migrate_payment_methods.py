#!/usr/bin/env python3
"""
Migration script to add payment_methods table and update bills table.
This script adds the payment_methods table and updates the bills table to reference payment methods.
"""

import sqlite3
import os

def migrate_payment_methods():
    """Add payment_methods table and update bills table"""
    db_file = '../bills_tracker.db'
    
    if not os.path.exists(db_file):
        print(f"Database file '{db_file}' not found. Creating new database...")
        return
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create payment_methods table
        print("Creating payment_methods table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                is_automatic INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default payment methods
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
        
        # Check if payment_method_id column exists in bills table
        cursor.execute("PRAGMA table_info(bills)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'payment_method_id' not in columns:
            print("Adding payment_method_id column to bills table...")
            cursor.execute("ALTER TABLE bills ADD COLUMN payment_method_id INTEGER")
            cursor.execute("ALTER TABLE bills ADD COLUMN FOREIGN KEY (payment_method_id) REFERENCES payment_methods (id)")
        
        conn.commit()
        print("✓ Payment methods migration completed successfully!")
        
        # Verify the changes
        cursor.execute("SELECT name FROM payment_methods")
        payment_methods = cursor.fetchall()
        print(f"✓ Created {len(payment_methods)} payment methods")
        
        conn.close()
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Bills Tracker v3 - Payment Methods Migration")
    print("=" * 50)
    migrate_payment_methods()
    print("=" * 50)
    print("Migration script completed.") 
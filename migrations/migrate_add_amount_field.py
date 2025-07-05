import sqlite3
import os
import sys

# Add the src directory to the path so we can import from core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from db import get_db_connection

def migrate_add_amount_field():
    """
    Migration to add amount field to bills table.
    This field will store the bill amount for better reminder notifications.
    """
    print("Starting migration: Add amount field to bills table...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if amount column already exists
        cursor.execute("PRAGMA table_info(bills)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'amount' not in columns:
            print("Adding amount column to bills table...")
            
            # Add amount column
            cursor.execute('''
                ALTER TABLE bills 
                ADD COLUMN amount REAL DEFAULT NULL
            ''')
            
            # Add amount column to templates table as well
            cursor.execute("PRAGMA table_info(templates)")
            template_columns = [column[1] for column in cursor.fetchall()]
            
            if 'amount' not in template_columns:
                cursor.execute('''
                    ALTER TABLE templates 
                    ADD COLUMN amount REAL DEFAULT NULL
                ''')
            
            conn.commit()
            print("✅ Successfully added amount field to bills and templates tables")
        else:
            print("✅ Amount field already exists in bills table")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_add_amount_field() 
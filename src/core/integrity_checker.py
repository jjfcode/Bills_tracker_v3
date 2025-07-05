#!/usr/bin/env python3
"""
Data Integrity Checker for Bills Tracker application.
Verifies data consistency on startup and provides repair capabilities.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from validation import DataValidator

class DataIntegrityChecker:
    """Comprehensive data integrity checker for Bills Tracker."""
    
    def __init__(self, db_file: str = 'bills_tracker.db'):
        self.db_file = db_file
        self.issues = []
        self.repairs_made = []
        self.stats = {
            'bills_checked': 0,
            'templates_checked': 0,
            'issues_found': 0,
            'repairs_made': 0
        }
    
    def check_database_integrity(self) -> Tuple[bool, List[str]]:
        """
        Perform comprehensive database integrity check.
        
        Returns:
            Tuple of (is_healthy, list_of_issues)
        """
        self.issues = []
        self.repairs_made = []
        self.stats = {
            'bills_checked': 0,
            'templates_checked': 0,
            'issues_found': 0,
            'repairs_made': 0
        }
        
        # Check if database file exists
        if not os.path.exists(self.db_file):
            self.issues.append(f"Database file '{self.db_file}' not found")
            return False, self.issues
        
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Check database structure
            self._check_database_structure(cursor)
            
            # Check bills table integrity
            self._check_bills_integrity(cursor)
            
            # Check templates table integrity
            self._check_templates_integrity(cursor)
            
            # Check for orphaned data
            self._check_orphaned_data(cursor)
            
            # Check for data consistency
            self._check_data_consistency(cursor)
            
            conn.close()
            
        except sqlite3.Error as e:
            self.issues.append(f"Database error: {str(e)}")
        except Exception as e:
            self.issues.append(f"Unexpected error: {str(e)}")
        
        return len(self.issues) == 0, self.issues
    
    def _check_database_structure(self, cursor: sqlite3.Cursor):
        """Check database schema and table structure."""
        try:
            # Check if required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['bills', 'templates']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                self.issues.append(f"Missing required tables: {', '.join(missing_tables)}")
                return
            
            # Check bills table structure
            cursor.execute("PRAGMA table_info(bills)")
            bills_columns = {row[1] for row in cursor.fetchall()}
            required_bills_columns = {
                'id', 'name', 'due_date', 'billing_cycle', 'reminder_days',
                'web_page', 'login_info', 'password', 'paid', 'company_email',
                'support_phone', 'billing_phone', 'customer_service_hours',
                'account_number', 'reference_id', 'support_chat_url', 'mobile_app'
            }
            
            missing_bills_columns = required_bills_columns - bills_columns
            if missing_bills_columns:
                self.issues.append(f"Missing columns in bills table: {', '.join(missing_bills_columns)}")
            
            # Check templates table structure
            cursor.execute("PRAGMA table_info(templates)")
            templates_columns = {row[1] for row in cursor.fetchall()}
            required_templates_columns = {
                'id', 'name', 'due_date', 'billing_cycle', 'reminder_days',
                'web_page', 'login_info', 'password', 'company_email',
                'support_phone', 'billing_phone', 'customer_service_hours',
                'account_number', 'reference_id', 'support_chat_url', 'mobile_app'
            }
            
            missing_templates_columns = required_templates_columns - templates_columns
            if missing_templates_columns:
                self.issues.append(f"Missing columns in templates table: {', '.join(missing_templates_columns)}")
                
        except sqlite3.Error as e:
            self.issues.append(f"Error checking database structure: {str(e)}")
    
    def _check_bills_integrity(self, cursor: sqlite3.Cursor):
        """Check bills table data integrity."""
        try:
            cursor.execute("SELECT COUNT(*) FROM bills")
            total_bills = cursor.fetchone()[0]
            self.stats['bills_checked'] = total_bills
            
            if total_bills == 0:
                return
            
            # Check each bill for data integrity
            cursor.execute("SELECT * FROM bills")
            bills = cursor.fetchall()
            
            for i, bill in enumerate(bills):
                bill_dict = dict(zip([col[0] for col in cursor.description], bill))
                self._validate_bill_data(bill_dict, i + 1)
                
        except sqlite3.Error as e:
            self.issues.append(f"Error checking bills integrity: {str(e)}")
    
    def _check_templates_integrity(self, cursor: sqlite3.Cursor):
        """Check templates table data integrity."""
        try:
            cursor.execute("SELECT COUNT(*) FROM templates")
            total_templates = cursor.fetchone()[0]
            self.stats['templates_checked'] = total_templates
            
            if total_templates == 0:
                return
            
            # Check each template for data integrity
            cursor.execute("SELECT * FROM templates")
            templates = cursor.fetchall()
            
            for i, template in enumerate(templates):
                template_dict = dict(zip([col[0] for col in cursor.description], template))
                self._validate_template_data(template_dict, i + 1)
                
        except sqlite3.Error as e:
            self.issues.append(f"Error checking templates integrity: {str(e)}")
    
    def _validate_bill_data(self, bill: Dict[str, Any], row_num: int):
        """Validate individual bill data."""
        # Check required fields
        if not bill.get('name'):
            self.issues.append(f"Bill {row_num}: Missing required field 'name'")
            self.stats['issues_found'] += 1
        
        if not bill.get('due_date'):
            self.issues.append(f"Bill {row_num}: Missing required field 'due_date'")
            self.stats['issues_found'] += 1
        
        # Validate bill name
        if bill.get('name'):
            is_valid, error_msg = DataValidator.validate_bill_name(bill['name'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid name - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate due date
        if bill.get('due_date'):
            is_valid, error_msg = DataValidator.validate_due_date(bill['due_date'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid due date - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate billing cycle
        if bill.get('billing_cycle'):
            is_valid, error_msg = DataValidator.validate_billing_cycle(bill['billing_cycle'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid billing cycle - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate reminder days
        if bill.get('reminder_days') is not None:
            is_valid, error_msg = DataValidator.validate_reminder_days(bill['reminder_days'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid reminder days - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate URLs
        if bill.get('web_page'):
            is_valid, error_msg, _ = DataValidator.validate_url(bill['web_page'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid web page URL - {error_msg}")
                self.stats['issues_found'] += 1
        
        if bill.get('support_chat_url'):
            is_valid, error_msg, _ = DataValidator.validate_url(bill['support_chat_url'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid support chat URL - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate email
        if bill.get('company_email'):
            is_valid, error_msg = DataValidator.validate_email(bill['company_email'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid company email - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate phone numbers
        if bill.get('support_phone'):
            is_valid, error_msg = DataValidator.validate_phone(bill['support_phone'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid support phone - {error_msg}")
                self.stats['issues_found'] += 1
        
        if bill.get('billing_phone'):
            is_valid, error_msg = DataValidator.validate_phone(bill['billing_phone'])
            if not is_valid:
                self.issues.append(f"Bill {row_num}: Invalid billing phone - {error_msg}")
                self.stats['issues_found'] += 1
    
    def _validate_template_data(self, template: Dict[str, Any], row_num: int):
        """Validate individual template data."""
        # Check required fields
        if not template.get('name'):
            self.issues.append(f"Template {row_num}: Missing required field 'name'")
            self.stats['issues_found'] += 1
        
        # Validate template name
        if template.get('name'):
            is_valid, error_msg = DataValidator.validate_bill_name(template['name'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid name - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate billing cycle
        if template.get('billing_cycle'):
            is_valid, error_msg = DataValidator.validate_billing_cycle(template['billing_cycle'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid billing cycle - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate reminder days
        if template.get('reminder_days') is not None:
            is_valid, error_msg = DataValidator.validate_reminder_days(template['reminder_days'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid reminder days - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate URLs
        if template.get('web_page'):
            is_valid, error_msg, _ = DataValidator.validate_url(template['web_page'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid web page URL - {error_msg}")
                self.stats['issues_found'] += 1
        
        if template.get('support_chat_url'):
            is_valid, error_msg, _ = DataValidator.validate_url(template['support_chat_url'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid support chat URL - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate email
        if template.get('company_email'):
            is_valid, error_msg = DataValidator.validate_email(template['company_email'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid company email - {error_msg}")
                self.stats['issues_found'] += 1
        
        # Validate phone numbers
        if template.get('support_phone'):
            is_valid, error_msg = DataValidator.validate_phone(template['support_phone'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid support phone - {error_msg}")
                self.stats['issues_found'] += 1
        
        if template.get('billing_phone'):
            is_valid, error_msg = DataValidator.validate_phone(template['billing_phone'])
            if not is_valid:
                self.issues.append(f"Template {row_num}: Invalid billing phone - {error_msg}")
                self.stats['issues_found'] += 1
    
    def _check_orphaned_data(self, cursor: sqlite3.Cursor):
        """Check for orphaned or inconsistent data."""
        try:
            # Check for bills with invalid billing cycles
            cursor.execute("""
                SELECT id, name, billing_cycle FROM bills 
                WHERE billing_cycle NOT IN ('weekly', 'bi-weekly', 'monthly', 'quarterly', 'semi-annually', 'annually', 'one-time')
            """)
            invalid_cycles = cursor.fetchall()
            
            for bill_id, name, cycle in invalid_cycles:
                self.issues.append(f"Bill '{name}' (ID: {bill_id}): Invalid billing cycle '{cycle}'")
                self.stats['issues_found'] += 1
            
            # Check for bills with invalid reminder days
            cursor.execute("""
                SELECT id, name, reminder_days FROM bills 
                WHERE reminder_days < 1 OR reminder_days > 365
            """)
            invalid_reminders = cursor.fetchall()
            
            for bill_id, name, days in invalid_reminders:
                self.issues.append(f"Bill '{name}' (ID: {bill_id}): Invalid reminder days {days} (must be 1-365)")
                self.stats['issues_found'] += 1
            
            # Check for bills with invalid due dates
            cursor.execute("""
                SELECT id, name, due_date FROM bills 
                WHERE due_date IS NULL OR due_date = ''
            """)
            invalid_dates = cursor.fetchall()
            
            for bill_id, name, due_date in invalid_dates:
                self.issues.append(f"Bill '{name}' (ID: {bill_id}): Missing or invalid due date")
                self.stats['issues_found'] += 1
            
            # Check for duplicate bill names
            cursor.execute("""
                SELECT name, COUNT(*) as count FROM bills 
                GROUP BY LOWER(name) 
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            
            for name, count in duplicates:
                self.issues.append(f"Duplicate bill names found: '{name}' appears {count} times")
                self.stats['issues_found'] += 1
                
        except sqlite3.Error as e:
            self.issues.append(f"Error checking orphaned data: {str(e)}")
    
    def _check_data_consistency(self, cursor: sqlite3.Cursor):
        """Check for data consistency issues."""
        try:
            # Check for bills with future due dates that are marked as paid
            cursor.execute("""
                SELECT id, name, due_date, paid FROM bills 
                WHERE paid = 1 AND due_date > date('now')
            """)
            future_paid_bills = cursor.fetchall()
            
            for bill_id, name, due_date, paid in future_paid_bills:
                self.issues.append(f"Bill '{name}' (ID: {bill_id}): Marked as paid but due date is in the future ({due_date})")
                self.stats['issues_found'] += 1
            
            # Check for bills with very old due dates
            cursor.execute("""
                SELECT id, name, due_date FROM bills 
                WHERE due_date < date('now', '-2 years')
            """)
            old_bills = cursor.fetchall()
            
            for bill_id, name, due_date in old_bills:
                self.issues.append(f"Bill '{name}' (ID: {bill_id}): Very old due date ({due_date}) - consider updating or removing")
                self.stats['issues_found'] += 1
                
        except sqlite3.Error as e:
            self.issues.append(f"Error checking data consistency: {str(e)}")
    
    def repair_issues(self, auto_repair: bool = False) -> List[str]:
        """
        Attempt to repair identified issues.
        
        Args:
            auto_repair: If True, automatically repair issues without confirmation
            
        Returns:
            List of repair actions taken
        """
        if not self.issues:
            return []
        
        repairs = []
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Repair invalid billing cycles
            cursor.execute("""
                UPDATE bills 
                SET billing_cycle = 'monthly' 
                WHERE billing_cycle NOT IN ('weekly', 'bi-weekly', 'monthly', 'quarterly', 'semi-annually', 'annually', 'one-time')
            """)
            if cursor.rowcount > 0:
                repairs.append(f"Fixed {cursor.rowcount} invalid billing cycles")
            
            # Repair invalid reminder days
            cursor.execute("""
                UPDATE bills 
                SET reminder_days = 7 
                WHERE reminder_days < 1 OR reminder_days > 365
            """)
            if cursor.rowcount > 0:
                repairs.append(f"Fixed {cursor.rowcount} invalid reminder days")
            
            # Repair templates with invalid billing cycles
            cursor.execute("""
                UPDATE templates 
                SET billing_cycle = 'monthly' 
                WHERE billing_cycle NOT IN ('weekly', 'bi-weekly', 'monthly', 'quarterly', 'semi-annually', 'annually', 'one-time')
            """)
            if cursor.rowcount > 0:
                repairs.append(f"Fixed {cursor.rowcount} invalid template billing cycles")
            
            # Repair templates with invalid reminder days
            cursor.execute("""
                UPDATE templates 
                SET reminder_days = 7 
                WHERE reminder_days < 1 OR reminder_days > 365
            """)
            if cursor.rowcount > 0:
                repairs.append(f"Fixed {cursor.rowcount} invalid template reminder days")
            
            conn.commit()
            conn.close()
            
            self.repairs_made = repairs
            self.stats['repairs_made'] = len(repairs)
            
        except sqlite3.Error as e:
            repairs.append(f"Error during repair: {str(e)}")
        
        return repairs
    
    def get_integrity_report(self) -> Dict[str, Any]:
        """Generate a comprehensive integrity report."""
        return {
            'database_file': self.db_file,
            'check_timestamp': datetime.now().isoformat(),
            'is_healthy': len(self.issues) == 0,
            'total_issues': len(self.issues),
            'total_repairs': len(self.repairs_made),
            'stats': self.stats,
            'issues': self.issues,
            'repairs': self.repairs_made
        }
    
    def print_report(self):
        """Print a formatted integrity report."""
        report = self.get_integrity_report()
        
        print("🔍 Data Integrity Report")
        print("=" * 50)
        print(f"Database: {report['database_file']}")
        print(f"Check Time: {report['check_timestamp']}")
        print(f"Status: {'✅ Healthy' if report['is_healthy'] else '❌ Issues Found'}")
        print()
        
        print("📊 Statistics:")
        print(f"  Bills checked: {report['stats']['bills_checked']}")
        print(f"  Templates checked: {report['stats']['templates_checked']}")
        print(f"  Issues found: {report['stats']['issues_found']}")
        print(f"  Repairs made: {report['stats']['repairs_made']}")
        print()
        
        if report['issues']:
            print("❌ Issues Found:")
            for i, issue in enumerate(report['issues'], 1):
                print(f"  {i}. {issue}")
            print()
        
        if report['repairs']:
            print("🔧 Repairs Made:")
            for i, repair in enumerate(report['repairs'], 1):
                print(f"  {i}. {repair}")
            print()
        
        if report['is_healthy']:
            print("🎉 Database integrity check passed successfully!")
        else:
            print("⚠️  Database has integrity issues that should be addressed.")

def run_integrity_check(db_file: str = 'bills_tracker.db', auto_repair: bool = False) -> bool:
    """
    Run a complete integrity check on the database.
    
    Args:
        db_file: Path to the database file
        auto_repair: Whether to automatically repair issues
        
    Returns:
        True if database is healthy, False otherwise
    """
    checker = DataIntegrityChecker(db_file)
    
    # Run integrity check
    is_healthy, issues = checker.check_database_integrity()
    
    # Print report
    checker.print_report()
    
    # Attempt repairs if needed
    if not is_healthy and auto_repair:
        print("\n🔧 Attempting automatic repairs...")
        repairs = checker.repair_issues(auto_repair=True)
        
        if repairs:
            print("Repairs completed. Running integrity check again...")
            is_healthy, issues = checker.check_database_integrity()
            checker.print_report()
    
    return is_healthy

if __name__ == "__main__":
    # Run integrity check when script is executed directly
    run_integrity_check() 
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReminderService:
    """
    Service for managing bill reminders and notifications.
    Runs in a background thread to check for due bills and trigger notifications.
    """
    
    def __init__(self, db_file: str = 'bills_tracker.db', check_interval: int = 300):
        """
        Initialize the reminder service.
        
        Args:
            db_file: Path to the database file
            check_interval: How often to check for reminders (in seconds, default 5 minutes)
        """
        self.db_file = db_file
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.notification_callback: Optional[Callable] = None
        self.last_check_time = None
        self.sent_reminders = set()  # Track sent reminders to avoid duplicates
        
    def start(self, notification_callback: Optional[Callable] = None):
        """
        Start the reminder service in a background thread.
        
        Args:
            notification_callback: Function to call when a reminder should be shown
        """
        if self.running:
            logger.warning("Reminder service is already running")
            return
            
        self.notification_callback = notification_callback
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Reminder service started")
        
    def stop(self):
        """Stop the reminder service."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        logger.info("Reminder service stopped")
        
    def _run(self):
        """Main loop for the reminder service."""
        while self.running:
            try:
                self._check_reminders()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in reminder service: {e}")
                time.sleep(60)  # Wait a minute before retrying
            except KeyboardInterrupt:
                logger.info("Reminder service interrupted")
                break
                
    def _check_reminders(self):
        """Check for bills that need reminders and trigger notifications."""
        try:
            due_bills = self._get_due_bills()
            self.last_check_time = datetime.now()
            
            for bill in due_bills:
                reminder_key = f"{bill['id']}_{bill['due_date']}"
                if reminder_key not in self.sent_reminders:
                    self._trigger_reminder(bill)
                    self.sent_reminders.add(reminder_key)
                    
            # Clean up old sent reminders (older than 30 days)
            self._cleanup_old_reminders()
            
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
            
    def _get_due_bills(self) -> List[Dict]:
        """
        Get bills that are due within their reminder period.
        
        Returns:
            List of bill dictionaries that need reminders
        """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get current date
            today = datetime.now().date()
            
            # Query for bills that are due within their reminder period
            cursor.execute('''
                SELECT b.*, c.name as category_name, c.color as category_color,
                       p.name as payment_method_name
                FROM bills b 
                LEFT JOIN categories c ON b.category_id = c.id 
                LEFT JOIN payment_methods p ON b.payment_method_id = p.id
                WHERE b.paid = 0 
                AND b.due_date IS NOT NULL 
                AND b.reminder_days IS NOT NULL
                AND date(b.due_date) <= date(?, '+' || b.reminder_days || ' days')
                AND date(b.due_date) >= date(?)
                ORDER BY b.due_date
            ''', (today.isoformat(), today.isoformat()))
            
            rows = cursor.fetchall()
            bills = []
            for row in rows:
                bill = dict(row)
                bill['paid'] = bool(bill.get('paid', 0))
                if not bill.get('category_name'):
                    bill['category_name'] = 'Uncategorized'
                if not bill.get('payment_method_name'):
                    bill['payment_method_name'] = 'Not Set'
                bills.append(bill)
                
            return bills
            
        finally:
            conn.close()
            
    def _trigger_reminder(self, bill: Dict):
        """
        Trigger a reminder for a specific bill.
        
        Args:
            bill: Bill dictionary containing reminder information
        """
        try:
            # Calculate days until due
            due_date = datetime.strptime(bill['due_date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            days_until_due = (due_date - today).days
            
            # Create reminder message
            if days_until_due == 0:
                urgency = "URGENT"
                message = f"⚠️ {bill['name']} is due TODAY!"
            elif days_until_due < 0:
                urgency = "OVERDUE"
                message = f"🚨 {bill['name']} is OVERDUE by {abs(days_until_due)} days!"
            else:
                urgency = "REMINDER"
                message = f"📅 {bill['name']} is due in {days_until_due} days"
                
            # Add additional details
            details = f"Amount: ${bill.get('amount', 'N/A')}\n"
            details += f"Category: {bill.get('category_name', 'Uncategorized')}\n"
            details += f"Payment Method: {bill.get('payment_method_name', 'Not Set')}\n"
            
            if bill.get('web_page'):
                details += f"Website: {bill['web_page']}\n"
            if bill.get('company_email'):
                details += f"Email: {bill['company_email']}\n"
            if bill.get('support_phone'):
                details += f"Phone: {bill['support_phone']}\n"
                
            # Create notification data
            notification_data = {
                'title': f"Bill {urgency}",
                'message': message,
                'details': details,
                'bill_id': bill['id'],
                'bill_name': bill['name'],
                'due_date': bill['due_date'],
                'urgency': urgency,
                'days_until_due': days_until_due,
                'web_page': bill.get('web_page'),
                'company_email': bill.get('company_email'),
                'support_phone': bill.get('support_phone')
            }
            
            # Trigger notification callback if available
            if self.notification_callback:
                try:
                    self.notification_callback(notification_data)
                except Exception as callback_error:
                    logger.error(f"Error in notification callback: {callback_error}")
                    # Fallback to logging
                    logger.info(f"Reminder: {message}")
            else:
                logger.info(f"Reminder: {message}")
                
        except Exception as e:
            logger.error(f"Error triggering reminder for bill {bill.get('id')}: {e}")
            
    def _cleanup_old_reminders(self):
        """Clean up old sent reminders to prevent memory bloat."""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            cutoff_str = cutoff_date.strftime('%Y-%m-%d')
            
            # Remove reminders older than 30 days
            old_reminders = set()
            for reminder in self.sent_reminders:
                try:
                    bill_id, due_date = reminder.split('_', 1)
                    if due_date < cutoff_str:
                        old_reminders.add(reminder)
                except:
                    # Invalid reminder format, remove it
                    old_reminders.add(reminder)
                    
            self.sent_reminders -= old_reminders
            
        except Exception as e:
            logger.error(f"Error cleaning up old reminders: {e}")
            
    def get_upcoming_reminders(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get reminders for bills due in the next N days.
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming reminders
        """
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            today = datetime.now().date()
            future_date = today + timedelta(days=days_ahead)
            
            cursor.execute('''
                SELECT b.*, c.name as category_name, c.color as category_color,
                       p.name as payment_method_name
                FROM bills b 
                LEFT JOIN categories c ON b.category_id = c.id 
                LEFT JOIN payment_methods p ON b.payment_method_id = p.id
                WHERE b.paid = 0 
                AND b.due_date IS NOT NULL 
                AND date(b.due_date) BETWEEN date(?) AND date(?)
                ORDER BY b.due_date
            ''', (today.isoformat(), future_date.isoformat()))
            
            rows = cursor.fetchall()
            reminders = []
            for row in rows:
                bill = dict(row)
                bill['paid'] = bool(bill.get('paid', 0))
                if not bill.get('category_name'):
                    bill['category_name'] = 'Uncategorized'
                if not bill.get('payment_method_name'):
                    bill['payment_method_name'] = 'Not Set'
                    
                # Calculate days until due
                due_date = datetime.strptime(bill['due_date'], '%Y-%m-%d').date()
                days_until_due = (due_date - today).days
                bill['days_until_due'] = days_until_due
                
                reminders.append(bill)
                
            return reminders
            
        except Exception as e:
            logger.error(f"Error getting upcoming reminders: {e}")
            return []
        finally:
            conn.close()
            
    def mark_reminder_sent(self, bill_id: int, due_date: str):
        """
        Mark a reminder as sent to avoid duplicate notifications.
        
        Args:
            bill_id: ID of the bill
            due_date: Due date of the bill
        """
        reminder_key = f"{bill_id}_{due_date}"
        self.sent_reminders.add(reminder_key)
        
    def clear_sent_reminders(self):
        """Clear all sent reminders (useful for testing or reset)."""
        self.sent_reminders.clear()
        logger.info("Cleared all sent reminders")
        
    def get_service_status(self) -> Dict:
        """
        Get the current status of the reminder service.
        
        Returns:
            Dictionary with service status information
        """
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'sent_reminders_count': len(self.sent_reminders),
            'thread_alive': self.thread.is_alive() if self.thread else False
        } 
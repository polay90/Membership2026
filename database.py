import sqlite3
from datetime import datetime
from config import DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database tables"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      phone_number TEXT UNIQUE,
                      balance INTEGER DEFAULT 0,
                      is_verified INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # OTP table
        c.execute('''CREATE TABLE IF NOT EXISTS otp
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      otp_code TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      expired_at TIMESTAMP,
                      used INTEGER DEFAULT 0,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        
        # Transactions table
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      service_name TEXT,
                      amount INTEGER,
                      status TEXT DEFAULT 'completed',
                      service_data TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        
        # Top-up requests table
        c.execute('''CREATE TABLE IF NOT EXISTS topup_requests
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      amount INTEGER,
                      proof_file_id TEXT,
                      status TEXT DEFAULT 'pending',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      verified_at TIMESTAMP,
                      verified_by INTEGER,
                      FOREIGN KEY(user_id) REFERENCES users(user_id))''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

def get_user(user_id):
    """Get user by user_id"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None

def get_user_by_phone(phone_number):
    """Get user by phone number"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
        user = c.fetchone()
        conn.close()
        return user
    except Exception as e:
        logger.error(f"Error getting user by phone: {e}")
        return None

def create_user(user_id, phone_number):
    """Create new user"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO users (user_id, phone_number, balance) VALUES (?, ?, ?)',
                 (user_id, phone_number, 0))
        conn.commit()
        conn.close()
        logger.info(f"User created: {user_id}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"User already exists: {user_id}")
        return False
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return False

def get_balance(user_id):
    """Get user balance"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        return 0

def reduce_balance(user_id, amount):
    """Reduce user balance and return True if successful"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Check current balance
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        
        if not result or result[0] < amount:
            conn.close()
            return False
        
        # Reduce balance
        c.execute('UPDATE users SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                 (amount, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error reducing balance: {e}")
        return False

def add_balance(user_id, amount):
    """Add balance to user (for admin top-up)"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('UPDATE users SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                 (amount, user_id))
        conn.commit()
        conn.close()
        logger.info(f"Added {amount} to user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding balance: {e}")
        return False

def save_transaction(user_id, service_name, amount, service_data):
    """Save transaction record"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO transactions (user_id, service_name, amount, service_data) VALUES (?, ?, ?, ?)',
                 (user_id, service_name, amount, service_data))
        conn.commit()
        conn.close()
        logger.info(f"Transaction saved for user {user_id}: {service_name}")
        return True
    except Exception as e:
        logger.error(f"Error saving transaction: {e}")
        return False

def save_otp(user_id, otp_code, expired_at):
    """Save OTP"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO otp (user_id, otp_code, expired_at) VALUES (?, ?, ?)',
                 (user_id, otp_code, expired_at))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving OTP: {e}")
        return False

def verify_otp_code(user_id, otp_code):
    """Verify OTP code and return True if valid"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Get latest OTP
        c.execute('''SELECT id, expired_at, used FROM otp 
                     WHERE user_id = ? AND used = 0 
                     ORDER BY created_at DESC LIMIT 1''', (user_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return False
        
        otp_id, expired_at, used = result
        
        # Check if expired
        expired_time = datetime.fromisoformat(expired_at)
        if datetime.now() > expired_time:
            conn.close()
            return False
        
        # Mark as used
        c.execute('UPDATE otp SET used = 1 WHERE id = ?', (otp_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return False

def create_topup_request(user_id, amount, proof_file_id):
    """Create top-up request"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO topup_requests (user_id, amount, proof_file_id) VALUES (?, ?, ?)',
                 (user_id, amount, proof_file_id))
        request_id = c.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Top-up request created: {request_id}")
        return request_id
    except Exception as e:
        logger.error(f"Error creating top-up request: {e}")
        return None

def get_pending_topups():
    """Get all pending top-up requests"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('SELECT id, user_id, amount, proof_file_id, created_at FROM topup_requests WHERE status = "pending"')
        topups = c.fetchall()
        conn.close()
        return topups
    except Exception as e:
        logger.error(f"Error getting pending topups: {e}")
        return []

def approve_topup(topup_id, admin_id):
    """Approve top-up request"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        
        # Get topup details
        c.execute('SELECT user_id, amount FROM topup_requests WHERE id = ?', (topup_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return False
        
        user_id, amount = result
        
        # Update topup status
        c.execute('UPDATE topup_requests SET status = "approved", verified_by = ?, verified_at = CURRENT_TIMESTAMP WHERE id = ?',
                 (admin_id, topup_id))
        
        # Add balance to user
        c.execute('UPDATE users SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?',
                 (amount, user_id))
        
        conn.commit()
        conn.close()
        logger.info(f"Top-up {topup_id} approved, added {amount} to user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error approving topup: {e}")
        return False

def reject_topup(topup_id):
    """Reject top-up request"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        c.execute('UPDATE topup_requests SET status = "rejected" WHERE id = ?', (topup_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error rejecting topup: {e}")
        return False

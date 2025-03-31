import sqlite3
from pathlib import Path
import logging
from datetime import datetime

class Database:
    def __init__(self, db_path='finance.db'):
        self.db_path = Path(db_path)
        self.conn = None
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='finance_manager.log'
        )
        
    def connect(self):
        try:
            if not self.conn:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.execute("PRAGMA foreign_keys = ON")
                logging.info("Database connection established")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database connection failed: {str(e)}")
            return False
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            logging.info("Database connection closed")
    
    def initialize(self):
        if not self.connect():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            tables = {
                'stock': """
                CREATE TABLE IF NOT EXISTS stock (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    transaction_type TEXT CHECK(transaction_type IN ('Purchase', 'Sale')),
                    vendor_name TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity REAL NOT NULL CHECK(quantity > 0),
                    unit_price REAL NOT NULL CHECK(unit_price >= 0),
                    total_price REAL NOT NULL CHECK(total_price >= 0),
                    UNIQUE(date, transaction_type, vendor_name, item_name)
                )""",
                
                'financial_records': """
                CREATE TABLE IF NOT EXISTS financial_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT CHECK(type IN ('income', 'expense')),
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    verified BOOLEAN DEFAULT 0 CHECK(verified IN (0, 1))
                )""",
                
                'categories': """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT CHECK(type IN ('income', 'expense')),
                    name TEXT NOT NULL,
                    UNIQUE(type, name)
                )""",
                
                'settings': """
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    company_name TEXT NOT NULL DEFAULT 'My Business',
                    logo_path TEXT DEFAULT 'assets/logo.png',
                    address TEXT,
                    tax_rate REAL NOT NULL DEFAULT 0.0 CHECK(tax_rate >= 0),
                    invoice_counter INTEGER DEFAULT 1
                )"""
            }
            
            for table, schema in tables.items():
                cursor.execute(schema)
                logging.info(f"Table {table} verified/created")
            
            cursor.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
            
            default_categories = [
                ('income', 'Sales'),
                ('income', 'Services'),
                ('expense', 'Supplies'),
                ('expense', 'Rent')
            ]
            for cat_type, name in default_categories:
                try:
                    cursor.execute(
                        "INSERT INTO categories (type, name) VALUES (?, ?)",
                        (cat_type, name)
                    )
                except sqlite3.IntegrityError:
                    pass
            
            self.conn.commit()
            logging.info("Database initialized successfully")
            return True
            
        except sqlite3.Error as e:
            logging.error(f"Database initialization failed: {str(e)}")
            return False
    
    def execute_query(self, query, params=(), commit=False):
        try:
            self.connect()  # Ensure connection is open
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            if commit:
                self.conn.commit()
            return cursor
        except sqlite3.Error as e:
            logging.error(f"Query failed: {query} - Error: {str(e)}")
            raise
    
    def backup_database(self):
        backup_path = self.db_path.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            with sqlite3.connect(str(backup_path)) as backup:
                self.connect()
                self.conn.backup(backup)
            logging.info(f"Database backup created at {backup_path}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Backup failed: {str(e)}")
            return False
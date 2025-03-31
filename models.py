from dataclasses import dataclass
from datetime import date
from typing import List, Dict
import re

@dataclass
class StockTransaction:
    date: date
    transaction_type: str  # 'Purchase' or 'Sale'
    vendor_name: str
    item_name: str
    quantity: float
    unit_price: float
    
    def validate(self):
        errors = []
        if self.transaction_type not in ['Purchase', 'Sale']:
            errors.append("Transaction type must be 'Purchase' or 'Sale'")
        if not self.vendor_name.strip():
            errors.append("Vendor name cannot be empty")
        if not self.item_name.strip():
            errors.append("Item name cannot be empty")
        if self.quantity <= 0:
            errors.append("Quantity must be positive")
        if self.unit_price < 0:
            errors.append("Unit price cannot be negative")
        return errors

@dataclass
class FinancialRecord:
    record_type: str  # 'income' or 'expense'
    date: date
    category: str
    description: str
    amount: float
    
    def validate(self):
        errors = []
        if self.record_type not in ['income', 'expense']:
            errors.append("Record type must be 'income' or 'expense'")
        if not self.category.strip():
            errors.append("Category cannot be empty")
        if self.amount <= 0:
            errors.append("Amount must be positive")
        return errors

@dataclass
class Invoice:
    customer_name: str
    customer_address: str
    items: List[Dict]  # List of {'description': str, 'quantity': int, 'price': float}
    tax_rate: float
    
    def validate(self):
        errors = []
        if not self.customer_name.strip():
            errors.append("Customer name cannot be empty")
        if not self.items:
            errors.append("Invoice must have at least one item")
        for item in self.items:
            if not item.get('description', '').strip():
                errors.append("Item description cannot be empty")
            if item.get('quantity', 0) <= 0:
                errors.append("Item quantity must be positive")
            if item.get('price', 0) <= 0:
                errors.append("Item price must be positive")
        if self.tax_rate < 0:
            errors.append("Tax rate cannot be negative")
        return errors

@dataclass
class Settings:
    company_name: str
    logo_path: str
    address: str
    tax_rate: float
    
    def validate(self):
        errors = []
        if not self.company_name.strip():
            errors.append("Company name cannot be empty")
        if self.tax_rate < 0:
            errors.append("Tax rate cannot be negative")
        return errors
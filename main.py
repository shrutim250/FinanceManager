import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import logging
from database import Database
from models import Settings
from invoice_template import InvoiceTemplate

class FinanceManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Manager Pro")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.db = Database()
        try:
            if not self.db.initialize():
                messagebox.showerror("Error", "Failed to initialize database")
                self.root.destroy()
                return
            
            # Load settings
            self.settings = self._load_settings()
            if not self.settings:
                self.settings = Settings("My Business", "assets/logo.png", "", 0.0)
            
            # Setup UI
            self._setup_ui()
            self._load_initial_data()
            
            # Backup on startup
            self.db.backup_database()
            
        except Exception as e:
            messagebox.showerror("Error", f"Application failed to start: {str(e)}")
            self.root.destroy()
    
    def _setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self._create_stock_tab()
        self._create_income_tab()
        self._create_expense_tab()
        self._create_invoice_tab()
        self._create_reports_tab()
        self._create_settings_tab()
        
        self._create_menu()
    
    def _load_settings(self):
        try:
            cursor = self.db.execute_query("SELECT * FROM settings WHERE id=1")
            settings_data = cursor.fetchone()
            if settings_data:
                return Settings(
                    company_name=settings_data[1],
                    logo_path=settings_data[2],
                    address=settings_data[3],
                    tax_rate=settings_data[4]
                )
            return Settings("My Business", "assets/logo.png", "", 0.0)
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")
            return None
    
    def _load_initial_data(self):
        pass
    
    def _create_stock_tab(self):
        pass
    
    def _create_income_tab(self):
        pass
    
    def _create_expense_tab(self):
        pass
    
    def _create_invoice_tab(self):
        self.invoice_template = InvoiceTemplate(self.db)
    
    def _create_reports_tab(self):
        pass
    
    def _create_settings_tab(self):
        pass
    
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Backup Database", command=self._backup_database)
        file_menu.add_command(label="Export Data", command=self._export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Verify Data", command=self._verify_data)
        tools_menu.add_command(label="Recalculate Totals", command=self._recalculate_totals)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        self.root.config(menu=menubar)
    
    def _backup_database(self):
        if self.db.backup_database():
            messagebox.showinfo("Success", "Database backup created successfully")
        else:
            messagebox.showerror("Error", "Failed to create database backup")
    
    def _export_data(self):
        file_types = [('CSV Files', '*.csv'), ('All Files', '*.*')]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=file_types,
            title="Export Data"
        )
        
        if not file_path:
            return
        
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            self.invoice_template.export_data(current_tab, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def _verify_data(self):
        pass
    
    def _recalculate_totals(self):
        pass
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceManagerApp(root)
    root.mainloop()

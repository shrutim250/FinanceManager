import os
import logging
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from PIL import ImageTk, Image
import uuid
import urllib.request

# Setup logging
logging.basicConfig(level=logging.INFO)

# Download logo from provided URL if not already downloaded
logo_url = "https://static.vecteezy.com/system/resources/previews/008/214/517/non_2x/abstract-geometric-logo-or-infinity-line-logo-for-your-company-free-vector.jpg"
downloaded_logo = "downloaded_logo.png"

def download_logo():
    if not os.path.exists(downloaded_logo):
        try:
            urllib.request.urlretrieve(logo_url, downloaded_logo)
            print("Logo downloaded successfully.")
        except Exception as e:
            print(f"Error downloading logo: {e}")

download_logo()

# Default logo path is the downloaded logo if available
logo_path = downloaded_logo if os.path.exists(downloaded_logo) else "assets/logo.png"
selected_logo_path = logo_path

# Initialize Tkinter window
root = tk.Tk()
root.title("Finance Manager")
root.geometry("500x600")

class FinanceManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stock_records = []
        self.income_expense = {"income": [], "expense": []}

    def add_stock(self, entry_type, vendor, product, quantity, price):
        self.stock_records.append({
            "type": entry_type,
            "vendor": vendor,
            "product": product,
            "quantity": quantity,
            "price": price
        })

    def add_income_expense(self, category, amount, entry_type):
        self.income_expense[entry_type].append({
            "category": category,
            "amount": amount
        })

    def calculate_profit_loss(self):
        total_income = sum(entry['amount'] for entry in self.income_expense['income'])
        total_expense = sum(entry['amount'] for entry in self.income_expense['expense'])
        return total_income - total_expense

    def generate_invoice(self, invoice_data):
        try:
            output_path = f"Invoice_{invoice_data['number']}.pdf"
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter

            # Draw header text
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Invoice")

            # Draw logo on top-right
            if os.path.exists(invoice_data["logo_path"]):
                c.drawImage(invoice_data["logo_path"], width - 150, height - 100, width=100, height=50)

            # Draw invoice info
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Invoice #: {invoice_data['number']}")
            c.drawString(50, height - 100, f"Date: {invoice_data['date']}")

            # Draw customer info
            c.drawString(50, height - 130, f"Customer Name: {invoice_data['customer_name']}")
            c.drawString(50, height - 150, f"Address: {invoice_data['customer_address']}")

            # Draw the items table using ReportLab's Table
            self._draw_items_table(c, width, height, invoice_data)

            c.save()
            self.logger.info(f"Invoice generated successfully at {output_path}")
            self.preview_pdf(output_path)
            return True, output_path
        except Exception as e:
            self.logger.error(f"Invoice generation failed: {str(e)}")
            return False, str(e)

    def _draw_items_table(self, c, width, height, invoice):
        data = [["Description", "Quantity", "Unit Price", "Total"]]
        for item in invoice["items"]:
            data.append([
                item["description"],
                str(item["quantity"]),
                f"${item['price']:.2f}",
                f"${item['quantity'] * item['price']:.2f}"
            ])
        data.append(["", "", "Subtotal:", f"${invoice['subtotal']:.2f}"])
        data.append(["", "", "Tax (10%):", f"${invoice['tax']:.2f}"])
        data.append(["", "", "Total:", f"${invoice['total']:.2f}"])

        table = Table(data, colWidths=[300, 60, 80, 80])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ])
        table.setStyle(style)
        table.wrapOn(c, width, height)
        table.drawOn(c, 50, height - 300)

    def preview_pdf(self, file_path):
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            elif os.name == 'posix':
                cmd = "open" if "darwin" in os.sys.platform else "xdg-open"
                subprocess.run([cmd, file_path], check=True)
            else:
                webbrowser.open(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {e}")

finance_manager = FinanceManager()

# Invoice Input Variables
invoice_number = tk.StringVar()
invoice_date = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
customer_name = tk.StringVar()

# Function to generate invoice from user inputs and stock records
def generate_invoice_gui():
    # If invoice number is empty, generate a random 8-character hash
    if not invoice_number.get().strip():
        invoice_number.set(str(uuid.uuid4())[:8])
    
    if not customer_name.get().strip():
        messagebox.showerror("Error", "Customer name is required.")
        return

    address = customer_address.get("1.0", "end").strip()
    if not address:
        messagebox.showerror("Error", "Customer address is required.")
        return

    # Use the first stock record as the invoice item, if available.
    if not finance_manager.stock_records:
        messagebox.showerror("Error", "No stock records available.")
        return

    stock_item = finance_manager.stock_records[0]

    invoice_data = {
        "number": invoice_number.get().strip(),
        "date": invoice_date.get().strip(),
        "customer_name": customer_name.get().strip(),
        "customer_address": address,
        "items": [{
            "description": stock_item["product"],
            "quantity": stock_item["quantity"],
            "price": stock_item["price"]
        }],
        "subtotal": stock_item["quantity"] * stock_item["price"],
        "tax": (stock_item["quantity"] * stock_item["price"]) * 0.1,
        "total": (stock_item["quantity"] * stock_item["price"]) * 1.1,
        "logo_path": selected_logo_path if os.path.exists(selected_logo_path) else logo_path
    }

    success, msg = finance_manager.generate_invoice(invoice_data)
    messagebox.showinfo("Invoice", "Invoice generated successfully!" if success else f"Error: {msg}")

# Additional functions for stock, income, expense management using CLI input (kept as-is)
def add_stock_entry():
    vendor = input("Enter vendor: ")
    product = input("Enter product: ")
    quantity = int(input("Enter quantity: "))
    price = float(input("Enter price: "))
    entry_type = input("Enter type (purchase/sale): ").strip().lower()
    if entry_type not in ["purchase", "sale"]:
        messagebox.showerror("Error", "Invalid entry type. Use 'purchase' or 'sale'.")
        return
    finance_manager.add_stock(entry_type, vendor, product, quantity, price)
    messagebox.showinfo("Success", f"{entry_type.capitalize()} entry added.")

def add_income():
    category = input("Enter income category: ")
    amount = float(input("Enter amount: "))
    finance_manager.add_income_expense(category, amount, "income")
    messagebox.showinfo("Success", "Income added.")

def add_expense():
    category = input("Enter expense category: ")
    amount = float(input("Enter amount: "))
    finance_manager.add_income_expense(category, amount, "expense")
    messagebox.showinfo("Success", "Expense added.")

def show_profit_loss():
    profit_loss = finance_manager.calculate_profit_loss()
    status = "Profit" if profit_loss >= 0 else "Loss"
    messagebox.showinfo("Net Profit/Loss", f"Net {status}: ${abs(profit_loss):.2f}")

# UI Layout
frame = ttk.Frame(root, padding=20)
frame.pack(expand=True)

# Invoice input fields
ttk.Label(frame, text="Invoice #").pack()
ttk.Entry(frame, textvariable=invoice_number).pack()

ttk.Label(frame, text="Date").pack()
ttk.Entry(frame, textvariable=invoice_date, state="readonly").pack()

ttk.Label(frame, text="Customer Name").pack()
ttk.Entry(frame, textvariable=customer_name).pack()

ttk.Label(frame, text="Customer Address").pack()
customer_address = tk.Text(frame, height=3, width=40)
customer_address.pack()

# Buttons for other functionalities
ttk.Button(frame, text="Add Stock Entry", command=add_stock_entry).pack(pady=5)
ttk.Button(frame, text="Add Income", command=add_income).pack(pady=5)
ttk.Button(frame, text="Add Expense", command=add_expense).pack(pady=5)
ttk.Button(frame, text="Show Net Profit/Loss", command=show_profit_loss).pack(pady=5)
ttk.Button(frame, text="Generate Invoice", command=generate_invoice_gui).pack(pady=5)

root.mainloop()

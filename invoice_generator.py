import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch


COUNTER_FILE = "invoice_counter.txt"
LOGO_FILE = "luxeralogo.png"
COMPANY_NAME = "LUXERA DIGITAL"
CURRENCY = "₹"
PAYMENT_CLAUSE = "All payment must be made within 3 days of product submission."


def get_next_invoice_number():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            try:
                counter = int(f.read().strip())
            except ValueError:
                counter = 0
    else:
        counter = 0
    
    counter += 1
    
    with open(COUNTER_FILE, "w") as f:
        f.write(str(counter))
    
    return counter


def generate_invoice_number(num):
    return f"LUX-{num:03d}"


service_entries = []


def get_customer_data():
    return {
        "customer_name": entry_customer_name.get().strip(),
        "contact_person": entry_contact_person.get().strip(),
        "email": entry_email.get().strip(),
        "phone": entry_phone.get().strip(),
        "address": entry_address.get("1.0", tk.END).strip(),
        "city": entry_city.get().strip(),
        "state": entry_state.get().strip(),
        "country": entry_country.get().strip(),
        "postal_code": entry_postal_code.get().strip(),
    }


def get_service_entries_data():
    entries = []
    for frame, product_entry, desc_entry, qty_entry, price_entry in service_entries:
        product = product_entry.get().strip()
        description = desc_entry.get("1.0", tk.END).strip()
        qty_str = qty_entry.get().strip()
        price_str = price_entry.get().strip()
        
        if product or description or qty_str or price_str:
            if not product:
                return None, "Product/Service name is required"
            if not qty_str:
                return None, "Quantity is required"
            if not price_str:
                return None, "Unit Price is required"
            try:
                qty = float(qty_str)
                price = float(price_str)
                if qty <= 0 or price < 0:
                    return None, "Quantity must be positive and price must be non-negative"
            except ValueError:
                return None, "Quantity and Price must be valid numbers"
            
            entries.append({
                "product": product,
                "description": description,
                "quantity": qty,
                "unit_price": price,
                "subtotal": qty * price
            })
    return entries, None


def find_in_row(row, field_names):
    for key in row.keys():
        for fname in field_names:
            if key.lower().strip() == fname.lower():
                return row[key].strip()
    return ""


def load_customer_from_csv():
    file_path = filedialog.askopenfilename(
        title="Select Customer CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                messagebox.showerror("Error", "CSV file is empty")
                return
            
            row = rows[0]
            
            field_mappings = {
                'customer_name': ['customer_name', 'customer name', 'name', 'client_name', 'client name'],
                'contact_person': ['contact_person', 'contact person', 'contact', 'person'],
                'email': ['email', 'email_address', 'e-mail', 'mail'],
                'phone': ['phone', 'phone_number', 'phone number', 'contact_no', 'contact number', 'mobile'],
                'address': ['address', 'billing_address', 'billing address', 'street'],
                'city': ['city', 'town'],
                'state': ['state', 'state_province', 'province', 'region'],
                'country': ['country', 'nation'],
                'postal_code': ['postal_code', 'postal code', 'zip', 'zipcode', 'zip_code', 'pincode', 'pin code'],
            }
            
            def find_value(field_names):
                for fname in field_names:
                    for key in row.keys():
                        if key.lower().strip() == fname.lower():
                            return row[key].strip()
                return ""
            
            entry_customer_name.delete(0, tk.END)
            entry_customer_name.insert(0, find_value(field_mappings['customer_name']))
            
            entry_contact_person.delete(0, tk.END)
            entry_contact_person.insert(0, find_value(field_mappings['contact_person']))
            
            entry_email.delete(0, tk.END)
            entry_email.insert(0, find_value(field_mappings['email']))
            
            entry_phone.delete(0, tk.END)
            entry_phone.insert(0, find_value(field_mappings['phone']))
            
            entry_address.delete("1.0", tk.END)
            entry_address.insert("1.0", find_value(field_mappings['address']))
            
            entry_city.delete(0, tk.END)
            entry_city.insert(0, find_value(field_mappings['city']))
            
            entry_state.delete(0, tk.END)
            entry_state.insert(0, find_value(field_mappings['state']))
            
            entry_country.delete(0, tk.END)
            entry_country.insert(0, find_value(field_mappings['country']))
            
            entry_postal_code.delete(0, tk.END)
            entry_postal_code.insert(0, find_value(field_mappings['postal_code']))
            
            product_mappings = ['product', 'product_name', 'product name', 'service', 'service_name', 'item', 'item_name', 'description', 'item_description']
            desc_mappings = ['description', 'desc', 'details', 'product_description', 'service_description']
            qty_mappings = ['quantity', 'qty', 'quantity', 'count', 'units']
            price_mappings = ['price', 'unit_price', 'unit price', 'rate', 'amount', 'price_per_unit']
            
            clear_all_services()
            
            for csv_row in rows:
                product = find_in_row(csv_row, product_mappings)
                description = find_in_row(csv_row, desc_mappings)
                qty_str = find_in_row(csv_row, qty_mappings)
                price_str = find_in_row(csv_row, price_mappings)
                
                if product:
                    add_service_row()
                    if service_entries:
                        frame, product_entry, desc_entry, qty_entry, price_entry = service_entries[-1]
                        product_entry.insert(0, product)
                        if description:
                            desc_entry.insert("1.0", description)
                        if qty_str:
                            try:
                                qty_entry.insert(0, str(int(float(qty_str))))
                            except:
                                qty_entry.insert(0, "1")
                        if price_str:
                            try:
                                price_entry.insert(0, str(float(price_str)))
                            except:
                                price_entry.insert(0, "0")
            
            messagebox.showinfo("Success", f"Loaded {len(rows)} customer(s)/product(s) from CSV")
    
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")


def create_pdf(invoice_num_str, customer, services, tax_percent, payment_terms, payment_due_date, payment_method):
    subtotal = sum(s["subtotal"] for s in services)
    tax_amount = subtotal * (tax_percent / 100)
    total = subtotal + tax_amount
    
    pdf_filename = f"{invoice_num_str}.pdf"
    
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=40, bottomMargin=40)
    story = []
    
    brand_color = colors.HexColor("#2C3E50")
    accent_color = colors.HexColor("#E74C3C")
    light_bg = colors.HexColor("#ECF0F1")
    dark_text = colors.HexColor("#2C3E50")
    
    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=32, textColor=brand_color, spaceAfter=5, alignment=1)
    subtitle_style = ParagraphStyle('Subtitle', fontName='Helvetica', fontSize=12, textColor=accent_color, spaceAfter=20, alignment=1)
    heading_style = ParagraphStyle('Heading', fontName='Helvetica-Bold', fontSize=12, textColor=brand_color, spaceAfter=8)
    normal_style = ParagraphStyle('Normal', fontName='Helvetica', fontSize=10, textColor=dark_text, spaceAfter=5)
    label_style = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#7F8C8D"), spaceAfter=2)
    footer_style = ParagraphStyle('Footer', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor("#95A5A6"), alignment=1, spaceAfter=3)
    
    if os.path.exists(LOGO_FILE):
        try:
            logo = Image(LOGO_FILE, width=180, height=70)
            logo.hAlign = 'CENTER'
            story.append(logo)
        except Exception:
            story.append(Paragraph(COMPANY_NAME, title_style))
    else:
        story.append(Paragraph(COMPANY_NAME, title_style))
    
    story.append(Paragraph("INVOICE", subtitle_style))
    
    header_data = [
        [Paragraph("<b>INVOICE #</b>", label_style), Paragraph("<b>DATE</b>", label_style), Paragraph("<b>DUE DATE</b>", label_style)],
        [invoice_num_str, datetime.now().strftime("%B %d, %Y"), payment_due_date if payment_due_date else "N/A"]
    ]
    header_table = Table(header_data, colWidths=[2*inch, 2*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), brand_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 1), (-1, 1), 8),
        ('GRID', (0, 0), (-1, 1), 0.5, colors.HexColor("#BDC3C7")),
    ]))
    story.append(Spacer(1, 25))
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    bill_to = []
    if customer["customer_name"]:
        bill_to.append(Paragraph("<b>" + customer["customer_name"] + "</b>", normal_style))
    if customer["contact_person"]:
        bill_to.append(Paragraph(f"Contact: {customer['contact_person']}", normal_style))
    if customer["address"]:
        bill_to.append(Paragraph(customer["address"], normal_style))
    city_state = []
    if customer["city"]:
        city_state.append(customer["city"])
    if customer["state"]:
        city_state.append(customer["state"])
    if customer["postal_code"]:
        city_state.append(customer["postal_code"])
    if customer["country"]:
        city_state.append(customer["country"])
    if city_state:
        bill_to.append(Paragraph(", ".join(city_state), normal_style))
    if customer["email"]:
        bill_to.append(Paragraph(customer["email"], normal_style))
    if customer["phone"]:
        bill_to.append(Paragraph(f"Phone: {customer['phone']}", normal_style))
    
    story.append(Paragraph("BILL TO", heading_style))
    story.append(Spacer(1, 5))
    for line in bill_to:
        story.append(line)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("SERVICE / PRODUCT", heading_style))
    story.append(Spacer(1, 5))
    
    product_data = [[Paragraph("<b>#</b>", label_style), Paragraph("<b>Item</b>", label_style), Paragraph("<b>Description</b>", label_style), Paragraph("<b>Qty</b>", label_style), Paragraph("<b>Unit Price</b>", label_style), Paragraph("<b>Amount</b>", label_style)]]
    
    for idx, service in enumerate(services, 1):
        product_data.append([
            Paragraph(str(idx), normal_style),
            Paragraph(service["product"], normal_style),
            Paragraph(service["description"] if service["description"] else "-", normal_style),
            Paragraph(str(int(service["quantity"])), normal_style),
            Paragraph(f"{CURRENCY}{service['unit_price']:,.2f}", normal_style),
            Paragraph(f"{CURRENCY}{service['subtotal']:,.2f}", normal_style)
        ])
    
    product_table = Table(product_data, colWidths=[0.4*inch, 1.5*inch, 2.5*inch, 0.6*inch, 1*inch, 1.2*inch])
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), light_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), brand_color),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('ALIGN', (5, 0), (5, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
    ]))
    story.append(product_table)
    story.append(Spacer(1, 20))
    
    totals_data = [
        [Paragraph("Subtotal", normal_style), f"{CURRENCY}{subtotal:,.2f}"],
        [Paragraph(f"Tax ({tax_percent}%)", normal_style), f"{CURRENCY}{tax_amount:,.2f}"],
        [Paragraph("<b>Total Due</b>", heading_style), Paragraph(f"<b>{CURRENCY}{total:,.2f}</b>", ParagraphStyle('Total', fontName='Helvetica-Bold', fontSize=14, textColor=accent_color))],
    ]
    totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 12),
        ('TOPPADDING', (0, 2), (-1, 2), 10),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 10),
        ('LINEABOVE', (0, 2), (-1, 2), 1, brand_color),
    ]))
    story.append(Spacer(1, 15))
    story.append(totals_table)
    story.append(Spacer(1, 25))
    
    if payment_terms or payment_due_date or payment_method:
        story.append(Paragraph("PAYMENT DETAILS", heading_style))
        story.append(Spacer(1, 5))
        payment_info = []
        if payment_terms:
            payment_info.append(Paragraph(f"<b>Payment Terms:</b> {payment_terms}", normal_style))
        if payment_due_date:
            payment_info.append(Paragraph(f"<b>Due Date:</b> {payment_due_date}", normal_style))
        if payment_method:
            payment_info.append(Paragraph(f"<b>Payment Method:</b> {payment_method}", normal_style))
        for p in payment_info:
            story.append(p)
        story.append(Spacer(1, 20))
    
    story.append(Paragraph("─" * 60, footer_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(PAYMENT_CLAUSE, footer_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Thank you for your business!", ParagraphStyle('Thanks', fontName='Helvetica', fontSize=10, textColor=brand_color, alignment=1)))
    story.append(Spacer(1, 3))
    story.append(Paragraph("theluxeradigital@gmail.com", footer_style))
    
    doc.build(story)
    return pdf_filename


def add_service_row():
    frame = ttk.Frame(services_frame, relief="solid", padding=10)
    frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(frame, text="Product/Service:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
    product_entry = ttk.Entry(frame, width=25)
    product_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
    
    ttk.Label(frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
    desc_entry = tk.Text(frame, width=25, height=2)
    desc_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
    
    ttk.Label(frame, text="Qty:").grid(row=2, column=0, sticky=tk.W)
    qty_entry = ttk.Entry(frame, width=8)
    qty_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
    qty_entry.insert(0, "1")
    
    ttk.Label(frame, text=f"Unit Price ({CURRENCY}):").grid(row=2, column=2, sticky=tk.W, padx=(10, 0))
    price_entry = ttk.Entry(frame, width=12)
    price_entry.grid(row=2, column=3, sticky=tk.W, padx=(10, 0))
    
    service_entries.append((frame, product_entry, desc_entry, qty_entry, price_entry))


def clear_all_services():
    for frame, _, _, _, _ in service_entries:
        frame.destroy()
    service_entries.clear()
    add_service_row()


def calculate_due_date(days=3):
    due = datetime.now() + timedelta(days=days)
    return due.strftime("%B %d, %Y")


def generate_invoice():
    customer = get_customer_data()
    tax_str = entry_tax.get()
    payment_terms = combo_payment_terms.get()
    payment_due_date = entry_due_date.get().strip()
    payment_method = combo_payment_method.get()
    
    if not customer["customer_name"]:
        messagebox.showerror("Validation Error", "Customer Name is required")
        return
    
    services, error = get_service_entries_data()
    if error:
        messagebox.showerror("Validation Error", error)
        return
    
    if not services:
        messagebox.showerror("Validation Error", "At least one service is required")
        return
    
    try:
        tax_percent = float(tax_str) if tax_str.strip() else 0
        if tax_percent < 0 or tax_percent > 100:
            messagebox.showerror("Validation Error", "Tax percentage must be between 0 and 100")
            return
    except ValueError:
        messagebox.showerror("Validation Error", "Tax must be a valid number")
        return
    
    if not payment_due_date:
        payment_due_date = calculate_due_date(3)
    
    invoice_num = get_next_invoice_number()
    invoice_num_str = generate_invoice_number(invoice_num)
    
    try:
        pdf_file = create_pdf(invoice_num_str, customer, services, tax_percent, payment_terms, payment_due_date, payment_method)
        messagebox.showinfo("Success", f"Invoice generated successfully!\n\nFile: {pdf_file}")
        
        entry_customer_name.delete(0, tk.END)
        entry_contact_person.delete(0, tk.END)
        entry_email.delete(0, tk.END)
        entry_phone.delete(0, tk.END)
        entry_address.delete("1.0", tk.END)
        entry_city.delete(0, tk.END)
        entry_state.delete(0, tk.END)
        entry_country.delete(0, tk.END)
        entry_postal_code.delete(0, tk.END)
        entry_tax.delete(0, tk.END)
        entry_tax.insert(0, "0")
        entry_due_date.delete(0, tk.END)
        combo_payment_terms.current(0)
        combo_payment_method.current(0)
        
        clear_all_services()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")


root = tk.Tk()
root.title("Luxera Invoice Generator")
root.geometry("650x850")
root.resizable(True, True)

main_frame = ttk.Frame(root, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

ttk.Label(scrollable_frame, text="Luxera Invoice Generator", font=("Arial", 16, "bold")).pack(pady=(0, 15))

btn_load_csv = ttk.Button(scrollable_frame, text="Load Customer from CSV", command=load_customer_from_csv)
btn_load_csv.pack(pady=(0, 15))

customer_frame = ttk.LabelFrame(scrollable_frame, text="Customer Details", padding=10)
customer_frame.pack(fill=tk.X, pady=(0, 15))

row = 0
ttk.Label(customer_frame, text="Customer Name *:").grid(row=row, column=0, sticky=tk.W, pady=3)
entry_customer_name = ttk.Entry(customer_frame, width=30)
entry_customer_name.grid(row=row, column=1, sticky=tk.W, padx=(10, 20), pady=3)

ttk.Label(customer_frame, text="Contact Person:").grid(row=row, column=2, sticky=tk.W, pady=3)
entry_contact_person = ttk.Entry(customer_frame, width=25)
entry_contact_person.grid(row=row, column=3, sticky=tk.W, pady=3)

row += 1
ttk.Label(customer_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=3)
entry_email = ttk.Entry(customer_frame, width=30)
entry_email.grid(row=row, column=1, sticky=tk.W, padx=(10, 20), pady=3)

ttk.Label(customer_frame, text="Phone:").grid(row=row, column=2, sticky=tk.W, pady=3)
entry_phone = ttk.Entry(customer_frame, width=25)
entry_phone.grid(row=row, column=3, sticky=tk.W, pady=3)

row += 1
ttk.Label(customer_frame, text="Billing Address:").grid(row=row, column=0, sticky=tk.W, pady=3)
entry_address = tk.Text(customer_frame, width=30, height=2)
entry_address.grid(row=row, column=1, sticky=tk.W, padx=(10, 20), pady=3)

ttk.Label(customer_frame, text="City:").grid(row=row, column=2, sticky=tk.W, pady=3)
entry_city = ttk.Entry(customer_frame, width=25)
entry_city.grid(row=row, column=3, sticky=tk.W, pady=3)

row += 1
ttk.Label(customer_frame, text="State/Province:").grid(row=row, column=0, sticky=tk.W, pady=3)
entry_state = ttk.Entry(customer_frame, width=30)
entry_state.grid(row=row, column=1, sticky=tk.W, padx=(10, 20), pady=3)

ttk.Label(customer_frame, text="Country:").grid(row=row, column=2, sticky=tk.W, pady=3)
entry_country = ttk.Entry(customer_frame, width=25)
entry_country.grid(row=row, column=3, sticky=tk.W, pady=3)

row += 1
ttk.Label(customer_frame, text="Postal Code:").grid(row=row, column=0, sticky=tk.W, pady=3)
entry_postal_code = ttk.Entry(customer_frame, width=30)
entry_postal_code.grid(row=row, column=1, sticky=tk.W, padx=(10, 20), pady=3)

services_label_frame = ttk.LabelFrame(scrollable_frame, text="Services / Products", padding=10)
services_label_frame.pack(fill=tk.X, pady=(0, 10))

services_frame = ttk.Frame(services_label_frame)
services_frame.pack(fill=tk.X)

add_service_row()

btn_add_service = ttk.Button(services_label_frame, text="+ Add Service", command=add_service_row)
btn_add_service.pack(pady=(10, 0))

payment_frame = ttk.LabelFrame(scrollable_frame, text="Payment Details", padding=10)
payment_frame.pack(fill=tk.X, pady=(0, 15))

row = 0
ttk.Label(payment_frame, text="Tax (%):").grid(row=row, column=0, sticky=tk.W, pady=5)
entry_tax = ttk.Entry(payment_frame, width=15)
entry_tax.insert(0, "0")
entry_tax.grid(row=row, column=1, sticky=tk.W, padx=(10, 20), pady=5)

ttk.Label(payment_frame, text="Payment Terms:").grid(row=row, column=2, sticky=tk.W, pady=5)
combo_payment_terms = ttk.Combobox(payment_frame, values=["Net 3", "Net 7", "Net 15", "Net 30", "Net 45", "Net 60", "Due on Receipt"], width=15)
combo_payment_terms.current(0)
combo_payment_terms.grid(row=row, column=3, sticky=tk.W, pady=5)

row += 1
ttk.Label(payment_frame, text="Due Date:").grid(row=row, column=0, sticky=tk.W, pady=5)
entry_due_date = ttk.Entry(payment_frame, width=15)
entry_due_date.grid(row=row, column=1, sticky=tk.W, padx=(10, 20), pady=5)

ttk.Label(payment_frame, text="Payment Method:").grid(row=row, column=2, sticky=tk.W, pady=5)
combo_payment_method = ttk.Combobox(payment_frame, values=["Bank Transfer", "Cash", "Cheque", "Credit Card", "Debit Card", "UPI", "PayPal", "Other"], width=15)
combo_payment_method.current(0)
combo_payment_method.grid(row=row, column=3, sticky=tk.W, pady=5)

btn_generate = ttk.Button(scrollable_frame, text="Generate Invoice", command=generate_invoice)
btn_generate.pack(pady=(15, 10), ipadx=20, ipady=5)

ttk.Label(scrollable_frame, text="Invoice will be saved as LUX-XXX.pdf", font=("Arial", 9), foreground="gray").pack()

if os.path.exists(LOGO_FILE):
    ttk.Label(scrollable_frame, text=f"Logo: {LOGO_FILE}", font=("Arial", 8), foreground="green").pack(pady=(10, 0))
else:
    ttk.Label(scrollable_frame, text=f"Note: Logo file not found", font=("Arial", 8), foreground="orange").pack(pady=(10, 0))

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

root.mainloop()

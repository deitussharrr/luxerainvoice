from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash
import os
import csv
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'luxera_secret_key_123'

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


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luxera Invoice Generator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { opacity: 0.8; }
        .card { background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .card h2 { color: #2C3E50; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #ECF0F1; }
        .form-row { display: flex; gap: 15px; margin-bottom: 15px; }
        .form-group { flex: 1; }
        .form-group label { display: block; margin-bottom: 5px; color: #2C3E50; font-weight: 600; font-size: 0.9rem; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 12px; border: 2px solid #E0E0E0; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s; }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus { outline: none; border-color: #E74C3C; }
        .form-group textarea { resize: vertical; min-height: 60px; }
        .btn { padding: 12px 30px; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; transition: all 0.3s; font-weight: 600; }
        .btn-primary { background: #E74C3C; color: white; }
        .btn-primary:hover { background: #c0392b; transform: translateY(-2px); }
        .btn-secondary { background: #3498db; color: white; }
        .btn-secondary:hover { background: #2980b9; }
        .btn-success { background: #27ae60; color: white; }
        .btn-success:hover { background: #229954; }
        .btn-group { display: flex; gap: 10px; margin-top: 20px; }
        .service-item { background: #F8F9FA; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #E74C3C; }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .service-header h4 { color: #2C3E50; }
        .remove-btn { background: #e74c3c; color: white; padding: 5px 15px; border: none; border-radius: 5px; cursor: pointer; }
        .invoice-preview { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; }
        .invoice-preview h3 { color: #2C3E50; margin-bottom: 15px; }
        .invoice-number { font-size: 2rem; font-weight: bold; color: #E74C3C; text-align: center; padding: 20px; background: #2C3E50; color: white; border-radius: 10px; margin-bottom: 20px; }
        .success-message { background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .error-message { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .fetch-section { background: #e8f4fd; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .fetch-section h3 { color: #2C3E50; margin-bottom: 15px; }
        .fetch-section input { flex: 1; padding: 12px; border: 2px solid #3498db; border-radius: 8px; }
        .fetch-result { background: white; padding: 15px; border-radius: 8px; margin-top: 15px; }
        .fetch-result p { margin: 5px 0; color: #2C3E50; }
        .fetch-result strong { color: #E74C3C; }
        .info-badge { background: #3498db; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.85rem; display: inline-block; margin-bottom: 15px; }
        .next-invoice { text-align: center; margin-bottom: 20px; }
        .next-invoice span { background: #27ae60; color: white; padding: 10px 25px; border-radius: 25px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LUXERA DIGITAL</h1>
            <p>Invoice Generator</p>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ 'success-message' if category == 'success' else 'error-message' }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <div class="card">
            <h2>Fetch Customer from URL</h2>
            <div class="fetch-section">
                <h3>Enter Customer API URL</h3>
                <form method="POST" action="/fetch-customer">
                    <div class="form-row">
                        <input type="url" name="api_url" placeholder="https://yoursite.com/api/customer/123" required>
                        <button type="submit" class="btn btn-secondary">Fetch Customer</button>
                    </div>
                </form>
                
                {% if fetched_customer %}
                <div class="fetch-result">
                    <h4>Fetched Customer Data:</h4>
                    <p><strong>Name:</strong> {{ fetched_customer.get('customer_name', fetched_customer.get('name', 'N/A')) }}</p>
                    <p><strong>Contact Person:</strong> {{ fetched_customer.get('contact_person', 'N/A') }}</p>
                    <p><strong>Email:</strong> {{ fetched_customer.get('email', 'N/A') }}</p>
                    <p><strong>Phone:</strong> {{ fetched_customer.get('phone', 'N/A') }}</p>
                    <p><strong>Address:</strong> {{ fetched_customer.get('address', '') }} {{ fetched_customer.get('city', '') }} {{ fetched_customer.get('state', '') }}</p>
                    <button class="btn btn-success" onclick="useCustomer()" style="margin-top:10px;">Use This Customer</button>
                </div>
                {% endif %}
            </div>
        </div>

        <form method="POST" action="/generate">
            <div class="card">
                <h2>Customer Details</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Customer Name *</label>
                        <input type="text" name="customer_name" id="customer_name" value="{{ customer.get('customer_name', '') }}" required>
                    </div>
                    <div class="form-group">
                        <label>Contact Person</label>
                        <input type="text" name="contact_person" value="{{ customer.get('contact_person', '') }}">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Email</label>
                        <input type="email" name="email" value="{{ customer.get('email', '') }}">
                    </div>
                    <div class="form-group">
                        <label>Phone</label>
                        <input type="text" name="phone" value="{{ customer.get('phone', '') }}">
                    </div>
                </div>
                <div class="form-group">
                    <label>Billing Address</label>
                    <textarea name="address">{{ customer.get('address', '') }}</textarea>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>City</label>
                        <input type="text" name="city" value="{{ customer.get('city', '') }}">
                    </div>
                    <div class="form-group">
                        <label>State/Province</label>
                        <input type="text" name="state" value="{{ customer.get('state', '') }}">
                    </div>
                    <div class="form-group">
                        <label>Country</label>
                        <input type="text" name="country" value="{{ customer.get('country', '') }}">
                    </div>
                    <div class="form-group">
                        <label>Postal Code</label>
                        <input type="text" name="postal_code" value="{{ customer.get('postal_code', '') }}">
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Services / Products</h2>
                <div id="services-container">
                    {% for i in range(services|length) %}
                    <div class="service-item">
                        <div class="service-header">
                            <h4>Service {{ i + 1 }}</h4>
                            {% if i > 0 %}
                            <button type="button" class="remove-btn" onclick="removeService(this)">Remove</button>
                            {% endif %}
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Product/Service Name</label>
                                <input type="text" name="product_{{ i }}" value="{{ services[i].get('product', '') }}" required>
                            </div>
                            <div class="form-group">
                                <label>Quantity</label>
                                <input type="number" name="quantity_{{ i }}" value="{{ services[i].get('quantity', 1) }}" min="1" onchange="calculateSubtotal(this)">
                            </div>
                            <div class="form-group">
                                <label>Unit Price (₹)</label>
                                <input type="number" name="unit_price_{{ i }}" value="{{ services[i].get('unit_price', 0) }}" min="0" step="0.01" onchange="calculateSubtotal(this)">
                            </div>
                            <div class="form-group">
                                <label>Subtotal (₹)</label>
                                <input type="text" name="subtotal_{{ i }}" value="{{ services[i].get('subtotal', 0) }}" readonly style="background: #e0e0e0;">
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea name="description_{{ i }}">{{ services[i].get('description', '') }}</textarea>
                        </div>
                    </div>
                    {% endfor %}
                </div>
                <button type="button" class="btn btn-secondary" onclick="addService()">+ Add Service</button>
            </div>

            <div class="card">
                <h2>Payment Details</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Tax Percentage (%)</label>
                        <input type="number" name="tax_percent" id="tax_percent" value="0" min="0" max="100" onchange="calculateTotal()">
                    </div>
                    <div class="form-group">
                        <label>Payment Terms</label>
                        <select name="payment_terms">
                            <option value="Net 3">Net 3</option>
                            <option value="Net 7" selected>Net 7</option>
                            <option value="Net 15">Net 15</option>
                            <option value="Net 30">Net 30</option>
                            <option value="Net 45">Net 45</option>
                            <option value="Net 60">Net 60</option>
                            <option value="Due on Receipt">Due on Receipt</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Payment Method</label>
                        <select name="payment_method">
                            <option value="Bank Transfer">Bank Transfer</option>
                            <option value="Cash">Cash</option>
                            <option value="Cheque">Cheque</option>
                            <option value="Credit Card">Credit Card</option>
                            <option value="Debit Card">Debit Card</option>
                            <option value="UPI">UPI</option>
                            <option value="PayPal">PayPal</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                </div>
                -preview">
                    <div class="invoice<h3>Invoice Summary</h3>
                    <div class="next-invoice">
                        <span>Next Invoice: {{ next_invoice }}</span>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Subtotal</label>
                            <input type="text" id="subtotal" value="0.00" readonly style="background: #e0e0e0;">
                        </div>
                        <div class="form-group">
                            <label>Tax Amount</label>
                            <input type="text" id="tax_amount" value="0.00" readonly style="background: #e0e0e0;">
                        </div>
                        <div class="form-group">
                            <label>Total Amount (₹)</label>
                            <input type="text" id="total_amount" value="0.00" readonly style="background: #2C3E50; color: white; font-weight: bold; font-size: 1.2rem;">
                        </div>
                    </div>
                </div>
            </div>

            <div class="btn-group" style="justify-content: center;">
                <button type="submit" class="btn btn-primary" style="font-size: 1.2rem; padding: 15px 50px;">Generate Invoice</button>
            </div>
        </form>

        <p style="text-align: center; color: white; margin-top: 20px; opacity: 0.7;">
            Invoice will be saved as LUX-XXX.pdf
        </p>
    </div>

    <script>
        let serviceCount = {{ services|length }};
        
        function addService() {
            serviceCount++;
            const container = document.getElementById('services-container');
            const html = `
                <div class="service-item">
                    <div class="service-header">
                        <h4>Service ${serviceCount}</h4>
                        <button type="button" class="remove-btn" onclick="removeService(this)">Remove</button>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Product/Service Name</label>
                            <input type="text" name="product_${serviceCount - 1}" required>
                        </div>
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" name="quantity_${serviceCount - 1}" value="1" min="1" onchange="calculateSubtotal(this)">
                        </div>
                        <div class="form-group">
                            <label>Unit Price (₹)</label>
                            <input type="number" name="unit_price_${serviceCount - 1}" value="0" min="0" step="0.01" onchange="calculateSubtotal(this)">
                        </div>
                        <div class="form-group">
                            <label>Subtotal (₹)</label>
                            <input type="text" name="subtotal_${serviceCount - 1}" value="0" readonly style="background: #e0e0e0;">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="description_${serviceCount - 1}"></textarea>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        }

        function removeService(btn) {
            btn.closest('.service-item').remove();
            calculateTotal();
        }

        function calculateSubtotal(input) {
            const item = input.closest('.service-item');
            const qty = parseFloat(item.querySelector('[name*="quantity_"]').value) || 0;
            const price = parseFloat(item.querySelector('[name*="unit_price_"]').value) || 0;
            const subtotalInput = item.querySelector('[name*="subtotal_"]');
            subtotalInput.value = (qty * price).toFixed(2);
            calculateTotal();
        }

        function calculateTotal() {
            let subtotal = 0;
            document.querySelectorAll('[name*="subtotal_"]').forEach(input => {
                subtotal += parseFloat(input.value) || 0;
            });
            
            const taxPercent = parseFloat(document.getElementById('tax_percent').value) || 0;
            const taxAmount = subtotal * (taxPercent / 100);
            const total = subtotal + taxAmount;
            
            document.getElementById('subtotal').value = subtotal.toFixed(2);
            document.getElementById('tax_amount').value = taxAmount.toFixed(2);
            document.getElementById('total_amount').value = total.toFixed(2);
        }

        function useCustomer() {
            const fetched = {{ fetched_customer | tojson }};
            if (fetched) {
                document.getElementById('customer_name').value = fetched.customer_name || fetched.name || '';
                document.querySelector('[name="contact_person"]').value = fetched.contact_person || '';
                document.querySelector('[name="email"]').value = fetched.email || '';
                document.querySelector('[name="phone"]').value = fetched.phone || fetched.phone_number || '';
                document.querySelector('[name="address"]').value = fetched.address || fetched.billing_address || '';
                document.querySelector('[name="city"]').value = fetched.city || '';
                document.querySelector('[name="state"]').value = fetched.state || fetched.state_province || '';
                document.querySelector('[name="country"]').value = fetched.country || '';
                document.querySelector('[name="postal_code"]').value = fetched.postal_code || fetched.zipcode || fetched.zip || '';
            }
        }

        // Initialize calculations
        document.querySelectorAll('[name*="unit_price_"]').forEach(input => calculateSubtotal(input));
        calculateTotal();
    </script>
</body>
</html>
"""

INVOICE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice Generated - {{ invoice_number }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .card { background: white; border-radius: 15px; padding: 50px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 500px; }
        .icon { font-size: 4rem; margin-bottom: 20px; }
        h1 { color: #27ae60; margin-bottom: 10px; }
        .invoice-number { font-size: 2.5rem; font-weight: bold; color: #E74C3C; background: #2C3E50; color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }
        p { color: #666; margin-bottom: 30px; }
        .btn { padding: 15px 40px; background: #E74C3C; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; transition: background 0.3s; }
        .btn:hover { background: #c0392b; }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✅</div>
        <h1>Invoice Generated!</h1>
        <p>Your invoice has been created successfully.</p>
        <div class="invoice-number">{{ invoice_number }}</div>
        <p>File: {{ filename }}</p>
        <a href="/" class="btn">Create Another Invoice</a>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    next_num = 1
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            try:
                next_num = int(f.read().strip()) + 1
            except:
                pass
    
    return render_template_string(HTML_TEMPLATE,
        customer={},
        services=[{'product': '', 'description': '', 'quantity': 1, 'unit_price': 0, 'subtotal': 0}],
        next_invoice=f"LUX-{next_num:03d}",
        fetched_customer=None
    )


@app.route('/fetch-customer', methods=['POST'])
def fetch_customer():
    api_url = request.form.get('api_url', '').strip()
    
    if not api_url:
        flash('Please enter a URL', 'error')
        return redirect(url_for('index'))
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        customer_data = response.json()
        
        next_num = 1
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r") as f:
                try:
                    next_num = int(f.read().strip()) + 1
                except:
                    pass
        
        return render_template_string(HTML_TEMPLATE,
            customer={},
            services=[{'product': '', 'description': '', 'quantity': 1, 'unit_price': 0, 'subtotal': 0}],
            next_invoice=f"LUX-{next_num:03d}",
            fetched_customer=customer_data
        )
    
    except requests.exceptions.Timeout:
        flash('Request timed out. Please check the URL.', 'error')
    except requests.exceptions.RequestException as e:
        flash(f'Failed to fetch: {str(e)}', 'error')
    except ValueError:
        flash('Invalid response. Expected JSON data.', 'error')
    
    next_num = 1
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            try:
                next_num = int(f.read().strip()) + 1
            except:
                pass
    
    return render_template_string(HTML_TEMPLATE,
        customer={},
        services=[{'product': '', 'description': '', 'quantity': 1, 'unit_price': 0, 'subtotal': 0}],
        next_invoice=f"LUX-{next_num:03d}",
        fetched_customer=None
    )


@app.route('/generate', methods=['POST'])
def generate():
    customer = {
        'customer_name': request.form.get('customer_name', ''),
        'contact_person': request.form.get('contact_person', ''),
        'email': request.form.get('email', ''),
        'phone': request.form.get('phone', ''),
        'address': request.form.get('address', ''),
        'city': request.form.get('city', ''),
        'state': request.form.get('state', ''),
        'country': request.form.get('country', ''),
        'postal_code': request.form.get('postal_code', ''),
    }
    
    services = []
    i = 0
    while True:
        product = request.form.get(f'product_{i}')
        if product is None:
            break
        if product.strip():
            qty = float(request.form.get(f'quantity_{i}', 1) or 1)
            price = float(request.form.get(f'unit_price_{i}', 0) or 0)
            services.append({
                'product': product,
                'description': request.form.get(f'description_{i}', ''),
                'quantity': qty,
                'unit_price': price,
                'subtotal': qty * price
            })
        i += 1
    
    tax_percent = float(request.form.get('tax_percent', 0) or 0)
    payment_terms = request.form.get('payment_terms', 'Net 7')
    payment_method = request.form.get('payment_method', 'Bank Transfer')
    
    # Calculate due date based on payment terms
    days = 7
    if payment_terms == 'Net 3':
        days = 3
    elif payment_terms == 'Net 15':
        days = 15
    elif payment_terms == 'Net 30':
        days = 30
    elif payment_terms == 'Net 45':
        days = 45
    elif payment_terms == 'Net 60':
        days = 60
    elif payment_terms == 'Due on Receipt':
        days = 0
    
    due_date = (datetime.now() + timedelta(days=days)).strftime("%B %d, %Y") if days > 0 else "Due on Receipt"
    
    if not customer['customer_name']:
        flash('Customer Name is required', 'error')
        return redirect(url_for('index'))
    
    if not services:
        flash('At least one service is required', 'error')
        return redirect(url_for('index'))
    
    invoice_num = get_next_invoice_number()
    invoice_num_str = generate_invoice_number(invoice_num)
    
    # Generate PDF
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.units import inch
    
    subtotal = sum(s['subtotal'] for s in services)
    tax_amount = subtotal * (tax_percent / 100)
    total = subtotal + tax_amount
    
    pdf_filename = f"{invoice_num_str}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=40, bottomMargin=40)
    story = []
    
    brand_color = colors.HexColor("#2C3E50")
    accent_color = colors.HexColor("#E74C3C")
    light_bg = colors.HexColor("#ECF0F1")
    
    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=32, textColor=brand_color, spaceAfter=5, alignment=1)
    subtitle_style = ParagraphStyle('Subtitle', fontName='Helvetica', fontSize=12, textColor=accent_color, spaceAfter=20, alignment=1)
    heading_style = ParagraphStyle('Heading', fontName='Helvetica-Bold', fontSize=12, textColor=brand_color, spaceAfter=8)
    normal_style = ParagraphStyle('Normal', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#2C3E50"), spaceAfter=5)
    label_style = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#7F8C8D"), spaceAfter=2)
    footer_style = ParagraphStyle('Footer', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.HexColor("#95A5A6"), alignment=1, spaceAfter=3)
    
    if os.path.exists(LOGO_FILE):
        try:
            logo = Image(LOGO_FILE, width=180, height=70)
            logo.hAlign = 'CENTER'
            story.append(logo)
        except:
            story.append(Paragraph(COMPANY_NAME, title_style))
    else:
        story.append(Paragraph(COMPANY_NAME, title_style))
    
    story.append(Paragraph("INVOICE", subtitle_style))
    
    header_data = [
        [Paragraph("<b>INVOICE #</b>", label_style), Paragraph("<b>DATE</b>", label_style), Paragraph("<b>DUE DATE</b>", label_style)],
        [invoice_num_str, datetime.now().strftime("%B %d, %Y"), due_date]
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
    if customer['customer_name']:
        bill_to.append(Paragraph(f"<b>{customer['customer_name']}</b>", normal_style))
    if customer['contact_person']:
        bill_to.append(Paragraph(f"Contact: {customer['contact_person']}", normal_style))
    if customer['address']:
        bill_to.append(Paragraph(customer['address'], normal_style))
    city_parts = [c for c in [customer['city'], customer['state'], customer['postal_code'], customer['country']] if c]
    if city_parts:
        bill_to.append(Paragraph(", ".join(city_parts), normal_style))
    if customer['email']:
        bill_to.append(Paragraph(customer['email'], normal_style))
    if customer['phone']:
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
            Paragraph(service['product'], normal_style),
            Paragraph(service['description'] or "-", normal_style),
            Paragraph(str(int(service['quantity'])), normal_style),
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
    
    story.append(Paragraph("PAYMENT DETAILS", heading_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"<b>Payment Terms:</b> {payment_terms}", normal_style))
    story.append(Paragraph(f"<b>Due Date:</b> {due_date}", normal_style))
    story.append(Paragraph(f"<b>Payment Method:</b> {payment_method}", normal_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("─" * 60, footer_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(PAYMENT_CLAUSE, footer_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Thank you for your business!", ParagraphStyle('Thanks', fontName='Helvetica', fontSize=10, textColor=brand_color, alignment=1)))
    story.append(Paragraph("theluxeradigital@gmail.com", footer_style))
    
    doc.build(story)
    
    return render_template_string(INVOICE_HTML, invoice_number=invoice_num_str, filename=pdf_filename)


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  LUXERA INVOICE GENERATOR")
    print("="*50)
    print("\n🌐 Web App running at: http://127.0.0.1:5000")
    print("\n📌 How to use:")
    print("   1. Open http://127.0.0.1:5000 in browser")
    print("   2. Enter your customer API URL")
    print("   3. Fill in services and payment details")
    print("   4. Click Generate Invoice")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

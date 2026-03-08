from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luxera Invoice - Create Invoice</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { opacity: 0.8; }
        .card { background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .card h2 { color: #2C3E50; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #ECF0F1; }
        .form-row { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
        .form-group { flex: 1; min-width: 200px; }
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
        .btn-group { display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap; }
        .service-item { background: #F8F9FA; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #E74C3C; }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .service-header h4 { color: #2C3E50; }
        .remove-btn { background: #e74c3c; color: white; padding: 5px 15px; border: none; border-radius: 5px; cursor: pointer; }
        .error-message { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .fetch-section { background: #e8f4fd; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .fetch-section h3 { color: #2C3E50; margin-bottom: 15px; }
        .fetch-section input { flex: 1; padding: 12px; border: 2px solid #3498db; border-radius: 8px; min-width: 200px; }
        .fetch-result { background: white; padding: 15px; border-radius: 8px; margin-top: 15px; }
        .fetch-result p { margin: 5px 0; color: #2C3E50; }
        .required { color: #E74C3C; }
        .data-output { background: #1a1a2e; color: #00ff00; padding: 20px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto; margin-top: 20px; display: none; }
        .data-output.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LUXERA DIGITAL</h1>
            <p>Invoice Data Entry</p>
        </div>

        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}

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
                    <button class="btn btn-success" onclick="useCustomer()" style="margin-top:10px;">Use This Customer</button>
                </div>
                {% endif %}
            </div>
        </div>

        <form id="invoiceForm">
            <div class="card">
                <h2>Customer Details</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Customer Name <span class="required">*</span></label>
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
                                <input type="number" name="quantity_{{ i }}" value="{{ services[i].get('quantity', 1) }}" min="1">
                            </div>
                            <div class="form-group">
                                <label>Unit Price (₹)</label>
                                <input type="number" name="unit_price_{{ i }}" value="{{ services[i].get('unit_price', 0) }}" min="0" step="0.01">
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
                        <input type="number" name="tax_percent" value="0" min="0" max="100">
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
            </div>

            <div class="btn-group" style="justify-content: center;">
                <button type="button" class="btn btn-primary" onclick="generateData()" style="font-size: 1.2rem; padding: 15px 50px;">Generate Invoice Data</button>
            </div>
        </form>

        <div class="card" id="outputCard" style="display: none;">
            <h2>Invoice Data Generated!</h2>
            <p>Copy the data below and paste it in the Luxera Invoice Generator desktop app.</p>
            <div class="data-output" id="dataOutput"></div>
            <div class="btn-group">
                <button type="button" class="btn btn-success" onclick="copyData()">Copy to Clipboard</button>
                <button type="button" class="btn btn-secondary" onclick="downloadData()">Download JSON</button>
            </div>
        </div>

        <p style="text-align: center; color: white; margin-top: 20px; opacity: 0.7;">
            Data will be used in Luxera Invoice Generator desktop app
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
                            <input type="number" name="quantity_${serviceCount - 1}" value="1" min="1">
                        </div>
                        <div class="form-group">
                            <label>Unit Price (₹)</label>
                            <input type="number" name="unit_price_${serviceCount - 1}" value="0" min="0" step="0.01">
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
        }

        function generateData() {
            const form = document.getElementById('invoiceForm');
            const formData = new FormData(form);
            
            const data = {
                customer: {
                    customer_name: formData.get('customer_name') || '',
                    contact_person: formData.get('contact_person') || '',
                    email: formData.get('email') || '',
                    phone: formData.get('phone') || '',
                    address: formData.get('address') || '',
                    city: formData.get('city') || '',
                    state: formData.get('state') || '',
                    country: formData.get('country') || '',
                    postal_code: formData.get('postal_code') || ''
                },
                services: [],
                payment: {
                    tax_percent: parseFloat(formData.get('tax_percent')) || 0,
                    payment_terms: formData.get('payment_terms') || 'Net 7',
                    payment_method: formData.get('payment_method') || 'Bank Transfer'
                }
            };
            
            for (let i = 0; i < serviceCount; i++) {
                const product = formData.get(`product_${i}`);
                if (product) {
                    data.services.push({
                        product: product,
                        description: formData.get(`description_${i}`) || '',
                        quantity: parseFloat(formData.get(`quantity_${i}`)) || 1,
                        unit_price: parseFloat(formData.get(`unit_price_${i}`)) || 0
                    });
                }
            }
            
            if (!data.customer.customer_name) {
                alert('Customer Name is required');
                return;
            }
            if (data.services.length === 0) {
                alert('At least one service is required');
                return;
            }
            
            const jsonStr = JSON.stringify(data, null, 2);
            document.getElementById('dataOutput').textContent = jsonStr;
            document.getElementById('outputCard').style.display = 'block';
            document.getElementById('outputCard').scrollIntoView({ behavior: 'smooth' });
        }

        function copyData() {
            const data = document.getElementById('dataOutput').textContent;
            navigator.clipboard.writeText(data).then(() => {
                alert('Copied to clipboard!');
            });
        }

        function downloadData() {
            const data = document.getElementById('dataOutput').textContent;
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'invoice_data.json';
            a.click();
            URL.revokeObjectURL(url);
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
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE,
        customer={},
        services=[{'product': '', 'description': '', 'quantity': 1, 'unit_price': 0}],
        fetched_customer=None,
        error=None
    )


@app.route('/fetch-customer', methods=['POST'])
def fetch_customer():
    api_url = request.form.get('api_url', '').strip()
    
    if not api_url:
        return render_template_string(HTML_TEMPLATE,
            customer={},
            services=[{'product': '', 'description': '', 'quantity': 1, 'unit_price': 0}],
            fetched_customer=None,
            error="Please enter a URL"
        )
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        customer_data = response.json()
        
        return render_template_string(HTML_TEMPLATE,
            customer={},
            services=[{'product': '', 'description': '', 'quantity': 1, 'unit_price': 0}],
            fetched_customer=customer_data,
            error=None
        )
    
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
            customer={},
            services=[{'product': '', 'description': '', 'quantity': 1, 'unit_price': 0}],
            fetched_customer=None,
            error=f"Failed to fetch: {str(e)}"
        )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

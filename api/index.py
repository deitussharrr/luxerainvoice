from flask import Flask, request, render_template_string, jsonify
import uuid
import os
import json

app = Flask(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    cred = None
    
    # Try environment variable first (for Vercel)
    if os.environ.get('FIREBASE_CREDENTIALS'):
        cred = credentials.Certificate(json.loads(os.environ.get('FIREBASE_CREDENTIALS', '{}')))
    else:
        # Try local file (for local development)
        SERVICE_KEY_PATH = os.path.join(os.path.dirname(__file__), "..", "servicekey.json")
        if not os.path.exists(SERVICE_KEY_PATH):
            SERVICE_KEY_PATH = os.path.join(os.path.dirname(__file__), "servicekey.json")
        if os.path.exists(SERVICE_KEY_PATH):
            cred = credentials.Certificate(SERVICE_KEY_PATH)
    
    if cred and not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        USE_FIREBASE = True
    else:
        db = None
        USE_FIREBASE = False
except Exception as e:
    print(f"Firebase init failed: {e}")
    USE_FIREBASE = False
    db = None

customer_queue = {}


def load_customers():
    if not USE_FIREBASE:
        return {}
    try:
        customers = {}
        docs = db.collection('customers').stream()
        for doc in docs:
            customers[doc.id] = doc.to_dict()
        return customers
    except:
        return {}


def save_customer(customer_id, customer):
    if not USE_FIREBASE:
        return
    try:
        db.collection('customers').document(customer_id).set(customer)
    except:
        pass


customer_list = load_customers()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luxera Invoice - Customer Entry</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .card { background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .card h2 { color: #2C3E50; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #ECF0F1; }
        .form-row { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; }
        .form-group { flex: 1; min-width: 200px; }
        .form-group label { display: block; margin-bottom: 5px; color: #2C3E50; font-weight: 600; font-size: 0.9rem; }
        .form-group input, .form-group textarea { width: 100%; padding: 12px; border: 2px solid #E0E0E0; border-radius: 8px; font-size: 1rem; }
        .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #E74C3C; }
        .form-group textarea { resize: vertical; min-height: 60px; }
        .btn { padding: 12px 30px; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; font-weight: 600; }
        .btn-primary { background: #E74C3C; color: white; width: 100%; font-size: 1.2rem; padding: 15px; }
        .btn-primary:hover { background: #c0392b; }
        .btn-secondary { background: #3498db; color: white; }
        .error-message { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .success-message { background: #d4edda; color: #155724; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .success-message h3 { margin-bottom: 10px; }
        .required { color: #E74C3C; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LUXERA DIGITAL</h1>
            <p>Customer Details Entry</p>
        </div>

        {% if error %}<div class="error-message">{{ error }}</div>{% endif %}

        {% if success %}
        <div class="success-message">
            <h3>✅ Customer Data Sent!</h3>
            <p>Data has been sent to Luxera Invoice Generator desktop app.</p>
            <p style="margin-top:10px;"><a href="/" style="color:#E74C3C;">Add Another Customer</a></p>
        </div>
        {% else %}
        
        <form method="POST" action="/submit">
            <div class="card">
                <h2>Customer Details</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Customer Name <span class="required">*</span></label>
                        <input type="text" name="customer_name" value="{{ customer.get('customer_name', '') }}" required>
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
                    <div class="form-group"><label>City</label><input type="text" name="city" value="{{ customer.get('city', '') }}"></div>
                    <div class="form-group"><label>State/Province</label><input type="text" name="state" value="{{ customer.get('state', '') }}"></div>
                </div>
                <div class="form-row">
                    <div class="form-group"><label>Country</label><input type="text" name="country" value="{{ customer.get('country', '') }}"></div>
                    <div class="form-group"><label>Postal Code</label><input type="text" name="postal_code" value="{{ customer.get('postal_code', '') }}"></div>
                </div>
            </div>

            <button type="submit" class="btn btn-primary">Send to Desktop App</button>
        </form>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, customer={}, error=None, success=False)


@app.route('/submit', methods=['POST'])
def submit():
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
    
    if not customer['customer_name']:
        return render_template_string(HTML_TEMPLATE, customer=customer, error="Customer Name is required", success=False)
    
    customer_id = str(uuid.uuid4())[:8]
    customer_queue[customer_id] = customer
    customer_list[customer_id] = customer
    save_customer(customer_id, customer)
    
    return render_template_string(HTML_TEMPLATE, customer={}, error=None, success=True)


@app.route('/api/list')
def list_customers():
    global customer_list
    customer_list = load_customers()
    customers = [{'id': k, 'name': v.get('customer_name', 'Unknown')} for k, v in customer_list.items()]
    return jsonify({'success': True, 'customers': customers})


@app.route('/api/customer/<customer_id>')
def get_customer(customer_id):
    global customer_list
    customer_list = load_customers()
    if customer_id in customer_list:
        return jsonify({'success': True, 'data': customer_list[customer_id]})
    return jsonify({'success': False})


@app.route('/api/latest')
def get_latest():
    if customer_queue:
        customer_id = list(customer_queue.keys())[-1]
        data = customer_queue.pop(customer_id)
        return jsonify({'success': True, 'id': customer_id, 'data': data})
    return jsonify({'success': False})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)

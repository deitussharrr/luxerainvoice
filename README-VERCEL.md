# Luxera Invoice Generator - Vercel Deployment

## Quick Deploy

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/import/project?template=https://github.com/vercel/vercel/tree/main/python-flask)

1. Push to GitHub
2. Import at https://vercel.com/new
3. Add environment variable:
   - Go to Settings → Environment Variables
   - Add: `INVOICE_COUNTER` = starting number (e.g., `0` or `100`)

## Setup

```bash
# Clone your repo
git clone https://github.com/yourusername/luxera-invoice.git
cd luxera-invoice

# Install dependencies
pip install -r requirements.txt

# Test locally
python api/index.py
```

## Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `INVOICE_COUNTER` | Starting invoice number | `0` or `100` |

## Website

Will be available at: **https://luxerainvoice.vercel.app**

## Features

- Fetch customer from API URL
- Multiple services/products
- Tax calculation
- Payment terms (Net 3/7/15/30/45/60)
- Payment methods (Bank Transfer, Cash, UPI, etc.)
- Auto-incrementing invoice numbers
- Professional PDF generation

## API Response Format

Your customer API should return JSON like:

```json
{
  "customer_name": "John Doe",
  "contact_person": "Jane Doe",
  "email": "john@example.com",
  "phone": "+91 9876543210",
  "address": "123 Main Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "country": "India",
  "postal_code": "400001"
}
```

## Files

- `api/index.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel configuration
- `luxeralogo.png` - Company logo (upload to Vercel)

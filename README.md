# Luxera Invoice Generator

A Python desktop application for generating PDF invoices using Tkinter dialogs.

## Requirements

Install the required dependency:

```bash
pip install reportlab
```

## Files

- `invoice_generator.py` - Main application script
- `luxera_logo.png` - Company logo (place in same directory)
- `invoice_counter.txt` - Auto-generated counter file

## Usage

1. Ensure `reportlab` is installed: `pip install reportlab`
2. Place `luxera_logo.png` in the same directory (optional)
3. Run: `python invoice_generator.py`

## Features

- Interactive Tkinter dialog for invoice details
- Auto-incrementing invoice numbers (stored in `invoice_counter.txt`)
- Automatic calculation of subtotal, tax, and total
- PDF generation with:
  - Luxera logo at top
  - Company name "LUXERA"
  - Invoice number, client name, service details
  - Price breakdown
  - Payment clause: "All payment must be made within 3 days of product submission."
- Output: `LUX-XXX.pdf`

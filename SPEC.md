# Luxera Invoice Generator - Specification

## Project Overview
- **Project name**: Luxera Invoice Generator
- **Type**: Standalone Python desktop application
- **Core functionality**: Generate PDF invoices with auto-incrementing numbers using Tkinter dialogs
- **Target users**: Luxera company staff

## UI/UX Specification

### Layout Structure
- Single main window with form inputs
- Input fields: Client name, Product/Service name, Description, Price, Tax %
- Generate Invoice button
- Confirmation popup after generation

### Visual Design
- Standard Tkinter widgets
- Form labels and entry fields in vertical layout
- Primary action button with distinct styling

### Components
- Entry fields for text inputs
- Spinbox or Entry for price (numeric)
- Spinbox or Entry for tax percentage (0-100)
- Button to generate invoice

## Functionality Specification

### Core Features
1. **Invoice Number Counter**: Persistent counter stored in `invoice_counter.txt`
2. **Form Inputs**:
   - Client name (required)
   - Product/Service name (required)
   - Description (required)
   - Price (required, numeric)
   - Tax percentage (optional, default 0)
3. **Calculations**:
   - Subtotal = Price
   - Tax amount = Price × (Tax% / 100)
   - Total = Subtotal + Tax
4. **PDF Generation**:
   - Use reportlab library
   - Include logo at top (luxera_logo.png)
   - Company name "LUXERA" prominently displayed
   - Invoice number, client name, service details, price breakdown
   - Payment clause at bottom
5. **Output**: Save as `LUX-XXX.pdf` where XXX is incremented invoice number

### User Interactions
1. User fills in invoice details via dialog
2. Click "Generate Invoice" button
3. Program validates inputs
4. Calculates totals
5. Generates PDF
6. Shows confirmation popup with file path

### Data Handling
- Invoice counter stored in `invoice_counter.txt` (simple integer)
- PDF saved in same directory as script

### Edge Cases
- Empty required fields → show error
- Invalid price/tax → show error
- Logo file missing → generate without logo or show placeholder

## Acceptance Criteria
- [ ] Tkinter dialog collects all required inputs
- [ ] Invoice number auto-increments and persists
- [ ] Calculations are accurate
- [ ] PDF generates with all required fields
- [ ] Logo displays at top if file exists
- [ ] Payment clause appears at bottom
- [ ] Confirmation popup shows after generation
- [ ] File saves as LUX-XXX.pdf format

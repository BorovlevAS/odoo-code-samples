# Warranty Certificate for Sale Order

This module automates the generation and distribution of warranty certificates for products sold through Odoo Sale Orders. It creates digital warranty certificates with unique numbers, tracks warranty information, and optionally sends certificates to customers via SMS.

> **Note:** All client-specific modules and internal dependencies have been anonymized. Only generic, reusable logic is included.

---

## Features

### Warranty Certificate Management

- **Automatic generation** of warranty certificates upon delivery completion
- **Unique numbering** using configurable sequences
- **Digital certificates** accessible via public URLs
- **Product-level configuration** with adjustable warranty duration
- **Serial number extraction** from stock moves

### Certificate Information

Each certificate includes:
- Certificate number
- Product name and characteristics
- Serial numbers
- Warranty duration (in months)
- Warranty start date
- Company information

### Automatic Workflow

1. Stock picking is validated (delivery completed)
2. Warranty certificates generated for warranted products
3. Optional SMS notification sent to customer
4. Customer views certificates via public URLs

### Sales Team Integration

- Team-level control over warranty generation
- Enable/disable warranty flow per sales channel

### Company Settings

- Global toggle for automatic SMS sending
- Customizable SMS template

---

## Technical Implementation

### Models

#### `warranty.certificate`

Main model storing certificate data:

```python
{
    'name': '000000001',  # Auto-generated
    'warranty_date': '2025-11-18',
    'so_line_id': sale_order_line_id,
    'product_name': 'Product Name',
    'product_char': 'Product Characteristics',
    'serial_no': 'SN12345, SN12346',
    'warranty_duration': 12,
}
```

### Extended Models

#### `product.template`
- `is_warranty`: Enable warranty certificates
- `warranty_duration`: Duration in months

#### `sale.order`
- `warranty_generated`: Computed flag
- `generate_warranty()`: Manual creation
- `send_warranty()`: Manual SMS sending

#### `sale.order.line`
- `warranty_id`: Many2one link to certificate
- `action_view_warranty()`: Opens certificate in browser

#### `stock.picking`
- Hook in `_action_done()` to trigger warranty generation
- Sends SMS if enabled

#### `crm.team`
- `is_send_warranty`: Enable/disable per team

#### `res.company` & `res.config.settings`
- `send_warranty_enabled`: Company-level toggle

---

## Controller

Public route for certificate display:

```python
@http.route('/warranty/<int:rec_id>', type='http', auth='public')
def warranty_report_html(self, rec_id):
    # Returns HTML warranty certificate
```

---

## Data Files

### Sequence
- 9-digit, gapless numbering

### SMS Template
- Jinja2-based template
- Includes links to all certificates per order

---

## Configuration

### Product Setup
1. Open product form
2. Enable "Warranty needed"
3. Set duration

### Sales Team Setup
1. Sales → Configuration → Sales Teams
2. Enable "Send Warranty Certificate"

### Company Setup
1. Settings → General Settings
2. Enable automatic sending of warranty SMS

### SMS Setup
Requires `custom_sms_gateway_base` (anonymized dependency).

---

## Usage

### Automatic Flow
1. Create sale order with warranted products
2. Confirm order
3. Validate delivery picking
4. Certificates generated automatically
5. SMS sent (if enabled)

### Manual Operations

**Generate Certificates:**
```python
order.generate_warranty()
```

**Send SMS:**
```python
order.send_warranty()
```

**View Certificate:**
- Click "View Warranty" on sale order line

### Customer Access

Customers receive SMS with links, e.g.:
```
https://yourdomain.com/warranty/1
```
Certificates accessible without authentication.

---

## API Examples

### Programmatic Generation

```python
order = env['sale.order'].browse(order_id)
order.generate_warranty()
order.send_warranty()
```

### Manual Creation

```python
env['warranty.certificate'].create({
    'so_line_id': line_id,
    'warranty_date': fields.Date.today(),
    'product_name': 'Custom Product',
    'product_char': 'Size: Large, Color: Blue',
    'serial_no': 'ABC123',
    'warranty_duration': 24,
})
```

---

## Dependencies

- `sale`
- `sale_stock`
- `biko_base_module`
- `custom_sms_gateway_base`
- `sales_team`

---

## Reports

QWeb template:
- `warranty_certificate_report.xml`
- Printable HTML
- Supports company branding

---

## Author

- **BIKO Solutions**
- **Artem Borovlev**

## License

LGPL-3

## Version

14.0.1.0.0

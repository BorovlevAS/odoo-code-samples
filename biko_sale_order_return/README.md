# Sale Order Return

A comprehensive solution for managing product returns, refunds, and exchanges in Odoo. This module implements flexible return workflows with automatic stock movements, credit note generation, quantity tracking, and support for multiple return scenarios.

> **Note:**  
> This module is based on functionality originally developed for a commercial Odoo 14 environment. All client-specific dependencies have been anonymized. Only generic, reusable logic is published here.

---

## Features

### Multiple Return Types

The module supports four distinct return operation types:

1. **Full Return** (`full_return`)
   - Complete stock + financial reversal
   - Immediate creation of return stock moves
   - Credit notes generated after return validation
   - Two-stage flow: receive goods → generate credit notes

2. **Financial Return** (`financial_return`)
   - Financial reversal only
   - For invoiced but undelivered products
   - Cancels pending deliveries
   - Generates credit notes immediately

3. **Stock Return** (`stock_return`)
   - Physical return without financial impact
   - Suitable for warranty or quality-related returns
   - Stock movements only

4. **Product Exchange** (`exchange`)
   - Customer returns product and receives a replacement
   - Creates both return and replacement pickings
   - Triggers procurement for replacement items
   - Preserves original pricing and discounts

---

## Advanced Quantity Tracking

### Returnable Quantity System

Implements a recursive `qty_returnable` field on `stock.move`:

```python
qty_returnable = quantity_done - sum(returned_move_ids.qty_returnable)
```

**Key Features:**
- Prevents over-returns
- Correct handling of chained returns
- Accurate tracking of partial returns
- Efficient recalculation via hooks

### Return Line Quantity Tracking

Each return line tracks:
- `quantity_return`: Requested return quantity
- `returned_qty`: Physically returned quantity
- `qty_returned_inv`: Financially reverted quantity

---

## Automatic Document Generation

### Stock Movements

**Return Pickings:**
- Generated from original delivery pickings
- Customer → warehouse routing
- Maintains traceability through linked moves
- Auto-selected picking types

**Exchange Deliveries:**
- Replacement deliveries generated via procurement
- Preserves delivery preferences and shipping addresses

### Credit Notes

- Linked to original invoices
- Preserves taxes, discounts, analytic data
- Supports partial returns
- Auto-reconciliation where applicable

---

## State Management

### Return Order States
- **Draft** – Editable
- **Waiting for Stock** – Stock operations in progress
- **Done** – All operations completed
- **Cancelled** – Return cancelled with rollback

### Line-Level States
- Each line has its own state
- Supports mixed progress scenarios
- Aggregate order state is auto-computed

---

## Validation and Safety Checks

Before validation, system checks:
- Returnable quantities
- Operation type compatibility
- Stock availability
- Zero-quantity lines

Cancellation protections:
- Prevents cancelling partially processed returns
- Optional warning wizard
- Draft documents reversed automatically

---

## Technical Implementation

### `sale.stock.return`

```python
_name = "sale.stock.return"
_inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
```

**Key Fields:**
- `operation_type`
- `sale_order_id`
- `partner_id`
- `contract_id`
- `location_id`
- `procurement_group_id`
- `state`

**Key Methods:**
- `generate_stock_moves()`
- `generate_account_moves()`
- `action_validate()`
- `_action_cancel()`

### `sale.stock.return.line`

Tracks quantities and amounts.

**Quantity Fields:**
- `quantity_return`
- `returned_qty`
- `qty_returned_inv`

**Amount Fields:**
- `price_subtotal`, `price_total`, `price_tax`
- `discount_total`

**Methods:**
- `_get_returnable_move_ids()`
- `_get_acc_returnable_ids()`
- `_prepare_move_default_values()`
- `_prepare_account_move_line_vals()`

### Related Model Extensions

- **`sale.order`**: smart button, quick return action
- **`sale.order.line`**: default line preparation
- **`stock.move`**: returnability tracking
- **`account.move`** & **`account.move.line`**: traceability links

---

## Configuration

### Security Groups
- **Return Order User** – create/manage returns
- **Return Order Manager** – full access

### Sequences
- Numbering: `sale.return.order.seq`
- No gaps, per company

### Default Locations
- Source: customer location
- Destination: original delivery location or configured value

---

## User Interface

### Sale Order Enhancements
- Smart button showing related returns
- "Create Return Order" action

### Return Order Form
- Validate / Cancel / Back to Draft
- Smart buttons for invoices, stock moves, sale orders
- "Fill Products" / "Add Products" helpers

### Wizards

**Add Products Wizard:**
```python
wizard = env['add.so.lines.wizard'].create({
    'return_order_id': return_order.id,
})
```

**Cancel Warning Wizard:**
- Displays impact before cancellation

---

## Dependencies

- `sale`
- `account`
- `stock`
- `custom_contract_module` (anonymized)
- `custom_accounting_module` (anonymized)

---

## Hooks

### Pre-init

```python
def pre_init_hook(cr):
    # Create qty_returnable via SQL
    # Initialize values
```

### Post-init

```python
def post_init_hook(cr, registry):
    # Recompute qty_returnable recursively
```

---

## Advanced Features

### Discount Preservation
- Keeps original discounts
- Supports mixed discount scenarios

### Tax Handling
- Preserves tax configuration
- Correct handling of partial returns

---

## Author

**Artem Borovlev**

## License

LGPL-3

## Version

14.0.2.1.0
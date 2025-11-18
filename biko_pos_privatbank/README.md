# POS PrivatBank Integration

This module extends PrivatBank terminal integration for Odoo POS and Sale Order systems, providing enhanced functionality for card payment processing through PrivatBank payment terminals.

> **Note:** All client-specific dependencies have been anonymized. Only generic, reusable integration logic is included.

---

## Features

### Payment Terminal Integration
- **Socket-based communication** with PrivatBank terminals
- Supports **Purchase** and **Refund** operations
- Real-time processing with hardware terminals
- Automatic transaction logging and tracking

### Enhanced Payment Data
Captured details include:
- Masked PAN (card number)
- Acquirer bank name
- Authorization code
- RRN (Retrieval Reference Number)
- Payment system (Visa, MasterCard, etc.)
- Terminal ID
- Receipt number

### Multi-Subsystem Support
- **Sale Orders** – card payment processing
- **Return Orders** – refund handling with RRN lookup

### Transaction Management
- Automatic transaction record creation
- Structured logging of all requests/responses
- Status tracking (`waitingCard`, `done`, `retry`)
- Error detection and retry mechanism

---

## Technical Implementation

### Core Class: `PrivatbankTerminal`

Responsible for socket communication and API protocol handling.

```python
terminal = PrivatbankTerminal(
    terminal_ip="192.168.1.100:8080",
    env=self.env,
    subsystem="SALE"  # or "POS"
)

result = terminal.send_payment_request(
    amount=100.50,
    order_id=order_id,
    payment_type_id=payment_type_id,
    session_id=session_id
)
```

### Extended Models

- `privatbank_terminal.transaction` – transaction log
- `sale.order` – terminal payment metadata
- `sale.stock.return` – return order payment integration
- `sale.order.checkbox.wizard` – payment wizard for sale orders
- `return.order.checkbox.wizard` – refund wizard for returns

---

## Payment Flows

### 1. Purchase Flow
1. Create payment request with amount and order info
2. Send request through socket to terminal
3. Terminal processes customer card
4. Receive and parse result
5. Store transaction details

### 2. Refund Flow
1. Retrieve original transaction RRN
2. Send refund request with negative amount
3. Terminal processes refund
4. Log new refund transaction

---

## Configuration

### Prerequisites
- PrivatBank payment terminal with LAN access
- Terminal IP and port (format `IP:PORT`)
- Python dependency: `ftfy` for encoding fixes

### Setup Steps
1. Install the module
2. Configure POS payment method:
   - `use_payment_terminal = 'privatbank'`
   - Fill in terminal IP and port

---

## Dependencies

- `custom_pos_module` (anonymized)
- `biko_sale_order_pos` (POS + Sale Order integration)
- External Python library: `ftfy`

---

## Usage Examples

### Sale Order Payment
```python
# Payment is executed through the wizard
# Terminal request is sent automatically
# Transaction entries are logged
```

### Refund in Return Order
```python
# Refund wizard fetches original RRN
# Refund is submitted to terminal
# Response logged as refund transaction
```

---

## Error Handling

The module detects and logs:
- Connection timeouts
- Terminal busy responses
- Data parsing errors
- Empty/invalid response packets
- Unexpected protocol violations

Errors are logged and returned with user-friendly messages.

---

## Author
- **BIKO Solutions**
- **Artem Borovlev**

## License
LGPL-3

## Version
14.0.1.0.0

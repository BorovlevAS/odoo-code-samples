# Checkbox Integration Extension Module

This module extends the base Checkbox integration in Odoo by adding dual-mode support: **local Checkbox KassaManager** (self-hosted service) and **Checkbox Cloud API**. It provides a unified API wrapper that automatically adapts requests to the selected mode.

> **Note:**  
> All client-specific dependencies and internal modules have been anonymized.  
> Only generic, reusable functionality is included.

---

## Features

### Dual-Mode Operation

- **Checkbox Kassa Mode**
  - Direct communication with local desktop application
  - No authentication required
  - Customizable IP and port
  - Works offline

- **Checkbox Cloud API**
  - Production and Development endpoints
  - Token-based cashier authentication
  - License key validation
  - Full feature set of Checkbox cloud service

- **Unified API Interface**
  - All actions work identically regardless of selected mode
  - Automatic request translation for each mode

---

## Mode-Specific Configuration

### Checkbox Kassa Mode
- IP address (default: `127.0.0.1`)
- Port for local KassaManager
- No login/sign-in process
- Lightweight request/response format

### Checkbox Cloud API Mode
- `https://api.checkbox.in.ua` (prod)
- `https://dev-api.checkbox.in.ua` (dev)
- Cashier login/password
- Access tokens
- License key

---

## Automatic API Translation

The module automatically converts API calls based on the selected mode:

- Nested → flat payload transformation
- URL mapping (cloud vs local endpoints)
- Auth headers (token / no-auth)
- Different shift endpoints
- Different report endpoints

Example — product line conversion:

```json
# Cloud API
{
    "good": {"code": "123", "name": "Product", "price": 10000},
    "quantity": 1000,
    "tax": [20]
}

# Auto-converted for KassaManager
{
    "code": "123",
    "name": "Product",
    "price": 10000,
    "quantity": 1000,
    "taxes": [20]
}
```

---

## Technical Implementation

### Extended Models

#### `pos.config`

```python
checkbox_mode = fields.Selection([
    ('prod', 'Production'),
    ('dev', 'Development'),
    ('checkbox_kassa', 'Checkbox Kassa'),
])
checkbox_url = fields.Char()
checkbox_port = fields.Integer()
```

URL is auto-computed depending on the mode.

---

### `CheckboxAPI` Wrapper Class

Handles all communication with Checkbox services.

```python
class CheckboxAPI:
    def __init__(self, api_url, api_port, cb_license, mode, access_token=None):
        self.mode = mode
        if mode == "checkbox_kassa":
            api_url = f"{api_url}:{api_port}"
```

Supports:

- cashier sign-in/out  
- shift creation / closing  
- receipt registration  
- receipt info  
- X / Z reports  

---

## API Endpoints

### Cashier Operations

Cloud:
```
POST /api/v1/cashier/signin
```

Kassa:
```
# Bypassed
{"ok": true}
```

### Shift Operations

Cloud:
```
POST /api/v1/shifts
POST /api/v1/shifts/close
```

Kassa:
```
POST /api/v1/shift/open
POST /api/v1/shift/close
```

### Reports

Cloud:
```
POST /api/v1/reports
GET /api/v1/reports/{id}/text
```

Kassa:
```
POST /api/v1/shift/xreport/txt
```

---

## Configuration

### For Checkbox Kassa (Local)

1. Install KassaManager  
2. Configure POS:
   - Mode: “Checkbox Kassa”
   - IP: 127.0.0.1 (or custom)
   - Port: KassaManager port  

### For Checkbox Cloud API

1. Select mode: Production / Development  
2. Provide license key  
3. Enter cashier credentials  

---

## Usage Examples

### Cloud Mode

```python
api = CheckboxAPI(
    api_url="https://api.checkbox.in.ua",
    api_port=0,
    cb_license="LICENSE",
    mode="prod",
)
signin = api.cashier_signin("login", "password")
api.access_token = signin["access_token"]
api.shift_create()
```

### Kassa Mode

```python
api = CheckboxAPI(
    api_url="127.0.0.1",
    api_port=8484,
    cb_license="",
    mode="checkbox_kassa",
)
api.shift_create()  # No authentication required
```

### Register Receipt

```python
payload = {"goods": [...], "payments": [...], "discounts": []}
api.register_sell_return(payload)
```

---

## Error Handling

All network operations handled with detailed logging:

```python
try:
    result = api.send_request(...)
except requests.exceptions.RequestException as e:
    raise ValidationError(f"Request error: {e}")
```

---

## Advantages

- Works with both old and new Checkbox infrastructures  
- Unified interface → no code duplication  
- Offline-mode via KassaManager  
- Easy migration path to cloud-only setup  

---

## Dependencies

- `checkbox_integration` (base module)

*All internal/custom modules replaced by generic names.*

---

## Author

**Artem Borovlev**

## License

LGPL-3  
Version: 14.0.1.1.0
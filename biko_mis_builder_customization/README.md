# MIS Builder Customization

This module extends the standard Odoo MIS Builder by adding fiscal-year-based reporting logic and custom calculation modes.

---

## Features

- Introduces a new calculation mode:
  - **f** — fiscal year end balance for any account

- Enhances the `AccountingExpressionProcessor` to support fiscal-year-aware evaluations

- Implements monkey patching to extend MIS Builder without modifying core files

---

## Usage

After installation, you can use the new mode in MIS Builder expressions:

- ``balf[...]`` — Calculates balance from the start of the fiscal year to the reporting date

This works similarly to existing modes (`bal`, `deb`, `crd`) but applies fiscal year boundaries.

---

## Technical Implementation

The module patches three key methods of `AccountingExpressionProcessor`:

1. **`parse_expr`** — extended regex pattern to detect new modes
2. **`do_queries`** — updated query logic for fiscal-year-based calculations
3. **`get_aml_domain_for_dates`** — additional domain handling for fiscal year date ranges

---

## Installation

1. Install the module normally
2. Patches are applied automatically on load
3. All patches are safely removed on uninstall

---

## Author

- **BIKO Solutions**
- **Artem Borovlev**

## License
LGPL-3
================================
BIKO: MIS Builder Customization
================================

This module extends the standard MIS Builder functionality by adding fiscal year-based reporting modes.

Features
========

* Adds new calculation modes for MIS Builder reports:
  
  - **f** (end fiscal year): Calculates end balances for the fiscal year for any account

* Enhances the Accounting Expression Processor with fiscal year-aware logic

* Uses monkey patching to extend core MIS Builder methods without modifying the original module

Usage
=====

After installation, you can use the new modes in MIS Builder report expressions:

* ``balf[...]`` - Balance calculated from the start of the fiscal year to the reporting date

These modes work similarly to standard modes (bal, deb, crd) but with fiscal year boundaries.

Technical Implementation
========================

The module patches three key methods of ``AccountingExpressionProcessor``:

1. ``parse_expr`` - Extended regex pattern to recognize new modes
2. ``do_queries`` - Modified query logic for fiscal year calculations
3. ``get_aml_domain_for_dates`` - Additional domain logic for fiscal year date ranges

Installation
============

1. Install the module
2. Hooks automatically apply patches on module load
3. Patches are removed on module uninstallation

Author
======

* BIKO Solutions
* Artem Borovlev

License
=======

LGPL-3

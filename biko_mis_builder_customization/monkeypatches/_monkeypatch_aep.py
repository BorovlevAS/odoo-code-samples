import re
from collections import defaultdict

from odoo.addons.mis_builder.models.accounting_none import AccountingNone
from odoo.addons.mis_builder.models.aep import AccountingExpressionProcessor
from odoo.models import expression
from odoo.tools.float_utils import float_is_zero

AccountingExpressionProcessor._ACC_RE = re.compile(
    r"(?P<field>\bbal|\bpbal|\bnbal|\bcrd|\bdeb)"
    r"(?P<mode>[piseuf])?"
    r"\s*"
    r"(?P<account_sel>_[a-zA-Z0-9]+|\[.*?\])"
    r"\s*"
    r"(?P<ml_domain>\[.*?\])?"
)
AccountingExpressionProcessor.MODE_FROM_YEAR_START = "ify"
AccountingExpressionProcessor.MODE_END_FISCAL_YEAR = "f"


def parse_expr(self, expr: str):

    if (
        not self.env["ir.module.module"]
        .sudo()
        .search_count(
            [
                ("name", "=", "biko_mis_builder_customization"),
                ("state", "=", "installed"),
            ]
        )
    ):
        return type(self)._origin_parse_expr(self, expr)

    for mo in self._ACC_RE.finditer(string=expr):
        _field, mode, acc_domain, ml_domain = self._parse_match_object(mo=mo)
        if mode == self.MODE_END and self.smart_end:
            modes = [self.MODE_INITIAL, self.MODE_VARIATION, self.MODE_END]
        elif mode == self.MODE_END_FISCAL_YEAR and self.smart_end:
            modes = [
                self.MODE_FROM_YEAR_START,
                self.MODE_VARIATION,
                self.MODE_END_FISCAL_YEAR,
            ]
        else:
            modes = [
                mode,
            ]
        for mode in modes:
            key = (ml_domain, mode)
            self._map_account_ids[key].add(acc_domain)


def do_queries(
    self,
    date_from,
    date_to,
    additional_move_line_filter=None,
    aml_model=None,
):
    if (
        not self.env["ir.module.module"]
        .sudo()
        .search_count(
            [
                ("name", "=", "biko_mis_builder_customization"),
                ("state", "=", "installed"),
            ]
        )
    ):
        return type(self)._origin_do_queries(
            self,
            date_from,
            date_to,
            additional_move_line_filter,
            aml_model,
        )

    if not aml_model:
        aml_model = self.env["account.move.line"]
    else:
        aml_model = self.env[aml_model]
    aml_model = aml_model.with_context(active_test=False)
    company_rates = self._get_company_rates(date=date_to)
    self._data = defaultdict(dict)
    domain_by_mode = {}
    ends = []
    for key in self._map_account_ids:
        domain, mode = key
        if mode in (self.MODE_END, self.MODE_END_FISCAL_YEAR) and self.smart_end:
            ends.append((domain, mode))
            continue
        if mode not in domain_by_mode:
            domain_by_mode[mode] = self.get_aml_domain_for_dates(
                date_from=date_from, date_to=date_to, mode=mode
            )
        dom = list(domain) + domain_by_mode[mode]
        dom.append(("account_id", "in", self._map_account_ids[key]))
        if additional_move_line_filter:
            dom.extend(additional_move_line_filter)
        accs = aml_model.read_group(
            dom,
            ["debit", "credit", "account_id", "company_id"],
            ["account_id", "company_id"],
            lazy=False,
        )
        for acc in accs:
            rate, _dp = company_rates[acc["company_id"][0]]
            debit = acc["debit"] or 0.0
            credit = acc["credit"] or 0.0
            if mode in (
                self.MODE_INITIAL,
                self.MODE_FROM_YEAR_START,
                self.MODE_UNALLOCATED,
            ) and float_is_zero(value=debit - credit, precision_digits=self.dp):
                continue
            self._data[key][acc["account_id"][0]] = (debit * rate, credit * rate)
    for key in ends:
        domain, mode = key
        initial_data = self._data[(domain, self.MODE_INITIAL)]

        if mode == self.MODE_END_FISCAL_YEAR:
            initial_data = self._data[(domain, self.MODE_FROM_YEAR_START)]

        variation_data = self._data[(domain, self.MODE_VARIATION)]
        account_ids = set(initial_data.keys()) | set(variation_data.keys())
        for account_id in account_ids:
            di, ci = initial_data.get(account_id, (AccountingNone, AccountingNone))
            dv, cv = variation_data.get(account_id, (AccountingNone, AccountingNone))
            self._data[key][account_id] = (di + dv, ci + cv)


def get_aml_domain_for_dates(self, date_from, date_to, mode):
    if (
        not self.env["ir.module.module"]
        .sudo()
        .search_count(
            [
                ("name", "=", "biko_mis_builder_customization"),
                ("state", "=", "installed"),
            ]
        )
    ):
        return type(self)._origin_get_aml_domain_for_dates(
            self, date_from, date_to, mode
        )

    domain = []

    if mode == self.MODE_VARIATION:
        domain = [("date", ">=", date_from), ("date", "<=", date_to)]
    elif mode in (
        self.MODE_INITIAL,
        self.MODE_END,
        self.MODE_FROM_YEAR_START,
        self.MODE_END_FISCAL_YEAR,
    ):
        fy_date_from = self.companies[0].compute_fiscalyear_dates(
            current_date=date_from
        )["date_from"]
        if mode in (self.MODE_FROM_YEAR_START, self.MODE_END_FISCAL_YEAR):
            domain = [("date", ">=", fy_date_from)]
        else:
            domain = [
                "|",
                ("date", ">=", fy_date_from),
                ("account_id.user_type_id.include_initial_balance", "=", True),
            ]
        if mode in (self.MODE_INITIAL, self.MODE_FROM_YEAR_START):
            domain.append(("date", "<", date_from))
        elif mode in (self.MODE_END, self.MODE_END_FISCAL_YEAR):
            domain.append(("date", "<=", date_to))
    elif mode == self.MODE_UNALLOCATED:
        fy_date_from = self.companies[0].compute_fiscalyear_dates(
            current_date=date_from
        )["date_from"]
        domain = [
            ("date", "<", fy_date_from),
            ("account_id.user_type_id.include_initial_balance", "=", False),
        ]
    return expression.normalize_domain(domain)


def _get_patchable_methods():
    return [
        {
            "class": AccountingExpressionProcessor,
            "method_name": "parse_expr",
            "new_method": parse_expr,
        },
        {
            "class": AccountingExpressionProcessor,
            "method_name": "do_queries",
            "new_method": do_queries,
        },
        {
            "class": AccountingExpressionProcessor,
            "method_name": "get_aml_domain_for_dates",
            "new_method": get_aml_domain_for_dates,
        },
    ]

from typing import List, Tuple

from odoo import api, fields, models


class PrivatbankTerminalTransaction(models.Model):
    _inherit = "privatbank_terminal.transaction"

    @api.model
    def _select_target_model(self) -> List[Tuple[str, str]]:
        """
        Returns a list of tuples representing target models and their descriptions.

        Each tuple contains:
            - The model name as a string.
            - The model description as a string.

        Returns:
            List[Tuple[str, str]]: A list of tuples with model names and descriptions.
        """
        return [
            ("pos.order", "POS Order"),
            ("sale.order", "Sale Order"),
            ("sale.stock.return", "Sale Stock Return"),
        ]

    order_ref = fields.Reference(selection="_select_target_model")
    so_payment_type_id = fields.Many2one(comodel_name="so.payment.type")

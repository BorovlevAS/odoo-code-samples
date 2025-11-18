import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from odoo import models

_logger = logging.getLogger(__name__)

OdooRecordset = Union["models.BaseModel", Any]


class SaleStockReturn(models.Model):
    _inherit = "sale.stock.return"

    def _get_payment_terminal_data(
        self,
        payment_type_id: OdooRecordset,
        pos_session_id: Optional[OdooRecordset] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves payment terminal data for a given payment type and POS session.
        This method extends the base implementation to include additional data
        from the PrivatBank terminal transaction.
        Args:
            payment_type_id (OdooRecordset): The payment type recordset.
            pos_session_id (Optional[OdooRecordset], optional): The POS session recordset. Defaults to None.
        Returns:
            Dict[str, Any]: A dictionary containing payment terminal data, including card mask, bank name,
                            authorization code, RRN, payment system, terminal ID, and receipt number.
        Raises:
            Exception: If there is an error parsing the transaction data.
        """

        payment_data: Dict[str, Any] = super()._get_payment_terminal_data(
            payment_type_id=payment_type_id,
            pos_session_id=pos_session_id,
        )

        domain: List[Tuple[str, str, Any]] = [
            ("order_ref", "=", f"{self._name},{self.id}"),
            ("so_payment_type_id", "=", payment_type_id.id),
        ]

        if pos_session_id:
            domain.append(("session_id", "=", pos_session_id.id))

        transaction: OdooRecordset = self.env["privatbank_terminal.transaction"].search(
            domain
        )

        try:
            data: Dict[str, Any] = json.loads(transaction.received_data)  # type: ignore
            payment_params: Dict[str, Any] = data.get("params", {})  # type: ignore
            payment_data.update(
                {
                    "card_mask": payment_params.get("pan"),
                    "bank_name": payment_params.get("bankAcquirer"),
                    "auth_code": payment_params.get("approvalCode"),
                    "rrn": payment_params.get("rrn"),
                    "payment_system": payment_params.get("paymentSystem"),
                    "terminal": payment_params.get("terminalId"),
                    "receipt_no": payment_params.get("invoiceNumber"),
                }
            )
            return payment_data
        except Exception:
            _logger.exception("Error parsing data")
            return payment_data

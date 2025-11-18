from typing import Any, Dict, Literal, Union

from odoo import _, models
from odoo.exceptions import ValidationError

from .privat_terminal_api import PrivatbankTerminal

OdooRecordset = Union["models.BaseModel", Any]


class ReturnOrderCheckbox(models.TransientModel):
    _inherit = "return.order.checkbox.wizard"

    def terminal_send_payment(self) -> bool:
        """
        Sends payment requests to the PrivatBank terminal for each payment line in the order.

        This method overrides the `terminal_send_payment` method from the superclass. It first calls the
        superclass method and checks its result. If the result is not successful, it returns the result
        immediately. Otherwise, it iterates through the payment lines and sends payment requests to the
        PrivatBank terminal for each applicable payment line.

        Returns:
            bool: The result of the payment process.

        Raises:
            ValidationError: If the terminal returns a "retry" status with an error message.
        """
        result: bool = super().terminal_send_payment()

        if not result:
            return result

        payment: OdooRecordset
        for payment in self.payment_lines:
            # Only for PrivatBank
            if (
                payment.payment_amount == 0
                or payment.pos_payment_method_id.use_payment_terminal != "privatbank"
            ):
                continue

            terminal: PrivatbankTerminal = PrivatbankTerminal(
                payment.pos_payment_method_id.privatbank_terminal_ip,
                self.env,
            )

            payment_data: Dict[
                str, Any
            ] = self.order_id.sale_order_id._get_payment_terminal_data(
                payment_type_id=payment.payment_type,
            )

            send_result: Dict[
                Literal["status", "info"], Any
            ] = terminal.send_payment_request(
                amount=-1 * payment.payment_amount,
                order_id=self.order_id.id,
                payment_type_id=payment.payment_type.id,
                session_id=self.pos_session_id.id,
                rrn_param=payment_data.get("rrn", ""),
            )

            if send_result.get("status", "") == "retry":
                raise ValidationError(send_result.get("info", _("Unexpected error")))

        return result

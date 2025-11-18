from typing import Any, Dict, Literal

from odoo import _, models
from odoo.exceptions import ValidationError

from .privat_terminal_api import PrivatbankTerminal


class SaleOrderCheckbox(models.TransientModel):
    _inherit = "sale.order.checkbox.wizard"

    def terminal_send_payment(self, raise_exceptions: bool = True) -> bool:
        """
        Sends payment information to the PrivatBank terminal.

        This method overrides the base `terminal_send_payment` method to include
        functionality specific to PrivatBank terminals. It iterates through the
        payment lines and sends a payment request to the PrivatBank terminal if
        the payment method is set to use PrivatBank.

        Args:
            raise_exceptions (bool): If True, raises a ValidationError on failure.
                                     Defaults to True.

        Returns:
            bool: True if the payment was successfully sent to the terminal, False otherwise.

        Raises:
            ValidationError: If the payment request returns a "retry" status and
                             `raise_exceptions` is True.
        """
        result: bool = super().terminal_send_payment(raise_exceptions=raise_exceptions)

        if not result:
            return result

        payment: Any
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

            send_result: Dict[
                Literal["status", "info"], Any
            ] = terminal.send_payment_request(
                amount=payment.cash_amount,
                order_id=self.order_id.id,
                payment_type_id=payment.payment_type.id,
                session_id=self.pos_session_id.id,
            )

            if send_result.get("status", "") == "retry":
                if raise_exceptions:
                    raise ValidationError(
                        send_result.get("info", _("Unexpected error"))
                    )
                else:
                    return False

        return result

import json
import logging
import socket
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from ftfy import fix_text
from odoo import _, models
from odoo.api import Environment

_logger = logging.getLogger(__name__)

OdooRecordset = Union["models.BaseModel", Any]

EMPTY_THRESHOLD: int = 10


class PrivatbankTerminal:
    def __init__(
        self,
        terminal_ip: str,
        env: Environment,
        subsystem: Literal["SALE", "POS"] = "SALE",
    ) -> None:
        """
        Initializes the PrivatbankTerminal instance.

        Args:
            terminal_ip (str): The IP address and port of the terminal in the format 'IP:PORT'.
            env (Environment): The Odoo environment object.
            subsystem (str): The subsystem type, either 'SALE' or 'POS'. Defaults to 'SALE'.

        Returns:
            None

        Raises:
            Exception: If there is an error during initialization, it logs the error.
        """
        try:
            parts: List[str] = terminal_ip.split(":")
            if len(parts) != 2:
                raise ValueError(f"Invalid terminal_ip format: {terminal_ip}")

            self.terminal_ip: str = parts[0]
            self.terminal_port: str = parts[1]
            self.env: Environment = env
            self.subsystem: str = subsystem
        except Exception:
            _logger.exception("PRIVAT-TRMINAL: Can't connect with terminal")

    def _connect(self) -> bool:
        """
        Establishes a connection to the terminal using the provided IP address and port.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            _logger.debug(
                f"PRIVAT-TRMINAL: Connecting to terminal {self.terminal_ip}:{self.terminal_port}"
            )
            self.socket.connect((self.terminal_ip, int(self.terminal_port)))
        except Exception:
            _logger.exception("PRIVAT-TRMINAL: Can't connect with terminal")
            return False
        return True

    def _send_data(self, data: Dict) -> bool:
        """
        Sends data to the connected socket after encoding it to bytes and appending a null byte.

        Args:
            data (Dict): The data to be sent.

        Returns:
            bool: True if the data was sent successfully, False otherwise.

        Logs:
            Logs the data being sent at debug level.
            Logs any exceptions that occur during sending at exception level.
        """
        try:
            _logger.debug(f"PRIVAT-TRMINAL: SEND DATA: {data}")
            send_data: bytes = json.dumps(data).encode()
            send_data += b"\x00"
            self.socket.sendall(send_data)
        except Exception:
            _logger.exception("Error sending data")
            return False
        return True

    def _receive_data(self) -> bytes:
        """
        Receives data from the terminal.

        This method continuously reads data from the socket in chunks of 512 bytes
        until the received data ends with the byte sequence `b"}\x00"`. If an
        exception occurs during the process, it logs the error and returns an empty
        byte string.

        Returns:
            bytes: The received data as a byte string, or an empty byte string if
            an error occurs.

        Logs:
            Logs the received data at debug level.
            Logs any exceptions that occur during receiving at exception level.
        """
        try:
            received_data: bytes = b""
            empty_count: int = 0

            while True:
                data_new: bytes = self.socket.recv(512)
                if not data_new:
                    empty_count += 1
                    if empty_count > EMPTY_THRESHOLD:
                        raise Exception("Empty data received")
                    continue

                empty_count = 0

                received_data += data_new
                if received_data.endswith(b"}\x00"):
                    break
            _logger.debug(f"PRIVAT-TRMINAL: RECEIVED DATA: {received_data}")
            return received_data
        except Exception:
            _logger.exception("Error receiving reply from terminal")
            return b""

    def _parse_data(
        self, received_data: bytes
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Parses the received data from the terminal.

        Args:
            received_data (bytes): The raw data received from the terminal.

        Returns:
            tuple: A tuple containing a status dictionary and the parsed data dictionary.
                The status dictionary contains:
                    - "status" (str): The status of the parsing process. Possible values are "done" or "retry".
                    - "info" (str, optional): Additional information, especially in case of an error or retry status.
                The parsed data dictionary contains the JSON data parsed from the received data.

        Raises:
            Exception: If there is an error during the parsing process, it will be caught and logged.
        """
        try:
            fixed_text: str = fix_text(received_data.decode())
            _logger.debug(f"PARSED DATA: {fixed_text}")
            data: Dict[str, Any] = json.loads(fixed_text)
            # Check if the server returned an error
            if data.get("error", False):
                return {"status": "retry", "info": data.get("errorDescription")}, data
            params: Dict[str, Any] = data.get("params", {})
            if params:
                # Check if the server returned a service reply
                msg: str = params.get("msgType", "")
                if msg == "deviceBusy":
                    return {"status": "retry", "info": "deviceBusy"}, data
            return {"status": "done"}, data
        except Exception as e:
            _logger.exception("Error parsing data from terminal")
            return {"status": "retry", "info": str(e)}, {}

    def _create_update_transaction(
        self,
        order_id: OdooRecordset,
        payment_type_id: int,
        session_id: int,
        status: Optional[str],
        send_data: Optional[str] = None,
        received_data: Optional[str] = None,
    ) -> None:
        """
        Create or update a transaction record for a given order.

        This method searches for an existing transaction based on the order reference
        and payment type. If found, it updates the transaction with the provided values.
        If not found, it creates a new transaction record.

        Args:
            order_id (OdooRecordset): The order associated with the transaction.
            payment_type_id (int): The payment type identifier.
            session_id (int): The session identifier.
            status (Optional[str]): The status of the transaction.
            send_data (Optional[str], optional): Data sent during the transaction. Defaults to None.
            received_data (Optional[str], optional): Data received during the transaction. Defaults to None.

        Returns:
            None
        """
        # TODO: Add nested transaction for extended logging
        order_ref: str = f"{self.model_name},{order_id.id}"
        transaction: OdooRecordset = self.env["privatbank_terminal.transaction"].search(
            [
                ("order_ref", "=", order_ref),
                ("so_payment_type_id", "=", payment_type_id),
            ],
            limit=1,
        )
        vals: Dict[str, Any] = {
            "order_ref": order_ref,
            "order_receipt": order_id.name,  # type: ignore
            "so_payment_type_id": payment_type_id,
            "session_id": session_id,
            "status": status,
        }

        if send_data:
            vals["send_data"] = send_data

        if received_data:
            vals["received_data"] = received_data

        if not transaction:
            self.env["privatbank_terminal.transaction"].create(vals)
        else:
            transaction.write(vals)

    def _configure_order_model(self, amount: Union[float, Decimal]) -> None:
        """
        Configure the order model based on the subsystem and amount.

        This method sets the appropriate model, model name, and model caption
        based on the value of the `subsystem` attribute and the `amount` parameter.

        Parameters:
        amount (Union[float, Decimal]): The amount to determine the type of order.

        Returns:
        None
        """
        if self.subsystem == "SALE":
            if amount > 0:
                self.model: OdooRecordset = self.env["sale.order"]
                self.model_name: str = "sale.order"
                self.model_caption: str = _("Sale Order")
            else:
                self.model: OdooRecordset = self.env["sale.stock.return"]
                self.model_name: str = "sale.stock.return"
                self.model_caption: str = _("Return Order")
        elif self.subsystem == "POS":
            self.model: OdooRecordset = self.env["pos.order"]
            self.model_name: str = "pos.order"
            self.model_caption: str = _("POS Order")

    def _prepare_order_data(
        self, amount: Union[float, Decimal], rrn: str
    ) -> Dict[str, Any]:
        """
        Prepare the order data for a purchase or refund transaction.

        Args:
            amount (Union[float, Decimal]): The transaction amount. Positive for purchase, negative for refund.
            rrn (str): The Retrieval Reference Number (RRN) for refund transactions.

        Returns:
            Dict: A dictionary containing the transaction data.
        """
        if amount > 0:
            # sell
            # TODO: Add discount
            data: Dict[str, Any] = {
                "method": "Purchase",
                "step": 0,
                "params": {
                    "amount": round(amount, 2),
                    "discount": "",
                    # TODO: Add multiple merchants
                    "merchantId": "0",
                    "facepay": "false",
                },
            }
        else:
            # refund
            data: Dict[str, Any] = {
                "method": "Refund",
                "step": 0,
                "params": {
                    "amount": round(amount, 2) * -1,
                    "discount": "",
                    # TODO: Add multiple merchants
                    "merchantId": "0",
                    "rrn": rrn,
                },
            }

        return data

    def send_payment_request(
        self,
        amount: Union[float, Decimal],
        order_id: int,
        payment_type_id: int,
        session_id: int,
        rrn_param: str = "",
    ) -> Dict[Literal["status", "info"], Any]:
        """
        Sends a payment request to the terminal.

        Args:
            amount (Union[float, Decimal]): The amount to be paid.
            order_id (int): The ID of the order.
            payment_type_id (int): The ID of the payment type.
            session_id (int): The ID of the session.
            rrn_param (str, optional): The RRN parameter. Defaults to "".

        Returns:
            Dict[str, Any]: A dictionary containing the status and info of the payment request.
        """

        self._configure_order_model(amount)

        order: OdooRecordset = self.model.browse(order_id)
        pament_type: OdooRecordset = self.env["so.payment.type"].browse(payment_type_id)

        if not order:
            return {
                "status": "retry",
                "info": _(
                    "%(model_caption)s ID=%(order_id)d not found.",
                    model_caption=self.model_caption,
                    order_id=order_id,
                ),
            }
        if not pament_type:
            return {
                "status": "retry",
                "info": _(
                    "Payment type ID=%(payment_type_id)d not found.",
                    payment_type_id=payment_type_id,
                ),
            }

        data: Dict[str, Any] = self._prepare_order_data(amount, rrn_param)

        self._create_update_transaction(
            order_id=order,
            payment_type_id=payment_type_id,
            session_id=session_id,
            status="waitingCard",
            send_data=json.dumps(data),
        )

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
            if not self._connect():
                return {
                    "status": "retry",
                    "info": _("Can't connect with the terminal."),
                }

            if not self._send_data(data):
                return {
                    "status": "retry",
                    "info": _("Error sending data to the terminal."),
                }

            received_data: bytes = self._receive_data()
            if not received_data:
                return {
                    "status": "retry",
                    "info": _("Error receiving data from the terminal."),
                }
            return_data, parsed_data = self._parse_data(received_data)
            return_data: Dict[str, Any]
            parsed_data: Dict[str, Any]

            if return_data.get("status") == "retry":
                return {
                    "status": "retry",
                    "info": _(
                        "Error parsing reply from the terminal. Info %(info)s",
                        info=return_data.get("info"),
                    ),
                }
            self._create_update_transaction(
                order_id=order,
                payment_type_id=payment_type_id,
                session_id=session_id,
                status=return_data.get("status"),
                received_data=json.dumps(parsed_data),
            )

        return {"status": "done", "info": "Payment request sent successfully."}

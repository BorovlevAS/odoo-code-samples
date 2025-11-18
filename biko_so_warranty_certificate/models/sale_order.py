from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warranty_generated = fields.Boolean(
        string="Warranty Generated",
        compute="_compute_warranty_generated",
    )

    def _compute_warranty_generated(self):
        for record in self:
            record.warranty_generated = any(record.order_line.mapped("warranty_id"))

    def send_warranty(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self.filtered(lambda order: order.warranty_generated):
            if record.partner_id and record.partner_id.mobile:
                send_template_id = self.env.ref(
                    "muztorg_so_warranty_certificate.warranty_sms_tamplate"
                )
                if not send_template_id:
                    continue
                send_template_id.with_context(base_url=base_url).sudo().send_template(
                    send_template_id,
                    recipient_partner_id=record.partner_id,
                    recipient_phone=record.partner_id.mobile,
                    type=send_template_id.type or "sms",
                    obj=record,
                )

    def action_send_warranty(self):
        self.send_warranty()

    def generate_warranty(self):
        for record in self:
            for line in record.order_line.filtered(
                lambda order_line: order_line.product_id.is_warranty
            ):
                if line.warranty_id:
                    line.warranty_id.unlink()

                stock_move_id = (
                    self.env["stock.move"]
                    .sudo()
                    .search([("sale_line_id", "=", line.id)])
                )
                serial_no = ""
                if stock_move_id:
                    lot_ids = stock_move_id.lot_ids
                    serial_no = ", ".join(lot_ids.mapped("name"))
                warranty_id = self.env["warranty.certificate"].create(
                    {
                        "so_line_id": line.id,
                        "warranty_date": fields.Date.today(),
                        "product_name": line.product_id.name,
                        "product_char": line.product_id.biko_character_ukr,
                        "serial_no": serial_no,
                        "warranty_duration": line.product_id.warranty_duration,
                    }
                )
                line.write({"warranty_id": warranty_id.id})

    def action_generate_warranty(self):
        self.generate_warranty()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warranty_id = fields.Many2one(
        comodel_name="warranty.certificate",
        string="Warranty",
        copy=False,
    )

    def action_view_warranty(self):
        self.ensure_one()
        if self.warranty_id:
            action = {
                "type": "ir.actions.act_url",
                "url": f"/warranty/{self.warranty_id.id}",
                "target": "new",
            }
        else:
            action = {"type": "ir.actions.act_window_close"}

        return action

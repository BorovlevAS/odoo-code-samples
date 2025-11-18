from odoo import api, fields, models


class WarrantyCertificate(models.Model):
    _name = "warranty.certificate"
    _description = "Warranty certificate"

    name = fields.Char(
        string="Name",
        required=True,
        default="/",
        copy=False,
    )

    warranty_date = fields.Date(
        string="Warranty Date",
        default=fields.Date.today(),
    )

    so_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        inverse_name="warranty_id",
        string="Sale Order Line",
        ondelete="cascade",
    )
    so_line_id_char = fields.Integer(
        related="so_line_id.id", string="Sale Order Line ID"
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        related="so_line_id.order_id",
        string="Sale order",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="sale_order_id.company_id",
        string="Company",
    )
    product_name = fields.Char(string="Product Name")
    product_char = fields.Char(string="Product Characteristic")
    serial_no = fields.Char(string="Serial Number")
    warranty_duration = fields.Integer(string="Warranty Duration")

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code(
                    "warranty.certificate.code.seq",
                )
                or "/"
            )

        result = super().create(vals)
        return result

    def _prepare_html_values(self):
        self.ensure_one()
        return {
            "product_name": self.product_name,
            "product_char": self.product_char,
            "serial_no": self.serial_no,
            "warranty_duration": self.warranty_duration,
            "warranty_number": self.name,
            "warranty_date": self.warranty_date,
        }

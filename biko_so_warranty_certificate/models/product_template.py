from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_warranty = fields.Boolean(
        string="Warranty needed",
        default=False,
    )
    warranty_duration = fields.Integer(
        string="Warranty duration",
        default=12,
    )

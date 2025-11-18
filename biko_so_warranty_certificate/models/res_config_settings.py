from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    biko_send_warranty = fields.Boolean(
        comodel_name="product.pricelist",
        string="Send warranty certificate",
    )


class Settings(models.TransientModel):
    _inherit = "res.config.settings"
    biko_send_warranty = fields.Boolean(
        related="company_id.biko_send_warranty",
        string="Send warranty certificate",
        readonly=False,
    )

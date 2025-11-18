from odoo import fields, models


class Team(models.Model):
    _inherit = "crm.team"

    is_send_warranty = fields.Boolean(string="Send Warranty Certificate")

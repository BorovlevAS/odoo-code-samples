from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        result = super()._action_done()

        for res in self:
            if res.state == "done":
                if (
                    res.location_dest_id.usage == "customer"
                    and res.sale_id
                    and res.sale_id.team_id
                    and res.sale_id.team_id.is_send_warranty
                ):
                    res.sale_id.generate_warranty()
                    if res.sale_id.company_id.biko_send_warranty:
                        res.sale_id.send_warranty()

        return result

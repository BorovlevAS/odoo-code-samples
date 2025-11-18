from odoo import _, http
from odoo.http import request


class WarrantyReport(http.Controller):
    @http.route(
        "/warranty/<int:rec_id>",
        type="http",
        auth="public",
    )
    def warranty_report_html(self, rec_id):
        warranty_id = (
            request.env["warranty.certificate"]
            .sudo()
            .search([("id", "=", rec_id)], limit=1)
        )
        if not warranty_id:
            return request.not_found()
        values = warranty_id._prepare_html_values()
        values["title"] = _("Warranty Certificate")
        return request.render(
            "biko_so_warranty_certificate.warranty_certificate", values
        )

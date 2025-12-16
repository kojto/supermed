from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_financial_reports_list_view(self):
        action_id = self.env.ref("trinity_financial_reports.action_trinity_financial_reports").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

from odoo import models

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_medical_notice_list_view(self):
        action_id = self.env.ref("trinity_commons.action_trinity_medical_notice").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

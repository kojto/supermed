from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_prescription_list_view(self):
        action_id = self.env.ref("trinity_prescription.action_prescription_list").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_prescription_category_list_view(self):
        action_id = self.env.ref("trinity_prescription.action_prescription_category_list").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_prescription_template_list_view(self):
        action_id = self.env.ref("trinity_prescription.action_prescription_template_list").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_nomenclature_list_view(self):
        action_id = self.env.ref("trinity_nomenclature.action_trinity_nomenclature").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_trinity_nomenclature_import_nhis(self):
        action_id = self.env.ref("trinity_nomenclature.action_trinity_nomenclature_import_nhis").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_trinity_nomenclature_import_wizard(self):
        action_id = self.env.ref("trinity_nomenclature.action_trinity_nomenclature_import_wizard").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

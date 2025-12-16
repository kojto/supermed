from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_patient_list_view(self):
        action_id = self.env.ref("trinity_patient.action_trinity_patient").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_new_patient_form(self):
        return {
            'name': _('New Patient'),
            'type': 'ir.actions.act_window',
            'res_model': 'trinity.patient',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': {'create': True},
        }

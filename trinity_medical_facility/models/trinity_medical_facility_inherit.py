from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_medical_facility_list_view(self):
        action_id = self.env.ref("trinity_medical_facility.action_trinity_medical_facility").id
        medical_facility = self.env['trinity.medical.facility'].search([], limit=1)

        if medical_facility:
            url = f"/web#action={action_id}&id={medical_facility.id}&model=trinity.medical.facility&view_type=form"
        else:
            url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

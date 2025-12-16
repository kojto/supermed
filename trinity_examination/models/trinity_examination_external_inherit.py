from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_examination_list_view(self):
        action_id = self.env.ref("trinity_examination.action_trinity_examination").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_examination_template_list_view(self):
        action_id = self.env.ref("trinity_examination.action_trinity_examination_template").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_new_examination_form(self):
        return {
            'name': _('New Examination'),
            'type': 'ir.actions.act_window',
            'res_model': 'trinity.examination',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': {'create': True},
        }

class TrinityExaminationKojtoBaseNamesInherit(models.Model):
    _inherit = "kojto.base.names"

    language_id = fields.Many2one("res.lang", string="Language", default=lambda self: self.env.ref("base.lang_bg").id )

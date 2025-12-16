# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_examination_type_list_view(self):
        action_id = self.env.ref(
            "trinity_examination_type.action_trinity_examination_type"
        ).id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

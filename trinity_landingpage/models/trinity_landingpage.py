from odoo import api, fields, models, exceptions
from odoo.http import request


class KojtoLandingpageInherit(models.Model):
    _inherit = "kojto.landingpage"

    def open_users_list_view(self):
        return {
            "type": "ir.actions.act_url",
            "url": "/odoo/users",
            "target": "self",
        }

    def open_groups_list_view(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Groups",
            "res_model": "res.groups",
            "view_mode": "list",
            "target": "current",
            "context": {},
        }

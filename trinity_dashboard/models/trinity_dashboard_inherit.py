from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_dashboard(self):
        dashboard_record = self.env["trinity.dashboard"].search(
            [("user_id", "=", self.env.user.id)],
            limit=1,
            order="id"
        )
        action_id = self.env.ref("trinity_dashboard.action_trinity_dashboard").id

        if not dashboard_record:
            dashboard_record = self.env["trinity.dashboard"].create({
                "user_id": self.env.user.id,
                "name": f"Статистика за {self.env.user.name}",
            })

        url = f"/web#id={dashboard_record.id}&view_type=form&model=trinity.dashboard&action={action_id}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

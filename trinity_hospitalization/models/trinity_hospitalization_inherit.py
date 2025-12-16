from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_hospitalisation_fetch_view(self):
        fetch_record = self.env["trinity.hospitalisation.fetch"].search(
            [("user_id", "=", self.env.user.id)],
            limit=1,
            order="id"
        )

        action_id = self.env.ref("trinity_hospitalization.action_trinity_hospitalisation_fetch_form").id

        if not fetch_record:
            fetch_record = self.env["trinity.hospitalisation.fetch"].create({
                "user_id": self.env.user.id,
            })
        else:
            fetch_record.fetch_new_hospitalisation()

        url = f"/web#id={fetch_record.id}&view_type=form&model=trinity.hospitalisation.fetch&action={action_id}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }


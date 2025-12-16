from odoo import models, fields, api, _

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_referral_check_list_view(self):
        action_id = self.env.ref("trinity_referral.action_trinity_referral_check").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_referral_fetch_view(self):
        fetch_record = self.env["trinity.referral.fetch"].search(
            [("user_id", "=", self.env.user.id)],
            limit=1,
            order="id"
        )

        action_id = self.env.ref("trinity_referral.action_trinity_referral_fetch_form").id

        if not fetch_record:
            fetch_record = self.env["trinity.referral.fetch"].create({
                "user_id": self.env.user.id,
            })
        else:
            fetch_record.fetch_new_referral()

        url = f"/web#id={fetch_record.id}&view_type=form&model=trinity.referral.fetch&action={action_id}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    def open_referral_incomming_list_view(self):
        action_id = self.env.ref("trinity_referral.action_trinity_referral_incoming").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_referral_issue_list_view(self):
        action_id = self.env.ref("trinity_referral.action_trinity_referral_issue").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_referral_issue_dashboard_view(self):
        dashboard_record = self.env["trinity.referral.issue.dashboard"].search(
            [("user_id", "=", self.env.user.id)],
            limit=1,
            order="id desc"
        )

        action_id = self.env.ref("trinity_referral.action_trinity_referral_issue_dashboard").id

        if not dashboard_record:
            dashboard_record = self.env["trinity.referral.issue.dashboard"].create({
                "user_id": self.env.user.id,
            })

        url = f"/web#id={dashboard_record.id}&view_type=form&model=trinity.referral.issue.dashboard&action={action_id}"
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

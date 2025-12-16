from odoo import models, fields, api, _
from datetime import timedelta

class KojtoFinanceInvoicesInherit(models.Model):
    _inherit = "kojto.finance.invoices"

    examinations_in_invoice = fields.One2many('trinity.examination', 'invoice_id', string='Прегледи включени във фактурата')

    user_id = fields.Many2one('res.users', string='Потребител', default=lambda self: self.env.user)

    @api.depends("force_paid_status", "open_amount")
    def _compute_paid(self):
        super()._compute_paid()

        if not self.env.context.get('skip_examination_update'):
            self.set_examination_paid_status()

    def set_examination_paid_status(self):
        for invoice in self:
            if not invoice.examinations_in_invoice:
                continue

            if invoice.paid:
                allocation_dates = invoice.transaction_allocation_ids.mapped('transaction_date')
                paid_date = max(allocation_dates) if allocation_dates else invoice.date_issue
                vals = {
                    "examination_paid": True,
                    "examination_paid_date": paid_date,
                }
            else:
                vals = {
                    "examination_paid": False,
                    "examination_paid_date": False,
                }

            invoice.examinations_in_invoice.write(vals)

    def write(self, vals):
        res = super().write(vals)
        if any(field in vals for field in ('paid', 'force_paid_status', 'open_amount')):
            self.set_examination_paid_status()
        return res

class KojtoFinanceCashflow(models.Model):
    _name = "kojto.finance.cashflow"
    _inherit = "kojto.finance.cashflow"

    @api.onchange("counterparty_bank_account_id", "counterparty_id")
    def _onchange_assign_bank_account_to_contact(self):
        if self.counterparty_bank_account_id and self.counterparty_id:
            if self.counterparty_bank_account_id.contact_id != self.counterparty_id:
                self.counterparty_bank_account_id.contact_id = self.counterparty_id


class KojtoFinanceCashflowAllocation(models.Model):
    _name = "kojto.finance.cashflow.allocation"
    _inherit = "kojto.finance.cashflow.allocation"

    def make_amount_positive(self):
        for record in self:
            if record.amount and record.amount < 0:
                record.amount = abs(record.amount)

class KojtoLandingpage(models.Model):
    _inherit = "kojto.landingpage"

    def open_trinity_invoice_list_view(self):
        action_id = self.env.ref("kojto_finance.action_kojto_finance_invoices").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_trinity_cashflow_list_view(self):
        action_id = self.env.ref("kojto_finance.action_kojto_finance_cashflow").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

    def open_trinity_monthly_notification_list_view(self):
        action_id = self.env.ref("trinity_finance.action_trinity_monthly_notification").id
        url = f"/web#action={action_id}"

        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }

# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta


class TrinityReferralIssueNhifAllowed(models.Model):
    _name = 'trinity.referral.issue.nhif.allowed'
    _description = 'Trinity Referral Issue NHIF Allowed'
    _inherit = ["trinity.library.user.company.fields"]
    _rec_name = 'name'

    name = fields.Char(string='№', required=True, default=lambda self: self._generate_name(), copy=False)
    contents = fields.One2many('trinity.referral.issue.nhif.allowed.contents', 'nhif_allowence_id', string='Съдържание')

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False, required=True)

    date_start = fields.Date(string='От дата:', required=True, default=lambda self: self.default_date_start())
    date_end = fields.Date(string='До дата:', required=True, default=lambda self: self.default_date_end())

    @api.model
    def _generate_name(self):
        date_today = datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat
        existing_record = self.env['trinity.referral.issue.nhif.allowed'].sudo().search(
            [('name', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='name desc',
            limit=1,
        )
        if existing_record:
            last_sequence = existing_record.name[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1
        return f'Ref-NHIF-{date_today}-{current_company_vat}-{sequence_number:04d}'

    def _get_quarter_bounds(self, reference_date):
        reference_date = reference_date or fields.Date.context_today(self)
        quarter = (reference_date.month - 1) // 3
        start_month = quarter * 3 + 1
        quarter_start = reference_date.replace(month=start_month, day=1)
        quarter_end = (quarter_start + relativedelta(months=3)) - timedelta(days=1)
        return quarter_start, quarter_end

    @api.model
    def default_date_start(self):
        quarter_start, _ = self._get_quarter_bounds(fields.Date.context_today(self))
        return quarter_start

    @api.model
    def default_date_end(self):
        _, quarter_end = self._get_quarter_bounds(fields.Date.context_today(self))
        return quarter_end

class TrinityReferralIssueNhifAllowedContents(models.Model):
    _name = 'trinity.referral.issue.nhif.allowed.contents'
    _description = 'Trinity Referral Issue NHIF Allowed Contents'
    _order = 'position, id'

    isLimited_by_amount = fields.Boolean(string='Лимит в сума', default=True)
    isLimited_by_count = fields.Boolean(string='Лимит в брой', default=False)

    nhif_allowence_id = fields.Many2one('trinity.referral.issue.nhif.allowed', string='Dashboard', ondelete='cascade')
    referral_category_id = fields.Many2one('trinity.nomenclature.cl014', string='Тип направление')
    referral_category_key = fields.Char(related='referral_category_id.key', string='Код')
    total_count = fields.Integer(string='Брой')
    total_amount = fields.Monetary(string='Сума', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.BGN'))
    company_id = fields.Many2one('res.company', string='Фирма', default=lambda self: self.env.user.company_id)
    position = fields.Integer(string='#')

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.fields import Date
import io
import base64
import xlsxwriter

class TrinityReferralIssueDashboard(models.Model):
    _name = 'trinity.referral.issue.dashboard'
    _description = 'Trinity Referral Issue Dashboard'
    _rec_name = 'name'
    _inherit = ["trinity.library.user.company.fields"]

    name = fields.Char(string='№', required=True, default=lambda self: self.generate_name(), copy=False)

    contents = fields.One2many('trinity.referral.issue.dashboard.contents', 'dashboard_id', string='Съдържание', compute='create_dashboard_content')

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)
    main_dr_performing_full_name = fields.Char(related='main_dr_performing_doctor_id.full_name', string='Име')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.BGN'))

    date_start = fields.Date(string='От дата:', required=True, default=lambda self: self.default_date_start())
    date_end = fields.Date(string='До дата:', required=True, default=lambda self: self.default_date_end())

    def create_dashboard_content(self):
        DashboardContents = self.env['trinity.referral.issue.dashboard.contents']

        for dashboard in self:
            DashboardContents.search([('dashboard_id', '=', dashboard.id)]).unlink()

            domain = []
            if dashboard.date_start:
                domain.append(('referral_authoredOn', '>=', dashboard.date_start))
            if dashboard.date_end:
                domain.append(('referral_authoredOn', '<=', dashboard.date_end))
            if dashboard.main_dr_performing_doctor_id:
                domain.append(('referral_main_dr_performing_doctor_id', '=', dashboard.main_dr_performing_doctor_id.id))

            referrals = self.env['trinity.referral.issue'].search(domain)
            grouped = {}
            for referral in referrals:
                category = referral.referral_category
                key = category.id if category else False
                if key not in grouped:
                    grouped[key] = {
                        'referral_category_id': category.id if category else False,
                        'referral_category_name': category.name if category else '',
                        'referral_category_key': category.key if category else '',
                        'total_count': 0,
                        'total_amount': 0.0,
                    }
                grouped[key]['total_count'] += 1
                grouped[key]['total_amount'] += referral.referral_price or 0.0

            contents_vals = []
            for index, (_, data) in enumerate(sorted(grouped.items(), key=lambda item: item[1]['referral_category_key'])):
                data['position'] = index + 1
                contents_vals.append({
                    'referral_category_id': data['referral_category_id'],
                    'referral_category_name': data['referral_category_name'],
                    'referral_category_key': data['referral_category_key'],
                    'total_count': data['total_count'],
                    'total_amount': data['total_amount'],
                    'currency_id': dashboard.currency_id.id,
                    'company_id': dashboard.company_id.id,
                    'dashboard_id': dashboard.id,
                    'position': data['position'],
                })

            dashboard.contents = DashboardContents.create(contents_vals) if contents_vals else DashboardContents

    @api.model
    def generate_name(self):
        date_today = datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.referral.issue.dashboard'].sudo().search(
            [('name', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='name desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.name[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1

        lrn_value = f'Ref-Stat-{date_today}-{current_company_vat}-{sequence_number:04d}'
        return lrn_value

    def export_monthly_data_to_xlsx(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        worksheet_count = workbook.add_worksheet('Referral Count by Category')
        worksheet_amount = workbook.add_worksheet('Referral Amount by Category')

        base_domain = [
            ('referral_authoredOn', '>=', self.date_start),
            ('referral_authoredOn', '<=', self.date_end),
            ('response_status.key', '=', '2'),
        ]
        if self.main_dr_performing_doctor_id:
            base_domain.append(('referral_main_dr_performing_doctor_id', '=', self.main_dr_performing_doctor_id.id))

        referrals = self.env['trinity.referral.issue'].search(base_domain)
        referral_categories = sorted([cat for cat in set(referrals.mapped('referral_category')) if cat], key=lambda x: x.key)

        # Write headers
        worksheet_count.write(0, 0, 'Месец')
        worksheet_amount.write(0, 0, 'Месец')
        for col, category in enumerate(referral_categories, start=1):
            worksheet_count.write(0, col, f'{category.key} - {category.name}')
            worksheet_amount.write(0, col, f'{category.key} - {category.name}')

        start_date = self.date_start
        end_date = self.date_end
        current_month = start_date.month
        current_year = start_date.year
        row = 1

        while current_year < end_date.year or (current_year == end_date.year and current_month <= end_date.month):
            month_year = f'{current_year}-{current_month:02d}'
            data_count = [month_year]
            data_amount = [month_year]

            month_start = datetime(current_year, current_month, 1)
            month_end = datetime(current_year if current_month < 12 else current_year + 1, (current_month % 12) + 1, 1)
            domain = [
                ('referral_authoredOn', '>=', month_start.date()),
                ('referral_authoredOn', '<', month_end.date()),
            ]
            if self.main_dr_performing_doctor_id:
                domain.append(('referral_main_dr_performing_doctor_id', '=', self.main_dr_performing_doctor_id.id))

            for category in referral_categories:
                category_domain = domain + [('referral_category', '=', category.id)]
                referrals_in_category = self.env['trinity.referral.issue'].search(category_domain)
                count = len(referrals_in_category)
                amount = sum(r.referral_price for r in referrals_in_category)
                data_count.append(count)
                data_amount.append(amount)

            for col, value in enumerate(data_count):
                worksheet_count.write(row, col, value)
            for col, value in enumerate(data_amount):
                worksheet_amount.write(row, col, value)

            row += 1

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        workbook.close()
        output.seek(0)

        self.create_dashboard_content()

        attachment = self.env['ir.attachment'].create({
            'name': 'referral_monthly_data_by_category.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()).decode(),
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'new',
        }

    def _ensure_date_value(self, value):
        if not value:
            return value
        if isinstance(value, str):
            return fields.Date.from_string(value)
        return value

    @api.model
    def default_date_start(self):
        quarter_start, _ = self._get_quarter_bounds(fields.Date.context_today(self))
        return quarter_start

    @api.model
    def default_date_end(self):
        _, quarter_end = self._get_quarter_bounds(fields.Date.context_today(self))
        return quarter_end

    def _get_quarter_bounds(self, reference_date):
        reference_date = self._ensure_date_value(reference_date or fields.Date.context_today(self))
        quarter = (reference_date.month - 1) // 3
        start_month = quarter * 3 + 1
        quarter_start = reference_date.replace(month=start_month, day=1)
        quarter_end = quarter_start + relativedelta(months=3) - relativedelta(days=1)
        return quarter_start, quarter_end

    def forward_one_quarter(self):
        self.ensure_one()
        quarter_start, _ = self._get_quarter_bounds(self.date_start)
        next_quarter_start = quarter_start + relativedelta(months=3)
        next_quarter_end = next_quarter_start + relativedelta(months=3) - relativedelta(days=1)
        self.date_start = next_quarter_start
        self.date_end = next_quarter_end
        self.create_dashboard_content()

    def backward_one_quarter(self):
        self.ensure_one()
        quarter_start, _ = self._get_quarter_bounds(self.date_start)
        previous_quarter_start = quarter_start - relativedelta(months=3)
        previous_quarter_end = previous_quarter_start + relativedelta(months=3) - relativedelta(days=1)
        self.date_start = previous_quarter_start
        self.date_end = previous_quarter_end
        self.create_dashboard_content()

    def forward_one_year(self):
        self.ensure_one()
        start_date = self._ensure_date_value(self.date_start)
        end_date = self._ensure_date_value(self.date_end)
        self.date_start = (start_date + relativedelta(years=1)).replace(day=1)
        shifted_end = end_date + relativedelta(years=1)
        self.date_end = (shifted_end + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        self.create_dashboard_content()

    def backward_one_year(self):
        self.ensure_one()
        start_date = self._ensure_date_value(self.date_start)
        end_date = self._ensure_date_value(self.date_end)
        self.date_start = (start_date - relativedelta(years=1)).replace(day=1)
        shifted_end = end_date - relativedelta(years=1)
        self.date_end = (shifted_end + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        self.create_dashboard_content()

    def set_dates_to_current_quarter(self):
        self.ensure_one()
        quarter_start, quarter_end = self._get_quarter_bounds(fields.Date.context_today(self))
        self.date_start = quarter_start
        self.date_end = quarter_end
        self.create_dashboard_content()

    def set_dates_to_current_year(self):
        self.ensure_one()
        today = fields.Date.context_today(self)
        today = self._ensure_date_value(today)
        first_day_of_current_year = today.replace(day=1, month=1)
        last_day_of_current_year = today.replace(day=31, month=12)
        self.date_start = first_day_of_current_year
        self.date_end = last_day_of_current_year
        self.create_dashboard_content()

class TrinityReferralIssueDashboardContents(models.Model):
    _name = 'trinity.referral.issue.dashboard.contents'
    _description = 'Trinity Referral Issue Dashboard Contents'
    _order = 'position'

    referral_category_name = fields.Char(string='Категория направление')
    referral_category_id = fields.Many2one('trinity.nomenclature.cl014', string='Тип направление')
    referral_category_key = fields.Char(related='referral_category_id.key', string='Код')
    total_count = fields.Integer(string='Брой издадени')
    total_amount = fields.Float(string='Сума')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.BGN'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    dashboard_id = fields.Many2one('trinity.referral.issue.dashboard', string='Dashboard')
    position = fields.Integer(string='#')

    count_allowed = fields.Integer(string='Брой разрешени', compute='_compute_allowed_metrics')
    amount_allowed = fields.Monetary(string='Сума разрешени', currency_field='currency_id', compute='_compute_allowed_metrics')
    over_limit = fields.Boolean(string='Превишен лимит', compute='_compute_allowed_metrics')

    isLimited_by_amount = fields.Boolean(string='Лимит в сума', compute='_compute_allowed_metrics')
    isLimited_by_count = fields.Boolean(string='Лимит в брой', compute='_compute_allowed_metrics')

    @api.depends('dashboard_id.main_dr_performing_doctor_id', 'dashboard_id.date_start', 'dashboard_id.date_end', 'referral_category_id')
    def _compute_allowed_metrics(self):
        Allowance = self.env['trinity.referral.issue.nhif.allowed']
        allowance_cache = {}

        for line in self:
            line.count_allowed = 0
            line.amount_allowed = 0.0
            line.over_limit = False
            line.isLimited_by_amount = False
            line.isLimited_by_count = False

            dashboard = line.dashboard_id
            if not dashboard or not dashboard.main_dr_performing_doctor_id or not dashboard.date_start or not dashboard.date_end or not line.referral_category_id:
                continue

            cache_key = (
                dashboard.main_dr_performing_doctor_id.id,
                dashboard.date_start,
                dashboard.date_end,
                dashboard.company_id.id,
            )
            if cache_key not in allowance_cache:
                allowance_cache[cache_key] = Allowance.search([
                    ('main_dr_performing_doctor_id', '=', dashboard.main_dr_performing_doctor_id.id),
                    ('date_start', '=', dashboard.date_start),
                    ('date_end', '=', dashboard.date_end),
                    ('company_id', '=', dashboard.company_id.id),
                ], limit=1)

            allowance = allowance_cache[cache_key]
            if not allowance:
                continue

            allowed_line = allowance.contents.filtered(lambda c: c.referral_category_id.id == line.referral_category_id.id)
            if allowed_line:
                allowance_line = allowed_line[0]
                line.count_allowed = allowance_line.total_count
                line.amount_allowed = allowance_line.total_amount
                # Copy values directly from source model
                line.isLimited_by_amount = allowance_line.isLimited_by_amount
                line.isLimited_by_count = allowance_line.isLimited_by_count

                over_limit = False

                # Check count limit if limited by count
                if allowance_line.isLimited_by_count:
                    count_limit_defined = line.count_allowed not in (False, None, 0)
                    if count_limit_defined and line.total_count > line.count_allowed:
                        over_limit = True

                # Check amount limit if limited by amount
                if allowance_line.isLimited_by_amount:
                    amount_limit_defined = line.amount_allowed not in (False, None, 0.0)
                    if amount_limit_defined and line.total_amount > line.amount_allowed:
                        over_limit = True

                line.over_limit = over_limit

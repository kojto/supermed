# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.fields import Date
import io
import base64
import xlsxwriter

class TrinityDashboard(models.Model):
    _name = 'trinity.dashboard'
    _description = 'Trinity Dashboard'
    _rec_name = 'name'
    _inherit = ["trinity.library.user.company.fields"]

    name = fields.Char(string='№', required=True, default=lambda self: self.generate_name(), copy=False)

    contents = fields.One2many('trinity.dashboard.contents', 'dashboard_id', compute='create_dashboard_content', string='Съдържание')

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)
    main_dr_performing_full_name = fields.Char(related='main_dr_performing_doctor_id.full_name', string='Име')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.BGN'))

    date_start = fields.Date(string='От дата:', required=True, default=lambda self: self.default_date_start() if not self.date_start else False)
    date_end = fields.Date(string='До дата:', required=True, default=lambda self: self.default_date_end() if not self.date_end else False)

    def create_dashboard_content(self):
        DashboardContents = self.env['trinity.dashboard.contents']
        Examination = self.env['trinity.examination']

        for dashboard in self:
            DashboardContents.search([('dashboard_id', '=', dashboard.id)]).unlink()

            base_domain = []
            if dashboard.date_start:
                base_domain.append(('examination_open_dtm', '>=', dashboard.date_start))
            if dashboard.date_end:
                base_domain.append(('examination_open_dtm', '<=', dashboard.date_end))
            if dashboard.main_dr_performing_doctor_id:
                base_domain.append(('main_dr_performing_doctor_id', '=', dashboard.main_dr_performing_doctor_id.id))

            cost_bearers = self.env['trinity.costbearer'].with_context(active_test=False).search([
                ('financingSource', '!=', False),
                '|', ('active_from', '=', False), ('active_from', '<=', dashboard.date_end),
                '|', ('active_until', '=', False), ('active_until', '>=', dashboard.date_start),
            ])

            def sort_cost_bearers(cbs):
                sorted_list = []
                pos_map = {}
                index = 1
                for name in ['ПАЦИЕНТ', 'НЗОК', 'БЕЗ ПЛАЩАНЕ']:
                    cb = next((c for c in cbs if c.name == name), None)
                    if cb:
                        pos_map[cb.id] = index
                        sorted_list.append(cb)
                        index += 1
                others = sorted([cb for cb in cbs if cb.name not in ['ПАЦИЕНТ', 'НЗОК', 'БЕЗ ПЛАЩАНЕ']], key=lambda c: c.name or '')
                for cb in others:
                    pos_map[cb.id] = index
                    sorted_list.append(cb)
                    index += 1
                return sorted_list, pos_map

            sorted_cost_bearers, position_map = sort_cost_bearers(cost_bearers)

            grouped = {}
            for cb in sorted_cost_bearers:
                grouped[cb.id] = {
                    'cost_bearer': cb.name or '',
                    'total_count': 0,
                    'total_amount': 0.0,
                    'rejected_count': 0,
                    'rejected_amount': 0.0,
                    'payout_count': 0,
                    'payout_amount': 0.0,
                    'pending_count': 0,
                    'pending_amount': 0.0,
                }

            examinations = Examination.search(base_domain)
            for examination in examinations:
                cb = examination.cost_bearer_id
                if not cb or cb.id not in grouped:
                    continue

                data = grouped[cb.id]
                price = examination.examination_type_id_price.price if examination.examination_type_id_price else 0.0
                data['total_count'] += 1
                data['total_amount'] += price

                if examination.rejected_payment and examination.rejected_payment != 'no':
                    data['rejected_count'] += 1
                    data['rejected_amount'] += price

            payout_domain = [
                ('examination_paid_date', '!=', False),
                ('rejected_payment', '!=', 'yes'),
            ]
            if dashboard.date_start:
                payout_domain.append(('examination_paid_date', '>=', dashboard.date_start))
            if dashboard.date_end:
                payout_domain.append(('examination_paid_date', '<=', dashboard.date_end))
            if dashboard.main_dr_performing_doctor_id:
                payout_domain.append(('main_dr_performing_doctor_id', '=', dashboard.main_dr_performing_doctor_id.id))

            paid_examinations = Examination.search(payout_domain)
            for examination in paid_examinations:
                cb = examination.cost_bearer_id
                if not cb or cb.id not in grouped:
                    continue

                price = examination.examination_type_id_price.price if examination.examination_type_id_price else 0.0
                data = grouped[cb.id]
                data['payout_count'] += 1
                data['payout_amount'] += price

            # Calculate pending (invoices but not paid) for all times
            # Get all unpaid invoices and their associated examinations
            Invoice = self.env['kojto.finance.invoices']
            unpaid_invoices = Invoice.search([
                ('paid', '=', False),
                ('examinations_in_invoice', '!=', False),
            ])

            # Collect all examinations from unpaid invoices
            all_pending_examinations = unpaid_invoices.mapped('examinations_in_invoice')

            # Filter by doctor if specified
            if dashboard.main_dr_performing_doctor_id:
                all_pending_examinations = all_pending_examinations.filtered(
                    lambda e: e.main_dr_performing_doctor_id.id == dashboard.main_dr_performing_doctor_id.id
                )

            # Group by cost_bearer
            for examination in all_pending_examinations:
                cb = examination.cost_bearer_id
                if not cb or cb.id not in grouped:
                    continue

                price = examination.examination_type_id_price.price if examination.examination_type_id_price else 0.0
                data = grouped[cb.id]
                data['pending_count'] += 1
                data['pending_amount'] += price

            contents_vals = []
            summary_totals = {
                'total_amount': 0.0,
                'total_count': 0,
                'rejected_amount': 0.0,
                'rejected_count': 0,
                'payout_amount': 0.0,
                'payout_count': 0,
                'pending_amount': 0.0,
                'pending_count': 0,
            }

            for index, cb in enumerate(sorted_cost_bearers):
                data = grouped.get(cb.id)
                if not data:
                    continue

                summary_totals['total_amount'] += data['total_amount']
                summary_totals['total_count'] += data['total_count']
                summary_totals['rejected_amount'] += data['rejected_amount']
                summary_totals['rejected_count'] += data['rejected_count']
                summary_totals['payout_amount'] += data['payout_amount']
                summary_totals['payout_count'] += data['payout_count']
                summary_totals['pending_amount'] += data['pending_amount']
                summary_totals['pending_count'] += data['pending_count']

                contents_vals.append({
                    'cost_bearer': data['cost_bearer'],
                    'total_amount': data['total_amount'],
                    'total_count': data['total_count'],
                    'rejected_amount': data['rejected_amount'],
                    'rejected_count': data['rejected_count'],
                    'payout_amount': data['payout_amount'],
                    'payout_count': data['payout_count'],
                    'pending_amount': data['pending_amount'],
                    'pending_count': data['pending_count'],
                    'currency_id': dashboard.currency_id.id,
                    'company_id': dashboard.company_id.id,
                    'dashboard_id': dashboard.id,
                    'position': position_map.get(cb.id, index + 1),
                })

            if contents_vals:
                contents_vals.append({
                    'cost_bearer': 'ОБЩО',
                    'total_amount': summary_totals['total_amount'],
                    'total_count': summary_totals['total_count'],
                    'rejected_amount': summary_totals['rejected_amount'],
                    'rejected_count': summary_totals['rejected_count'],
                    'payout_amount': summary_totals['payout_amount'],
                    'payout_count': summary_totals['payout_count'],
                    'pending_amount': summary_totals['pending_amount'],
                    'pending_count': summary_totals['pending_count'],
                    'currency_id': dashboard.currency_id.id,
                    'company_id': dashboard.company_id.id,
                    'dashboard_id': dashboard.id,
                    'position': len(contents_vals) + 1,
                })

            dashboard.contents = DashboardContents.create(contents_vals) if contents_vals else DashboardContents

    @api.model
    def generate_name(self):
        date_today = datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.dashboard'].sudo().search(
            [('name', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='name desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.name[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1

        lrn_value = f'Stat-{date_today}-{current_company_vat}-{sequence_number:04d}'
        return lrn_value

    def export_monthly_data_to_xlsx(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        worksheets = {
            'total_amount': workbook.add_worksheet('Total Amount'),
            'total_count': workbook.add_worksheet('Total Count'),
            'rejected_amount': workbook.add_worksheet('Rejected Amount'),
            'rejected_count': workbook.add_worksheet('Rejected Count'),
            'payout_amount': workbook.add_worksheet('Payout Amount'),
            'payout_count': workbook.add_worksheet('Payout Count'),
            'pending_amount': workbook.add_worksheet('Pending Amount'),
            'pending_count': workbook.add_worksheet('Pending Count'),
        }

        base_domain = [
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        if self.main_dr_performing_doctor_id:
            base_domain.append(('main_dr_performing_doctor_id', '=', self.main_dr_performing_doctor_id.id))

        examinations = self.env['trinity.examination'].search(base_domain)
        cost_bearers = sorted([cb for cb in set(examinations.mapped('cost_bearer_id')) if cb and cb.name], key=lambda x: x.name)

        for worksheet in worksheets.values():
            worksheet.write(0, 0, 'Месец')
            for col, cost_bearer in enumerate(cost_bearers, start=1):
                worksheet.write(0, col, cost_bearer.name)

        start_date = self.date_start
        end_date = self.date_end
        current_month = start_date.month
        current_year = start_date.year
        row = 1

        while current_year < end_date.year or (current_year == end_date.year and current_month <= end_date.month):
            month_year = f'{current_year}-{current_month:02d}'

            data = {
                'total_amount': [month_year],
                'total_count': [month_year],
                'rejected_amount': [month_year],
                'rejected_count': [month_year],
                'payout_amount': [month_year],
                'payout_count': [month_year],
                'pending_amount': [month_year],
                'pending_count': [month_year],
            }

            month_start = datetime(current_year, current_month, 1)
            month_end = datetime(current_year if current_month < 12 else current_year + 1, (current_month % 12) + 1, 1)
            domain = [
                ('examination_open_dtm', '>=', month_start),
                ('examination_open_dtm', '<', month_end),
            ]

            if self.main_dr_performing_doctor_id:
                domain.append(('main_dr_performing_doctor_id', '=', self.main_dr_performing_doctor_id.id))

            for cost_bearer in cost_bearers:
                total_domain = domain + [('cost_bearer_id', '=', cost_bearer.id), ('rejected_payment', '!=', 'yes')]
                if cost_bearer.financingSource and cost_bearer.financingSource.key == '2':
                    total_domain.append(('e_examination_nrn', '!=', False))
                total_records = self.env['trinity.examination'].search(total_domain)
                total_amount = sum(record.examination_type_id_price.price if record.examination_type_id_price else 0 for record in total_records)
                total_count = len(total_records)

                rejected_domain = domain + [('cost_bearer_id', '=', cost_bearer.id), ('rejected_payment', '!=', 'no')]
                if cost_bearer.financingSource and cost_bearer.financingSource.key == '2':
                    rejected_domain.append(('e_examination_nrn', '!=', False))
                rejected_records = self.env['trinity.examination'].search(rejected_domain)
                rejected_amount = sum(record.examination_type_id_price.price if record.examination_type_id_price else 0 for record in rejected_records)
                rejected_count = len(rejected_records)

                paid_domain = [
                    ('examination_paid_date', '>=', month_start),
                    ('examination_paid_date', '<', month_end),
                    ('cost_bearer_id', '=', cost_bearer.id),
                    ('rejected_payment', '!=', 'yes'),
                ]
                if cost_bearer.financingSource and cost_bearer.financingSource.key == '2':
                    paid_domain.append(('e_examination_nrn', '!=', False))
                if self.main_dr_performing_doctor_id:
                    paid_domain.append(('main_dr_performing_doctor_id', '=', self.main_dr_performing_doctor_id.id))
                paid_records = self.env['trinity.examination'].search(paid_domain)
                payout_amount = sum(record.examination_type_id_price.price if record.examination_type_id_price else 0 for record in paid_records)
                payout_count = len(paid_records)

                # Calculate pending (invoices but not paid) for all times
                # Get all unpaid invoices and their associated examinations
                Invoice = self.env['kojto.finance.invoices']
                unpaid_invoices = Invoice.search([
                    ('paid', '=', False),
                    ('examinations_in_invoice', '!=', False),
                ])

                # Collect all examinations from unpaid invoices
                pending_records = unpaid_invoices.mapped('examinations_in_invoice')

                # Filter by cost_bearer
                pending_records = pending_records.filtered(lambda e: e.cost_bearer_id.id == cost_bearer.id)

                # Filter by financingSource if needed
                if cost_bearer.financingSource and cost_bearer.financingSource.key == '2':
                    pending_records = pending_records.filtered(lambda e: e.e_examination_nrn)

                # Filter by doctor if specified
                if self.main_dr_performing_doctor_id:
                    pending_records = pending_records.filtered(
                        lambda e: e.main_dr_performing_doctor_id.id == self.main_dr_performing_doctor_id.id
                    )

                pending_amount = sum(record.examination_type_id_price.price if record.examination_type_id_price else 0 for record in pending_records)
                pending_count = len(pending_records)

                data['total_amount'].append(total_amount)
                data['total_count'].append(total_count)
                data['rejected_amount'].append(rejected_amount)
                data['rejected_count'].append(rejected_count)
                data['payout_amount'].append(payout_amount)
                data['payout_count'].append(payout_count)
                data['pending_amount'].append(pending_amount)
                data['pending_count'].append(pending_count)

            for metric, values in data.items():
                worksheet = worksheets[metric]
                for col, value in enumerate(values):
                    worksheet.write(row, col, value)

            row += 1

            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1

        workbook.close()

        output.seek(0)

        self.create_dashboard_content()

        attachment = self.env['ir.attachment'].create({
            'name': 'monthly_data_by_metric_and_costbearer.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue()).decode(),
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'new',
        }

    def default_date_start(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        return first_day_of_current_month

    def default_date_end(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        first_day_of_next_month = first_day_of_current_month + relativedelta(months=1)
        last_day_of_current_month = first_day_of_next_month - timedelta(days=1)
        return last_day_of_current_month

    def forward_one_month(self):
        self.ensure_one()
        next_month = self.date_start + relativedelta(months=1)
        self.date_start = next_month.replace(day=1)
        self.date_end = self.date_end + relativedelta(months=1)
        next_month_end = self.date_end + relativedelta(months=1)
        self.date_end = next_month_end.replace(day=1) - relativedelta(days=1)
        self.create_dashboard_content()

    def backward_one_month(self):
        self.ensure_one()
        previous_month = self.date_start - relativedelta(months=1)
        self.date_start = previous_month.replace(day=1)
        next_month = self.date_start + relativedelta(months=1)
        self.date_end = next_month.replace(day=1) - relativedelta(days=1)
        self.create_dashboard_content()

    def forward_one_year(self):
        self.ensure_one()
        self.date_start = (self.date_start + relativedelta(years=1)).replace(day=1)
        self.date_end = self.date_end + relativedelta(years=1)
        next_year_end = (self.date_end + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        self.date_end = next_year_end
        self.create_dashboard_content()

    def backward_one_year(self):
        self.ensure_one()
        self.date_start = (self.date_start - relativedelta(years=1)).replace(day=1)
        self.date_end = self.date_end - relativedelta(years=1)
        previous_year_end = (self.date_end + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        self.date_end = previous_year_end
        self.create_dashboard_content()

    def set_dates_to_current_week(self):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        self.date_start = start_of_week
        self.date_end = end_of_week
        self.create_dashboard_content()

    def set_dates_to_today(self):
        today = date.today()
        self.date_start = today
        self.date_end = today
        self.create_dashboard_content()

    def set_dates_to_current_month(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        self.date_start = first_day_of_current_month
        first_day_of_next_month = first_day_of_current_month + relativedelta(months=1)
        last_day_of_current_month = first_day_of_next_month - timedelta(days=1)
        self.date_end = last_day_of_current_month
        self.create_dashboard_content()

    def set_dates_to_current_year(self):
        today = date.today()
        first_day_of_current_year = today.replace(day=1, month=1)
        last_day_of_current_year = today.replace(day=31, month=12)
        self.date_start = first_day_of_current_year
        self.date_end = last_day_of_current_year
        self.create_dashboard_content()

class TrinityDashboardContents(models.Model):
    _name = 'trinity.dashboard.contents'
    _description = 'Trinity Dashboard Contents'

    cost_bearer = fields.Char(string='Контрагент')
    dashboard_date_start = fields.Date(related='dashboard_id.date_start', string='От дата', readonly=True)
    dashboard_date_end = fields.Date(related='dashboard_id.date_end', string='До дата', readonly=True)
    total_amount = fields.Float(string='Изработени')
    total_count = fields.Integer(string='Изработени')
    rejected_amount = fields.Float(string='Отхвърлени')
    rejected_count = fields.Integer(string='Отхвърлени')
    payout_amount = fields.Float(string='Изплатени')
    payout_count = fields.Integer(string='Изплатени')
    pending_amount = fields.Float(string='Неплатени')
    pending_count = fields.Integer(string='Неплатени')

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.BGN'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    dashboard_id = fields.Many2one('trinity.dashboard', string='Dashboard', ondelete='cascade')
    position = fields.Integer(string='#')

    records_in_dashboard_content = fields.Many2many('trinity.examination', string='Прегледани този месец', compute='_compute_records_in_dashboard_content')

    records_in_dashboard_payout_content = fields.Many2many('trinity.examination', string='Изплатени прегледи', compute='_compute_records_in_dashboard_payout_content')

    records_in_dashboard_rejected_content = fields.Many2many('trinity.examination', string='Отхвърлени прегледи', compute='_compute_records_in_dashboard_rejected_content')

    records_in_dashboard_pending_content = fields.Many2many('trinity.examination', string='Фактурирани/неплатени прегледи', compute='_compute_records_in_dashboard_pending_content')

    @api.depends('cost_bearer', 'dashboard_id.date_start', 'dashboard_id.date_end', 'dashboard_id.main_dr_performing_doctor_id')
    def _compute_records_in_dashboard_content(self):
        Examination = self.env['trinity.examination']
        for line in self:
            if not line.dashboard_id:
                line.records_in_dashboard_content = [(6, 0, [])]
                continue

            domain = []
            if line.dashboard_id.date_start:
                domain.append(('examination_open_dtm', '>=', line.dashboard_id.date_start))
            if line.dashboard_id.date_end:
                domain.append(('examination_open_dtm', '<=', line.dashboard_id.date_end))
            if line.dashboard_id.main_dr_performing_doctor_id:
                domain.append(('main_dr_performing_doctor_id', '=', line.dashboard_id.main_dr_performing_doctor_id.id))

            if line.cost_bearer and line.cost_bearer != 'ОБЩО':
                domain.append(('cost_bearer_id.name', '=', line.cost_bearer))

            examinations = Examination.search(domain)
            line.records_in_dashboard_content = [(6, 0, examinations.ids)]

    @api.depends('cost_bearer', 'dashboard_id.date_start', 'dashboard_id.date_end', 'dashboard_id.main_dr_performing_doctor_id')
    def _compute_records_in_dashboard_payout_content(self):
        Examination = self.env['trinity.examination']
        for line in self:
            if not line.dashboard_id:
                line.records_in_dashboard_payout_content = [(6, 0, [])]
                continue

            domain = [
                ('examination_paid_date', '!=', False),
                ('rejected_payment', '!=', 'yes'),
            ]
            if line.dashboard_id.date_start:
                domain.append(('examination_paid_date', '>=', line.dashboard_id.date_start))
            if line.dashboard_id.date_end:
                domain.append(('examination_paid_date', '<=', line.dashboard_id.date_end))
            if line.dashboard_id.main_dr_performing_doctor_id:
                domain.append(('main_dr_performing_doctor_id', '=', line.dashboard_id.main_dr_performing_doctor_id.id))
            if line.cost_bearer and line.cost_bearer != 'ОБЩО':
                domain.append(('cost_bearer_id.name', '=', line.cost_bearer))

            paid_examinations = Examination.search(domain)
            line.records_in_dashboard_payout_content = [(6, 0, paid_examinations.ids)]

    @api.depends('cost_bearer', 'dashboard_id.date_start', 'dashboard_id.date_end', 'dashboard_id.main_dr_performing_doctor_id')
    def _compute_records_in_dashboard_rejected_content(self):
        Examination = self.env['trinity.examination']
        for line in self:
            if not line.dashboard_id:
                line.records_in_dashboard_rejected_content = [(6, 0, [])]
                continue

            domain = [('rejected_payment', '!=', 'no')]
            if line.dashboard_id.date_start:
                domain.append(('examination_paid_date', '>=', line.dashboard_id.date_start))
            if line.dashboard_id.date_end:
                domain.append(('examination_paid_date', '<=', line.dashboard_id.date_end))
            if line.dashboard_id.main_dr_performing_doctor_id:
                domain.append(('main_dr_performing_doctor_id', '=', line.dashboard_id.main_dr_performing_doctor_id.id))
            if line.cost_bearer and line.cost_bearer != 'ОБЩО':
                domain.append(('cost_bearer_id.name', '=', line.cost_bearer))

            rejected_examinations = Examination.search(domain)
            line.records_in_dashboard_rejected_content = [(6, 0, rejected_examinations.ids)]

    @api.depends('cost_bearer', 'dashboard_id.date_start', 'dashboard_id.date_end', 'dashboard_id.main_dr_performing_doctor_id')
    def _compute_records_in_dashboard_pending_content(self):
        Invoice = self.env['kojto.finance.invoices']
        for line in self:
            if not line.dashboard_id:
                line.records_in_dashboard_pending_content = [(6, 0, [])]
                continue

            # Get all unpaid invoices and their associated examinations
            unpaid_invoices = Invoice.search([
                ('paid', '=', False),
                ('examinations_in_invoice', '!=', False),
            ])

            # Collect all examinations from unpaid invoices
            pending_examinations = unpaid_invoices.mapped('examinations_in_invoice')

            # Filter by doctor if specified
            if line.dashboard_id.main_dr_performing_doctor_id:
                pending_examinations = pending_examinations.filtered(
                    lambda e: e.main_dr_performing_doctor_id.id == line.dashboard_id.main_dr_performing_doctor_id.id
                )

            # Filter by cost_bearer if specified
            if line.cost_bearer and line.cost_bearer != 'ОБЩО':
                pending_examinations = pending_examinations.filtered(
                    lambda e: e.cost_bearer_id.name == line.cost_bearer
                )

            line.records_in_dashboard_pending_content = [(6, 0, pending_examinations.ids)]

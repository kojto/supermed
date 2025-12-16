from odoo import models, fields, api

class TrinityFinancialReportContents(models.Model):
    _name = 'trinity.financial.report.contents'
    _description = 'Trinity Financial Report Contents'

    financial_report_id = fields.Many2one('trinity.financial.reports', string='Financial Report', ondelete='cascade', required=True)

    unit = fields.Char(string='Услуга')
    unit_code = fields.Char(string='Код услуга')
    unit_quantity = fields.Float(string='Брой', digits=(16, 0))
    unit_price = fields.Float(string='Ед. цена лв.', digits=(16, 2))
    pre_vat_total = fields.Float(string='Обща цена лв. без ДДС', digits=(16, 2), compute='_compute_pre_vat_total')
    vat_rate = fields.Float(string='ДДС ставка %', digits=(16, 2), default=0.0)
    vat_amount = fields.Float(string='ДДС сума лв.', digits=(16, 2), compute='_compute_vat_amount')
    total_price = fields.Float(string='Обща цена лв.', digits=(16, 2), compute='_compute_total_price')

    @api.depends('unit_price', 'unit_quantity')
    def _compute_pre_vat_total(self):
        for record in self:
            record.pre_vat_total = record.unit_price * record.unit_quantity

    @api.depends('pre_vat_total', 'vat_rate')
    def _compute_vat_amount(self):
        for record in self:
            record.vat_amount = record.pre_vat_total * record.vat_rate / 100

    @api.depends('unit_price', 'unit_quantity', 'pre_vat_total', 'vat_rate')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.pre_vat_total + record.vat_amount

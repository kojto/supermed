# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.fields import Date
import datetime

class TrinityExaminationType(models.Model):
    _name = 'trinity.examination.type'
    _description = 'Examination Type'
    _rec_name = 'name'
    _order = 'top_choice desc, name asc'

    name = fields.Char(string='Име', compute='compute_name', store=True)
    nhif_procedure_code = fields.Char(related='diagnosticReport_code.meta_nhif_code', string='Код НЗОК процедура')
    examination_type = fields.Char(string='Examination Type', required=True)

    prices = fields.One2many('trinity.examination.type.prices', 'examination_type_id', string='Prices', context={'active_test': False},     order="active_from desc")

    cost_bearer_id = fields.Many2one('trinity.costbearer', string='Носител на разходите', store=True, required=True)
    cost_bearer_id_full_name = fields.Char(related='cost_bearer_id.full_name')
    financingSource = fields.Many2one(related='cost_bearer_id.financingSource')
    costbearer_code = fields.Char(string='Код на ДЗОФ')

    habilitation_required = fields.Selection([('hab', 'За хабилитирани'), ('nonhab', 'За не-хабилитани'), ('both', 'За всички')], string='Необходима хабилитация', default='both')

    valid_for_specialities = fields.Many2many('trinity.nomenclature.cl006', string='За специалности:', help='Изберете една или повече специалности за която е валиден шаблонът')

    active = fields.Boolean(string='Активна', default=True, store=True)
    top_choice = fields.Boolean(string='Топ избор', default=False)
    is_valid_for_all_patients = fields.Boolean(string='Валидна за всички пациенти', default=False)

    @api.depends('prices')
    def _compute_active(self):
        for record in self:
            active = False
            for price in record.prices:
                if price.active:
                    active = True
                    break
            record.active = active

    diagnosticReport_code = fields.Many2one('trinity.nomenclature.cl022', string='Процедура', required=True)
    diagnosticReport = fields.Boolean(string='Е диагностична процедура', required=True, default='false')
    diagnosticReport_status = fields.Many2one('trinity.nomenclature.cl083', string='Статус на диагн. процедура', required=True, default=lambda self: self.env['trinity.nomenclature.cl083'].search([('key', '=', '30')], limit=1).id)
    diagnosticReport_numberPerformed = fields.Integer(string='Diagnostic Report Count', required=True, default='1')

    secondary_examination = fields.Boolean(string='Е вторичен', required=True, default='false')
    secondary_to_examination_type = fields.Many2one('trinity.examination.type', string='Вторичен към следния първичен')
    primary_to_examination_type = fields.Many2one('trinity.examination.type', string='Първичен към следния вторичен')

    examination_purpose = fields.Many2one('trinity.nomenclature.cl047', string='Examination Purpose', default=lambda self: self.env['trinity.nomenclature.cl047'].search([('key', '=', '1')], limit=1).id)
    examination_class = fields.Many2one('trinity.nomenclature.cl049', string='Клас на прегледа', default=lambda self: self.env['trinity.nomenclature.cl049'].search([('key', '=', '1')], limit=1).id)

    @api.depends('examination_type', 'cost_bearer_id', 'diagnosticReport_code')
    def compute_name(self):
        for rec in self:
            cost_bearer_name = rec.cost_bearer_id.name if rec.cost_bearer_id else ''
            procedure_key = rec.diagnosticReport_code.key if rec.diagnosticReport_code else ''
            rec.name = f'{cost_bearer_name} - {rec.examination_type} - {procedure_key}'

class TrinityExaminationTypePrices(models.Model):
    _name = 'trinity.examination.type.prices'
    _description = 'Examination Type Prices'
    _rec_name = 'price'
    _order = 'active_from desc, price desc'

    examination_type_id = fields.Many2one('trinity.examination.type', string='Examination Type', required=True, ondelete='cascade')
    price = fields.Float(string='Цена', required=True)
    active_from = fields.Date(string='Активна от', required=True)
    active_until = fields.Date(string='Активна до')
    price_onsite = fields.Float(string='Цена на място')
    currency_id = fields.Many2one('res.currency', string='Валута', required=True, default=lambda self: self.env.company.currency_id if self.env.company else None)

    active = fields.Boolean(string='Активна', compute='_compute_active', store=True)

    @api.depends('active_from', 'active_until')
    def _compute_active(self):
        today = Date.today()
        for record in self:
            is_active = True
            if record.active_from and today < record.active_from:
                is_active = False
            if record.active_until and today > record.active_until:
                is_active = False
            record.active = is_active

    _sql_constraints = [
        ('unique_price_per_period', 'unique(examination_type_id, active_from, active_until)', 'Only one price can be active for the same period!')
    ]

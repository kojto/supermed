# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.fields import Date

class TrinityCostbearer(models.Model):
    _name = 'trinity.costbearer'
    _description = 'разходоносители'
    _rec_name = 'name'

    name = fields.Char(string='Име', required=True)
    full_name = fields.Char(string='Пълно име')
    vat_number = fields.Char(string='ЕИК', required=True)
    financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Вид финансиране', default=lambda self: self.env['trinity.nomenclature.cl069'].search([('key', '=', '2')], limit=1))

    associated_contact_id = fields.Many2one('kojto.contacts', string='Свързан контакт')

    first_name = fields.Char(string='Име', required=True)
    middle_name = fields.Char(string='Бащино')
    last_name = fields.Char(string='Фамилия')
    email = fields.Char(string='Емейл')
    phone = fields.Char(string='телефон')

    address_line = fields.Char(string='Адрес (първи ред)')
    address_line2 = fields.Char(string='Адрес (първи ред)')
    city = fields.Char(string='Населено място')
    state_id = fields.Char(string='Област')
    zip_code = fields.Char(string='Пощ. код')
    country_id = fields.Char(string='Държава')

    attach = fields.Binary(string='Attach')
    attach_char = fields.Char(string="Договор")

    active = fields.Boolean(string='Активна', default=True, compute='_compute_active', store=True)
    active_from = fields.Date(string='Активна от')
    active_until = fields.Date(string='Активна до')

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

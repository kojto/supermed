# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrinityMedicalFacilityDoctors(models.Model):
    _name = 'trinity.medical.facility.doctors'
    _description = 'Trinity Medical Facility Doctors'
    _rec_name = 'full_name_with_uin'

    doctor_id = fields.Char(string='УИН', required=True)
    active = fields.Boolean(string='Активен', default=True)
    is_administrator = fields.Boolean(string='Администратор', default=False)
    user_id = fields.Many2one('res.users', string='Сързан потребител')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id, copy=False)

    title = fields.Selection([('г-н', 'г-н'),('г-жа', 'г-жа'),('д-р', 'д-р'),('доц. д-р', 'доц. д-р'),('проф. д-р', 'проф. д-р')], string='Титла', default='д-р', required=True)
    first_name = fields.Char(string='Име', required=True)
    middle_name = fields.Char(string='Презиме')
    last_name = fields.Char(string='Фамилия', required=True)
    initials = fields.Char(string='Инициали', size=3)
    full_name = fields.Char(string='Пълно име', store=True, compute='compute_full_name')
    full_name_with_uin = fields.Char(string='Име със УИН', store=True, compute='compute_full_name_with_id')
    email = fields.Char(string='Имейл')
    private_email = fields.Char(string='Личен имейл')
    phone = fields.Char(string='Телефон')
    identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    identifier = fields.Char(string='Идентификатор')
    hospital_no = fields.Char(string='№ ЛЗ')
    hospital_name = fields.Char(string='ЛЗ')
    birth_date = fields.Date(string='Дата на раждане')
    gender = fields.Many2one('trinity.nomenclature.cl001', string='Пол')

    deductions = fields.One2many('trinity.medical.facility.doctors.deductions', 'doctor_id', string='Удръжки')

    nhif_ContractNo = fields.Char(string='Номер на договор с НЗОК')
    nhif_ContractDate = fields.Date(string='Дата на договор с НЗОК')
    nhif_Number = fields.Char(string='Номер в НЗОК')

    token_certificate = fields.Text(string='Сертификат на ел. подпис')
    accessToken = fields.Char(string='Токен за вход в НЗИС')
    expiresOnDatetime = fields.Datetime(string='Валиден до', default='2000-01-01 00:00:00')

    url_logo = fields.Char(string='URL към лого')

    address_line = fields.Char(string='Адрес ред 1')
    address_line2 = fields.Char(string='Адрес ред 2')
    city = fields.Char(string='Град')
    county_bulgarian = fields.Many2one('trinity.nomenclature.cl041', string='Област')
    country_bulgarian = fields.Many2one('trinity.nomenclature.cl005', string='Държава')
    ekatte_key = fields.Many2one('trinity.nomenclature.cl044', string='ЕКАТТЕ №')
    rhifareanumber_key = fields.Many2one('trinity.nomenclature.cl029', string='РЗОК № на област')
    zip_code = fields.Char(string='Пощенски код')

    qualification_code = fields.Many2one('trinity.nomenclature.cl006', string='Код на специалност')
    qualification_code_nhif = fields.Char(related='qualification_code.meta_nhif_code')
    description_bg = fields.Char(related='qualification_code.description')
    habilitation = fields.Boolean(string='Хабилитация', default=False)

    sender_type = fields.Many2one('trinity.nomenclature.cl018', string='Тип подател', default=lambda self: self.env['trinity.nomenclature.cl018'].search([('key', '=', '1')], limit=1))

    related_cash_bank_account_id = fields.Many2one('kojto.base.bank.accounts', string='Касов апарат', domain="[('contact_id', '=', 1), ('account_type', '=', 'cash')]")

    @api.depends('doctor_id', 'title', 'first_name', 'middle_name', 'last_name')
    def compute_full_name_with_id(self):
        for doctor in self:
            full_name = f"{doctor.title if doctor.title else ''} {doctor.first_name if doctor.first_name else ''} {doctor.middle_name if doctor.middle_name else ''} {doctor.last_name if doctor.last_name else ''}"
            doctor.full_name_with_uin = f"{full_name} - УИН: {doctor.doctor_id}"

    @api.constrains('doctor_id')
    def _restrict_duplicates(self):
        for rec in self:
            duplicates = self.env['trinity.medical.facility.doctors'].search(
                [('doctor_id', '=', rec.doctor_id), ('id', '!=', rec.id)])
            if duplicates:
                raise ValidationError(
                    _(f'Този УИН {rec.doctor_id} вече се използва'))

    @api.depends('title', 'first_name', 'middle_name', 'last_name')
    def compute_full_name(self):
        for record in self:
            record.full_name = f"{record.title if record.title else ''} {record.first_name if record.first_name else ''} {record.middle_name if record.middle_name else ''} {record.last_name if record.last_name else ''}"


class TrinityMedicalFacilityDoctorsDeductions(models.Model):
    _name = 'trinity.medical.facility.doctors.deductions'
    _description = 'Trinity Medical Facility Doctors Deductions'

    doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар')

    deduction = fields.Float(string='Удръжка в лв.', digits=(5, 2))
    deduction_type = fields.Selection([('absolute', 'Абсолютна'), ('percent', 'Процентна')], string='Тип на удръжката')
    deduction_description = fields.Char(string='Описание на удръжката')

    active = fields.Boolean(string='Активна', default=True)
    active_from = fields.Date(string='Активна от')
    active_until = fields.Date(string='Активна до')


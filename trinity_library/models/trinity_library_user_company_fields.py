# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrinityLibraryUserCompanyFields(models.AbstractModel):
    _name = "trinity.library.user.company.fields"
    _description = "Trinity Library User Company Fields"

    def _compute_doctor_id(self):
        Doctor = self.env['trinity.medical.facility.doctors']
        for record in self:
            doctor = Doctor.search([('user_id', '=', record.user_id.id)], limit=1) if record.user_id else False
            if not doctor:
                doctor = Doctor.search([('is_administrator', '=', True)], limit=1)
            record.doctor_id = doctor or False

    def _compute_hospital_id(self):
        Hospital = self.env['trinity.medical.facility']
        for record in self:
            hospital = Hospital.search([('hospital_id', '=', record.company_id.id)], limit=1) if record.company_id else False
            record.hospital_id = hospital or False

    user_id = fields.Many2one('res.users', string='Current User', default=lambda self: self.env.user, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id, copy=False)

    company_vat = fields.Char(related='company_id.vat', string='Company VAT')
    company_name = fields.Char(related='company_id.name', string='Company Name')
    company_managing_director = fields.Char(related='hospital_id.managing_director', string='МОЛ')
    company_street = fields.Char(related='company_id.street', string='Име на фирма')
    company_zip = fields.Char(related='company_id.zip', string='пк')
    company_city = fields.Char(related='company_id.city', string='град')
    company_country = fields.Many2one(related='company_id.country_id', string='държава')
    company_iban = fields.Char(related='hospital_id.IBAN_no.IBAN', string='IBAN')
    company_bic = fields.Char(related='hospital_id.bic_code', string='BIC')
    company_hospital_no = fields.Char(related='hospital_id.hospital_no', string='№ ЛЗ')

    doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', compute='_compute_doctor_id', copy=False)
    hospital_id = fields.Many2one('trinity.medical.facility', string='Лечебно заведение', compute='_compute_hospital_id', copy=False)

    user_token_expiresOnDatetime = fields.Datetime(related='doctor_id.expiresOnDatetime', string='Token Expiration Date')
    user_token_certificate = fields.Text(related='doctor_id.token_certificate', copy=False)
    user_token_is_expired = fields.Boolean(string="User Token is expired", default=False)

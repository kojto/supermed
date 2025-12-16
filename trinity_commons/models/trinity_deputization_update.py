# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import uuid
import logging

_logger = logging.getLogger(__name__)

class TrinityDeputizationUpdate(models.Model):
    _name = 'trinity.deputization.update'
    _description = 'Trinity Deputization Update'
    _rec_name = 'deputization_update_lrn'
    _inherit = ["trinity.library.nhif.qes"]

    deputization_update_lrn = fields.Char(string='Запис №', required=True, default=lambda self: self.generate_deputization_update_lrn(), copy=False)

    performer_pmi = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)
    performer_practiceNumber = fields.Char(related='hospital_id.hospital_no', string='№ ЛЗ', copy=False)
    performer_qualification_code = fields.Many2one(related='performer_pmi.qualification_code', string='Специалност')
    performer_qualification_code_nhif = fields.Char(related='performer_pmi.qualification_code_nhif', string='Специалност по НЗОК')
    performer_role = fields.Many2one('trinity.nomenclature.cl023', string='Роля на лекаря', default=lambda self: self.env['trinity.nomenclature.cl023'].search([('key', '=', '1')], limit=1))

    performer_pmiDeputy = fields.Many2one('trinity.medical.facility.doctors', required=True, string="Заместник")
    performer_pmiDeputy_qualification_code = fields.Many2one(related='performer_pmiDeputy.qualification_code', string='Специалност')
    performer_pmiDeputy_qualification_code_nhif = fields.Char(related='performer_pmiDeputy.qualification_code_nhif', string='Специалност по НЗОК')

    startDate = fields.Date(string='От дата:', required=True, default=lambda self: self.default_startDate() if not self.startDate else False)
    endDate = fields.Date(string='До дата:', required=True, default=lambda self: self.default_endDate() if not self.endDate else False)

    include = fields.Boolean(string='Включително', default=True)

    # C013 XML FIELDS
    C013 = fields.Text(string='C013', copy=False)
    C013_signed = fields.Char(string='C013 Signed Text', default='not signed', copy=False)
    SignedInfo_C013 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_C013_signature = fields.Char(string="SignedInfo signature", copy=False)

    C014 = fields.Text(string='C014', copy=False)

    def default_startDate(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        return first_day_of_current_month

    def default_endDate(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        first_day_of_next_month = first_day_of_current_month + relativedelta(months=1)
        last_day_of_current_month = first_day_of_next_month - timedelta(days=1)
        return last_day_of_current_month

    @api.model
    def generate_deputization_update_lrn(self):
        date_today = datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.deputization.update'].sudo().search(
            [('deputization_update_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='deputization_update_lrn desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.deputization_update_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1
        lrn_value = f'DEPU-{date_today}-{current_company_vat}-{sequence_number:04d}'
        return lrn_value

    #########################
    ########## C013 #########
    #########################

    @api.onchange('deputization_update_lrn', 'performer_pmi', 'performer_pmiDeputy', 'performer_qualification_code', 'performer_role', 'performer_practiceNumber', 'endDate', 'startDate')
    def compute_C013(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            C013 = f"""<?xml version="1.0" encoding="UTF-8"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-P001.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.performer_pmi.doctor_id if self.performer_pmi.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="C013"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:pmi value="{self.performer_pmi.doctor_id if self.performer_pmi else ''}"/>
                    <nhis:pmiDeputy value="{self.performer_pmiDeputy.doctor_id if self.performer_pmiDeputy else ''}"/>
                    <nhis:qualification value="{self.performer_qualification_code.key if self.performer_qualification_code.key else ''}"/>
                    <nhis:role value="{self.performer_role if self.performer_role else ''}"/>
                    <nhis:practiceNumber value="{self.performer_practiceNumber if self.performer_practiceNumber else ''}"/>
                    <nhis:period>
                        <nhis:startDate value="{self.startDate.strftime('%Y-%m-%d')}"/>
                        <nhis:endDate value="{self.endDate.strftime('%Y-%m-%d')}"/>
                        <nhis:include value="{self.include}"/>
                    </nhis:period>
                </nhis:contents>
            </nhis:message>"""

        self.C013 = C013.replace("False", "false").replace("True", "true")
        self.sign_C013()

    def getSignatureC013(self):
        return

    def sign_C013(self, field_name='C013', signedinfo='SignedInfo_C013', is_signed='C013_signed', signedinfo_signature='SignedInfo_C013_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    # Download C013
    def action_download_C013(self):
        return self.download_file('C013')

    # POST signed C013.xml to NZIS API
    def C013_api_request(self):
        # Search for the record "C013_api_request" in trinity.communicator
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'C013_api_request')], limit=1)

        if communicator_record:
            # Use the values from the communicator record
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value

            self.make_api_post_request(field_origin, url, field_response)

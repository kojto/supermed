# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError, UserError
from xml.etree import ElementTree as ET
import datetime
import uuid
import logging

_logger = logging.getLogger(__name__)

class TrinityDeputizationCheck(models.Model):
    _name = 'trinity.deputization.check'
    _description = 'Trinity Deputization Check'
    _rec_name = 'deputization_check_lrn'
    _inherit = ["trinity.library.nhif.qes"]

    deputization_check_lrn = fields.Char(string='Запис №', required=True, default=lambda self: self.generate_deputization_check_lrn(), readonly=True, copy=False)

    performer_pmi = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)
    performer_practiceNumber = fields.Char(related='hospital_id.hospital_no', string='№ ЛЗ', copy=False)

    startDate = fields.Date(string='От дата:')
    endDate = fields.Date(string='До дата:')

    include = fields.Boolean(string='Включително', default=True)

    # C015 XML FIELDS
    C015 = fields.Text(string='C015', copy=False)
    C015_signed = fields.Char(string='C015 Signed Text', default='not signed', copy=False)
    SignedInfo_C015 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_C015_signature = fields.Char(string="SignedInfo signature", copy=False)

    C016 = fields.Text(string='C016', copy=False)

    deputizationResponce = fields.Text(string='Замествания', readonly=True, copy=False)

    @api.model
    def generate_deputization_check_lrn(self):
        date_today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.deputization.check'].sudo().search(
            [('deputization_check_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='deputization_check_lrn desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.deputization_check_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1
        lrn_value = f'DEPU_CHECK-{date_today}-{current_company_vat}-{sequence_number:04d}'

        return lrn_value

    #########################
	########## C015 #########
    #########################

    @api.onchange('deputization_check_lrn', 'performer_pmi')
    def compute_C015(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            C015 = f"""<?xml version="1.0" encoding="UTF-8"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-P001.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.performer_pmi.doctor_id if self.performer_pmi.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="C015"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:pmi value="{self.performer_pmi.doctor_id if self.performer_pmi else ''}"/>
                </nhis:contents>
            </nhis:message>"""

        self.C015 = C015.replace("False", "false").replace("True", "true")
        self.sign_C015()

    def getSignatureC015(self):
        return

    def sign_C015(self, field_name='C015', signedinfo='SignedInfo_C015', is_signed='C015_signed', signedinfo_signature='SignedInfo_C015_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    # Download C015
    def action_download_C015(self):
        return self.download_file('C015')

    # POST signed C015.xml to NZIS API
    def C015_api_request(self):
        # Search for the record "C015_api_request" in trinity.communicator
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'C015_api_request')], limit=1)

        if communicator_record:
            # Use the values from the communicator record
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value

            self.make_api_post_request(field_origin, url, field_response)


    def check_response(self, response):
        try:
            xml_root = ET.fromstring(response.text)
        except ET.ParseError:
            if "401 Authorization Required" in response.text:
                raise UserError(_("НАПРАВЕТЕ ВРЪЗКА С НЗИС!"))
            return

        # List to store each deputizedBy block
        deputized_by_texts = []

        # Loop through each deputizedBy block
        for deputized_by in xml_root.findall('.//{https://www.his.bg}deputizedBy'):
            pmi = deputized_by.find('{https://www.his.bg}pmi').attrib['value']
            periods = deputized_by.findall('.//{https://www.his.bg}period')
            period_texts = []

            # Loop through each period block within the deputizedBy block
            for period in periods:
                start_date = period.find('{https://www.his.bg}startDate').attrib['value']
                end_date = period.find('{https://www.his.bg}endDate').attrib['value']
                period_text = f'от {start_date} до {end_date}'
                period_texts.append(period_text)

            # Concatenate the period texts
            period_text = '\n'.join(period_texts)

            # Combine pmi and period text
            deputized_by_text = f'------------\nУИН на заместник: {pmi}\n{period_text}\n------------'

            # Add the deputizedBy text to the list
            deputized_by_texts.append(deputized_by_text)

        # Concatenate all deputizedBy texts
        result = '\n\n'.join(deputized_by_texts)

        # Update the deputizationResponce field with the generated text
        self.write({'deputizationResponce': result})

import datetime
import logging
import uuid
import xml.etree.ElementTree as ET

from lxml import etree

from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class TrinityExamination(models.Model):
    _inherit = 'trinity.examination'

    H001 = fields.Text(string='H001', copy=False)
    H001_raw = fields.Text(string='H001 raw', copy=False)
    H001_signed = fields.Char(string='H001 Signed Text', default='not signed', copy=False)
    SignedInfo_H001 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_H001_signature = fields.Char(string="SignedInfo signature", copy=False)

    H002 = fields.Text(string='H002', copy=False)
    H002_raw = fields.Text(string='H002', copy=False, default='empty')

    error_type = fields.Char(string='Код на грешката', copy=False)
    error_reason = fields.Char(string='Грешка', copy=False)

    def getSignatureH001(self):
        self.compute_H001()
        return

    def compute_H001(self):
        for record in self:
            if record.error_type or record.error_reason:
                record.write({
                    'error_type': False,
                    'error_reason': False
                })
            current_datetime = datetime.datetime.now()
            uuid_value = str(uuid.uuid4())
            current_datetime_str = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            from_date_str = self.examination_open_dtm.strftime("%Y-%m-%d") if self.examination_open_dtm else ""
            to_date_str = self.examination_open_dtm.strftime("%Y-%m-%d") if self.examination_open_dtm else ""

            H001 = f"""
        <nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-H001.xsd">
            <nhis:header>
                <nhis:sender value="1"></nhis:sender>
                <nhis:senderId value="{self.main_dr_performing_doctor_id.doctor_id}"></nhis:senderId>
                <nhis:senderISName value="Supermed 1.0.1"></nhis:senderISName>
                <nhis:recipient value="4"></nhis:recipient>
                <nhis:recipientId value="NHIS"></nhis:recipientId>
                <nhis:messageId value="{uuid_value}"></nhis:messageId>
                <nhis:messageType value="H001"></nhis:messageType>
                <nhis:createdOn value="{current_datetime_str}"></nhis:createdOn>
            </nhis:header>
            <nhis:contents>
                <nhis:fromDate value="{from_date_str}"></nhis:fromDate>
                <nhis:toDate value="{to_date_str}"></nhis:toDate>
                <nhis:identifierType value="{self.patient_identifier_id.identifier_type.key if self.patient_identifier_id.identifier_type else ''}"></nhis:identifierType>
                <nhis:identifier value="{self.patient_identifier_id.identifier if self.patient_identifier_id.identifier else ''}"></nhis:identifier>
                <nhis:practiceNumber value="{self.hospital_id.hospital_no if self.hospital_id and self.hospital_id.hospital_no else ''}"></nhis:practiceNumber>
            </nhis:contents>
        </nhis:message>"""

            H001 = H001.replace("False", "false").replace("True", "true")
            self.H001 = H001
            self.sign_H001()

    def sign_H001(self, field_name='H001', signedinfo='SignedInfo_H001', is_signed='H001_signed', signedinfo_signature='SignedInfo_H001_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_H001(self):
        return self.download_file('H001')

    def H001_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'H001_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            return self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

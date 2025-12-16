import datetime
import logging
import uuid
import xml.etree.ElementTree as ET

from lxml import etree

from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class TrinityHospitalisationFetch(models.Model):
    _name = 'trinity.hospitalisation.fetch'
    _description = 'Trinity Hospitalisation Fetch'
    _rec_name = 'id'
    _inherit = ["trinity.library.nhif.qes"]

    fetch_nrnHospitalization = fields.Char(string='НРН хоспитализация', copy=False)
    fetch_fromDate = fields.Date(string='От дата', default=lambda self: date.today() - timedelta(days=1))
    fetch_toDate = fields.Date(string='До дата', default=lambda self: date.today())
    fetch_identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    fetch_identifier = fields.Char(string='Идентификатор')
    fetch_practiceNumber = fields.Char(string='Номер на практика', default='2203131524')

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)

    incoming_hospitalisation_ids = fields.One2many('trinity.hospitalisation.incoming', 'fetch_hospitalisation_id', string='Входящи хоспитализации')
    fetch_subject_full_name = fields.Char(string='Хоспитализации намерени за', compute='_compute_fetch_subject_full_name', store=False)

    @api.depends('fetch_identifier')
    def _compute_fetch_subject_full_name(self):
        for record in self:
            if record.fetch_identifier:
                patient_model = self.env['trinity.patient']
                existing_patient = patient_model.search([('identifier', '=', record.fetch_identifier)], limit=1)

                if existing_patient:
                    record.fetch_subject_full_name = f"{existing_patient.first_name or ''} {existing_patient.middle_name or ''} {existing_patient.last_name or ''}, ЕГН/ЛНЧ: {existing_patient.identifier}".strip()
                else:
                    record.fetch_subject_full_name = f"ЕГН/ЛНЧ: {record.fetch_identifier}"
            else:
                record.fetch_subject_full_name = ''

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
        return

    def fetch_new_hospitalisation(self):
        for record in self:
            record.incoming_hospitalisation_ids.unlink()

            default_identifier_type = self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1)

            hospital_no = record.hospital_id.hospital_no if record.hospital_id and record.hospital_id.hospital_no else ''

            record.write({
                'fetch_nrnHospitalization': False,
                'fetch_fromDate': date.today() - timedelta(days=1),
                'fetch_toDate': date.today(),
                'fetch_identifier_type': default_identifier_type.id if default_identifier_type else False,
                'fetch_identifier': False,
                'fetch_practiceNumber': hospital_no,
                'H001': False,
                'H001_raw': False,
                'H001_signed': 'not signed',
                'SignedInfo_H001': False,
                'SignedInfo_H001_signature': False,
                'H002': False,
                'H002_raw': 'empty',
                'error_type': False,
                'error_reason': False,
            })

    @api.onchange('fetch_nrnHospitalization', 'fetch_fromDate', 'fetch_toDate', 'fetch_identifier_type', 'fetch_identifier', 'fetch_practiceNumber')
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

            # Handle date fields - use current date if not provided
            from_date_str = self.fetch_fromDate.strftime("%Y-%m-%d") if self.fetch_fromDate else ""
            to_date_str = self.fetch_toDate.strftime("%Y-%m-%d") if self.fetch_toDate else ""

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
            <nhis:contents>"""

            # Add optional nrnHospitalization if provided
            if self.fetch_nrnHospitalization:
                H001 += f"""
                <nhis:nrnHospitalization value="{self.fetch_nrnHospitalization}"></nhis:nrnHospitalization>"""

            # Add conditional dates
            if from_date_str:
                H001 += f"""
                <nhis:fromDate value="{from_date_str}"></nhis:fromDate>"""

            if to_date_str:
                H001 += f"""
                <nhis:toDate value="{to_date_str}"></nhis:toDate>"""

            # Add conditional identifier fields
            if self.fetch_identifier_type and self.fetch_identifier:
                H001 += f"""
                <nhis:identifierType value="{self.fetch_identifier_type.key if self.fetch_identifier_type else ''}"></nhis:identifierType>
                <nhis:identifier value="{self.fetch_identifier if self.fetch_identifier else ''}"></nhis:identifier>"""

            # Add required practiceNumber
            H001 += f"""
                <nhis:practiceNumber value="{self.fetch_practiceNumber if self.fetch_practiceNumber else ''}"></nhis:practiceNumber>
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
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    def check_response(self, response, field_response, request_msg_type=None):
        try:
            xml_root = ET.fromstring(response.text)
        except ET.ParseError:
            if "401 Authorization Required" in response.text:
                self.write({
                    'error_type': 'Authorization Error',
                    'error_reason': 'НАПРАВЕТЕ ВРЪЗКА С НЗИС!'
                })
            return

        ns = {'nhis': 'https://www.his.bg'}

        error_tag = xml_root.find('.//nhis:error', ns)
        if error_tag is not None:
            error_type_tag = error_tag.find('./nhis:type', ns)
            reason_tag = error_tag.find('./nhis:reason', ns)
            error_type = error_type_tag.get('value') if error_type_tag is not None else "Error"
            error_reason = reason_tag.get('value') if reason_tag is not None else "Unknown reason"
            self.write({
                'error_type': error_type,
                'error_reason': error_reason
            })
            return

        self.write({
            'error_type': False,
            'error_reason': False
        })

        # Parse H002 response and create incoming hospitalisation records
        if field_response:
            self.write({
                field_response: response.text
            })

        hospitalization_incoming_model = self.env['trinity.hospitalisation.incoming']

        results_tags = xml_root.findall('.//nhis:results', ns)

        for result_tag in results_tags:
            if result_tag is not None:
                result_xml_str = ET.tostring(result_tag, encoding='unicode')
                hospitalization_vals = {
                    'H002': result_xml_str,
                    'fetch_hospitalisation_id': self.id
                }
                new_record = hospitalization_incoming_model.create(hospitalization_vals)
                new_record.parse_xml_and_set_fields()


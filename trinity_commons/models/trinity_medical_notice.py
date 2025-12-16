# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError, UserError
from xml.etree import ElementTree as ET
from datetime import timedelta
import datetime
import uuid
import logging

_logger = logging.getLogger(__name__)

class TrinityMedicalNotice(models.Model):
    _name = 'trinity.medical.notice'
    _description = 'Trinity Medical Notice'
    _rec_name = 'medicalNotice_lrn'
    _inherit = ["trinity.library.nhif.qes"]

    medicalNotice_basedOn_lrn = fields.Many2one('trinity.examination', string='Основано на амб. №', required=True)
    medicalNotice_basedOn_nrn = fields.Char(related='medicalNotice_basedOn_lrn.e_examination_nrn', string='Based On', readonly=True)

    medicalNotice_lrn = fields.Char(string='Медицинска бележка №', required=True, default=lambda self: self.generate_medicalNotice_lrn(), copy=False)
    response_nrnMedicalNotice = fields.Char(string='НРН на медицинска бележка')

    medicalNotice_reason = fields.Many2one('trinity.nomenclature.cl116', string='Място на провеждане на лечението', default=lambda self: self.env['trinity.nomenclature.cl068'].search([('key', '=', '1')], limit=1))
    medicalNotice_code = fields.Many2one(related='medicalNotice_basedOn_lrn.icd_code', string='Diagnosis Code')
    medicalNotice_fromDate = fields.Date(string='От Дата', default=lambda self: fields.Date.today())
    medicalNotice_toDate = fields.Date(string='До Дата', default=lambda self: fields.Date.today() + timedelta(days=1))
    medicalNotice_location = fields.Many2one('trinity.nomenclature.cl117', string='Място на провеждане на лечението', default=lambda self: self.env['trinity.nomenclature.cl117'].search([('key', '=', '1')], limit=1))
    medicalNotice_institution = fields.Char(string='Да послужи пред', default='училищните власти')
    medicalNotice_note = fields.Text(string='Бележка за Медицинско Уведомление')

    response_status = fields.Selection(selection=[('0', 'Неактивирана'), ('1', 'Активна'), ('2', 'Анулирана')], string='Статус', default='0')

    subject_identifier = fields.Many2one(related='medicalNotice_basedOn_lrn.patient_identifier_id', string='ЕГН/ЛНЧ/друг №')
    subject_identifierType = fields.Many2one(related='medicalNotice_basedOn_lrn.patient_identifier_type', string='Identifier Type')
    subject_nhifInsuranceNumber = fields.Char(string='NHIF Insurance Number')
    subject_birthDate = fields.Date(string='Birth Date', related='medicalNotice_basedOn_lrn.patient_birth_date')
    subject_gender = fields.Many2one(related='medicalNotice_basedOn_lrn.patient_gender', string='Пол')
    subject_age = fields.Float(related='medicalNotice_basedOn_lrn.patient_age')
    subject_given = fields.Char(string='Given Name', related='medicalNotice_basedOn_lrn.patient_first_name')
    subject_middle = fields.Char(string='Middle Name', related='medicalNotice_basedOn_lrn.patient_middle_name')
    subject_family = fields.Char(string='Family Name', related='medicalNotice_basedOn_lrn.patient_last_name')

    subject_full = fields.Char(string='Пациент', related='medicalNotice_basedOn_lrn.patient_full_name')

    # New fields with "address" prefix
    subject_country = fields.Many2one('trinity.nomenclature.cl005', related='medicalNotice_basedOn_lrn.patient_country')
    subject_county = fields.Many2one('trinity.nomenclature.cl041', related='medicalNotice_basedOn_lrn.patient_county')
    subject_city = fields.Char(string='City', related='medicalNotice_basedOn_lrn.patient_city')
    subject_postalCode = fields.Char(related='medicalNotice_basedOn_lrn.patient_zip_code')
    subject_phone = fields.Char(string='Телефонен Номер')
    subject_email = fields.Char(string='Имейл')

    # New fields with "performer" prefix
    performer_pmi = fields.Many2one(related='medicalNotice_basedOn_lrn.main_dr_performing_doctor_id')
    performer_pmi_first_name = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_first_name')
    performer_pmi_middle_name = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_middle_name')
    performer_pmi_last_name = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_last_name')
    performer_pmi_full_name = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_full_name')
    performer_pmiDeputy = fields.Char(string='Заместник на Изпълнителя PMI')
    performer_qualification_code = fields.Many2one(related='medicalNotice_basedOn_lrn.main_dr_performing_qualification_code')
    performer_qualification_code_nhif = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_qualification_code_nhif')
    performer_role = fields.Many2one(related='medicalNotice_basedOn_lrn.performer_role')
    performer_practiceNumber = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_practiceNumber')
    performer_phone = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_phone')
    performer_email = fields.Char(related='medicalNotice_basedOn_lrn.main_dr_performing_email')

    # Response
    response_sender = fields.Char(string='Sender')
    response_senderId = fields.Char(string='Sender ID')
    response_recipient = fields.Char(string='Recipient')
    response_recipientId = fields.Char(string='Recipient ID')
    response_messageId = fields.Char(string='Message ID')
    response_messageType = fields.Char(string='Message Type')
    response_createdOn = fields.Date(string='Created On')

    nrnMedicalNotice = fields.Char(string='НРН медицинска бележка', readonly=True)
    response_lrn = fields.Char(string='LRN', readonly=True)

    warnings_code = fields.Char(string='Code')
    warnings_description = fields.Char(string='Description')
    warnings_source = fields.Char(string='Source')
    warnings_nrnTarget = fields.Char(string='NRN Target')

    # XML FIELDS
    C041 = fields.Text(string='C041', copy=False)
    C041_signed = fields.Char(string='C041 Signed Text', default='not signed', copy=False)
    SignedInfo_C041 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_C041_signature = fields.Char(string="SignedInfo signature", copy=False)

    C045 = fields.Text(string='C045', copy=False)
    C045_signed = fields.Char(string='C045 Signed Text', default='not signed', copy=False)
    SignedInfo_C045 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_C045_signature = fields.Char(string="SignedInfo signature", copy=False)

    C042 = fields.Text(string='C042', copy=False)
    C046 = fields.Text(string='C046', copy=False)

    @api.model
    def generate_medicalNotice_lrn(self):
        date_today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.medical.notice'].sudo().search(
            [('medicalNotice_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='medicalNotice_lrn desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.medicalNotice_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1
        lrn_value = f'MN-{date_today}-{current_company_vat}-{sequence_number:04d}'
        return lrn_value

	# C041
    @api.onchange('medicalNotice_basedOn_lrn', 'medicalNotice_basedOn_nrn', 'medicalNotice_lrn', 'medicalNotice_reason', 'medicalNotice_code', 'medicalNotice_fromDate', 'medicalNotice_toDate', 'medicalNotice_location', 'medicalNotice_institution', 'medicalNotice_note', 'subject_identifier', 'subject_identifierType', 'subject_nhifInsuranceNumber', 'subject_birthDate', 'subject_gender', 'subject_age', 'subject_given', 'subject_middle', 'subject_family', 'subject_full', 'subject_country', 'subject_county', 'subject_city', 'subject_postalCode', 'subject_phone', 'subject_email', 'performer_pmi', 'performer_pmiDeputy', 'performer_qualification_code', 'performer_role', 'performer_practiceNumber', 'performer_phone', 'performer_email')
    def compute_C041(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            C041 = f"""<?xml version="1.0" encoding="UTF-8"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-P001.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.performer_pmi.doctor_id if self.performer_pmi.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="C041"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:medicalNotice>
                        <nhis:lrn value="{self.medicalNotice_lrn if self.medicalNotice_lrn else ''}"/>
                        <nhis:basedOn value="{self.medicalNotice_basedOn_nrn if self.medicalNotice_basedOn_nrn else ''}" />
                        <nhis:authoredOn value="{current_datetime.strftime('%Y-%m-%d')}"/>
                        <nhis:reason value="{self.medicalNotice_reason.key if self.medicalNotice_reason else ''}" />"""

            if record.medicalNotice_reason != '4':
                C041 += f"""
                        <nhis:code value="{self.medicalNotice_code.key if self.medicalNotice_code else ''}" />"""

            C041 += f"""
                        <nhis:fromDate value="{self.medicalNotice_fromDate.strftime('%Y-%m-%d') if self.medicalNotice_fromDate else ''}"/>"""

            if record.medicalNotice_reason != '4':
                C041 += f"""
                        <nhis:toDate value="{self.medicalNotice_toDate.strftime('%Y-%m-%d') if self.medicalNotice_toDate else ''}" />
                        <nhis:location value="{self.medicalNotice_location.key if self.medicalNotice_location else ''}" />"""

            C041 += f"""
                    <nhis:institution value="{self.medicalNotice_institution if self.medicalNotice_institution else ''}" />
                    </nhis:medicalNotice>
                    <nhis:subject>
                        <nhis:identifierType value="{self.subject_identifierType.key if self.subject_identifierType else ''}"/>
                        <nhis:identifier value="{self.subject_identifier.identifier if self.subject_identifier.identifier else ''}"/>
                        <nhis:birthDate value="{self.subject_birthDate if self.subject_birthDate else ''}"/>
                        <nhis:gender value="{self.subject_gender.key if self.subject_gender else ''}"/>
                        <nhis:name>
                            <nhis:given value="{self.subject_given if self.subject_given else ''}"/>
                            <nhis:family value="{self.subject_family if self.subject_family else ''}"/>
                        </nhis:name>
                        <nhis:address>
                            <nhis:country value="{self.subject_country.key if self.subject_country else ''}"/>
                            <nhis:county value="{self.subject_county.key if self.subject_county else ''}"/>
                            <nhis:city value="{self.subject_city if self.subject_city else ''}"/>
                        </nhis:address>
                        <nhis:various>
                            <nhis:age value="{self.subject_age if self.subject_age else ''}" />
                        </nhis:various>
                    </nhis:subject>
                    <nhis:performer>
                        <nhis:pmi value="{self.performer_pmi.doctor_id if self.performer_pmi else ''}"/>
                        <nhis:qualification value="{self.performer_qualification_code.key if self.performer_qualification_code.key else ''}"/>
                        <nhis:role value="{self.performer_role.key if self.performer_role else ''}"/>
                        <nhis:practiceNumber value="{self.performer_practiceNumber if self.performer_practiceNumber else ''}"/>
                        <nhis:phone value="{self.performer_phone if self.performer_phone else '0035924215555'}"/>
                    </nhis:performer>
                </nhis:contents>
            </nhis:message>"""

        self.C041 = C041
        self.sign_C041()
        self.compute_C045()

    cancelReason = fields.Char(string='Причина за анулирането', default='Пациентът няма нужда от бележката')

    # C045
    @api.onchange('response_nrnMedicalNotice')
    def compute_C045(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            C045 = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-C045.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.performer_pmi.doctor_id if self.performer_pmi.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="C045"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:nrnMedicalNotice value="{self.response_nrnMedicalNotice if self.response_nrnMedicalNotice else ''}" />
                    <nhis:cancelReason value="{self.cancelReason if self.cancelReason else ''}"/>
                </nhis:contents>
            </nhis:message>"""

        C045 = C045.replace("False", "false").replace("True", "true")

        self.C045 = C045
        self.sign_C045()

    def getSignatureC041(self):
        return

    def getSignatureC045(self):
        return

    def sign_C041(self, field_name='C041', signedinfo='SignedInfo_C041', is_signed='C041_signed', signedinfo_signature='SignedInfo_C041_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def sign_C045(self, field_name='C045', signedinfo='SignedInfo_C045', is_signed='C045_signed', signedinfo_signature='SignedInfo_C045_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    # Download C041
    def action_download_C041(self):
        return self.download_file('C041')

    # Download C045
    def action_download_C045(self):
        return self.download_file('C045')

    # POST signed C041.xml to NZIS API
    def C041_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'C041_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field

            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    def C045_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'C045_api_request')], limit=1)
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
                raise UserError("НАПРАВЕТЕ ВРЪЗКА С НЗИС!")
            return
        ns = {'nhis': 'https://www.his.bg'}
        nrnMedicalNotice = xml_root.find('.//nhis:nrnMedicalNotice', ns)
        status = xml_root.find('.//nhis:status', ns)
        error_reason = xml_root.find('.//nhis:reason', ns)
        message_type = xml_root.find('.//nhis:messageType', ns)

        if nrnMedicalNotice is not None and 'value' in nrnMedicalNotice.attrib:
            self.response_nrnMedicalNotice = nrnMedicalNotice.attrib['value']

        if message_type is not None and 'value' in message_type.attrib:
            msg_type_value = message_type.attrib['value']
            if msg_type_value == 'C042':
                self.response_status = '1'
            elif msg_type_value == 'C046':
                self.response_status = '2'

        self.compute_C045()

        if error_reason is not None and 'value' in error_reason.attrib:
            error_message = error_reason.attrib['value']
            raise UserError(error_message)

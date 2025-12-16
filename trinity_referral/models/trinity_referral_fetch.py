import datetime
import logging
import uuid
import xml.etree.ElementTree as ET

from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class TrinityReferralFetch(models.Model):
    _name = 'trinity.referral.fetch'
    _description = 'Trinity Referral Fetch'
    _rec_name = 'id'
    _inherit = ["trinity.library.nhif.qes"]

    fetch_nrnReferral = fields.Char(string='НРН направление', copy=False)
    fetch_identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    fetch_identifier = fields.Char(string='Идентификатор')
    fetch_subject_full_name = fields.Char(string='Направления издадени за', compute='_compute_fetch_subject_full_name', store=False)

    @api.depends('incomming_referral_ids', 'incomming_referral_ids.subject_full_name')
    def _compute_fetch_subject_full_name(self):
        for record in self:
            if record.incomming_referral_ids:
                record.fetch_subject_full_name = record.incomming_referral_ids[0].subject_full_name or ''
            else:
                record.fetch_subject_full_name = ''

    fetch_fromDate = fields.Date(string='От дата')
    fetch_toDate = fields.Date(string='До дата')
    fetch_category = fields.Many2one('trinity.nomenclature.cl014', default=lambda self: self.env['trinity.nomenclature.cl014'].search([('key', '=', 'R2')], limit=1))
    fetch_practiceNumber = fields.Char(string='Номер на практика', default='2203131524')

    incomming_referral_ids = fields.One2many('trinity.referral.incoming', 'fetch_referral_id', string='Входящи направления')

    R015 = fields.Text(string='R015', copy=False)
    R015_raw = fields.Text(string='R015 raw', copy=False)
    R015_signed = fields.Char(string='R015 Signed Text', default='not signed', copy=False)
    SignedInfo_R015 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_R015_signature = fields.Char(string="SignedInfo signature", copy=False)

    R016 = fields.Text(string='R016', copy=False)
    R016_raw = fields.Text(string='R016', copy=False, default='empty')

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)

    error_type = fields.Char(string='Код на грешката', copy=False)
    error_reason = fields.Char(string='Грешка', copy=False)

    def getSignatureR015(self):
        return

    def fetch_new_referral(self):

        for record in self:

            record.incomming_referral_ids.unlink()

            default_identifier_type = self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1)
            default_category = self.env['trinity.nomenclature.cl014'].search([('key', '=', 'R2')], limit=1)

            record.write({
                'fetch_nrnReferral': False,
                'fetch_identifier_type': default_identifier_type.id if default_identifier_type else False,
                'fetch_identifier': False,
                'fetch_fromDate': False,
                'fetch_toDate': False,
                'fetch_category': default_category.id if default_category else False,
                'fetch_practiceNumber': '2203131524',
                'R015': False,
                'R015_raw': False,
                'R015_signed': 'not signed',
                'SignedInfo_R015': False,
                'SignedInfo_R015_signature': False,
                'R016': False,
                'R016_raw': 'empty',
                'error_type': False,
                'error_reason': False,
            })

    @api.onchange('fetch_nrnReferral', 'fetch_identifier_type', 'fetch_identifier', 'fetch_fromDate', 'fetch_toDate', 'fetch_category', 'fetch_practiceNumber')
    def compute_R015(self):
        for record in self:
            if record.error_type or record.error_reason:
                record.write({
                    'error_type': False,
                    'error_reason': False
                })
            current_datetime = datetime.datetime.now()
            from_date = current_datetime - datetime.timedelta(days=90)
            uuid_value = str(uuid.uuid4())

            current_datetime_str = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            from_date_str = from_date.strftime("%Y-%m-%d")
            R015 = f"""
        <nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-X013.xsd">
            <nhis:header>
                <nhis:sender value="1"></nhis:sender>
                <nhis:senderId value="{self.main_dr_performing_doctor_id.doctor_id}"></nhis:senderId>
                <nhis:senderISName value="Supermed 1.0.1"></nhis:senderISName>
                <nhis:recipient value="4"></nhis:recipient>
                <nhis:recipientId value="NHIS"></nhis:recipientId>
                <nhis:messageId value="{uuid_value}"></nhis:messageId>
                <nhis:messageType value="R015"></nhis:messageType>
                <nhis:createdOn value="{current_datetime_str}"></nhis:createdOn>
            </nhis:header>
            <nhis:contents>
                <nhis:fromDate value="{from_date_str}"></nhis:fromDate>
                <nhis:identifierType value="{self.fetch_identifier_type.key if self.fetch_identifier_type else ''}"></nhis:identifierType>
                <nhis:identifier value="{self.fetch_identifier if self.fetch_identifier else ''}"></nhis:identifier>
                <nhis:practiceNumber value="{self.fetch_practiceNumber if self.fetch_practiceNumber else ''}"></nhis:practiceNumber>
            </nhis:contents>
        </nhis:message>"""

        R015 = R015.replace("False", "false").replace("True", "true")
        self.R015 = R015
        self.sign_R015()

    def sign_R015(self, field_name='R015', signedinfo='SignedInfo_R015', is_signed='R015_signed', signedinfo_signature='SignedInfo_R015_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_R015(self):
        return self.download_file('R015')

    def R015_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'R015_api_request')], limit=1)
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

        referral_incoming_model = self.env['trinity.referral.incoming']
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

        found_number_tag = xml_root.find('.//nhis:foundNumber', ns)
        if found_number_tag is not None:
            found_number = found_number_tag.get('value', '0')

        results_tags = xml_root.findall('.//nhis:results', ns)

        for result_tag in results_tags:
            if result_tag is not None:
                result_xml_str = ET.tostring(result_tag, encoding='unicode')
                referral_vals = {
                    'R016': result_xml_str,
                    'fetch_referral_id': self.id
                }
                new_record = referral_incoming_model.create(referral_vals)
                new_record.parse_xml_and_set_fields()

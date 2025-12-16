import datetime
import logging
import uuid
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class TrinityExaminationFetch(models.Model):
    _name = 'trinity.examination.fetch'
    _description = 'Trinity Examination Fetch'
    _inherit = ["trinity.library.nhif.qes"]

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)

    fetch_nrnExamination = fields.Char(string='НРН направление', copy=False)
    fetch_lrn = fields.Char(string='LRN', copy=False)
    fetch_identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    fetch_identifier = fields.Char(string='Идентификатор')
    fetch_fromDate = fields.Date(string='От дата')
    fetch_given_name = fields.Char(string='Име')
    fetch_middle_name = fields.Char(string='Презиме')
    fetch_family_name = fields.Char(string='Фамилия')

    fetch_search_method = fields.Selection([('nrn', 'НРН'), ('identifier_date', 'идентификатор и дата'), ('names_date', 'имена и дата'), ('lrn_date', 'LRN и дата'), ], string="Търсене по:", default='nrn')

    X005 = fields.Text(string='X005', copy=False)
    X005_raw = fields.Text(string='X005 raw', copy=False)
    X005_signed = fields.Char(string='X005 Signed Text', default='not signed', copy=False)
    SignedInfo_X005 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_X005_signature = fields.Char(string="SignedInfo signature", copy=False)
    X006 = fields.Text(string='X006', copy=False)
    X006_raw = fields.Text(string='X006', copy=False, default='empty')

    def getSignatureX005(self):
        return

    @api.onchange('fetch_nrnExamination', 'fetch_lrn', 'fetch_identifier_type', 'fetch_identifier', 'fetch_fromDate', 'fetch_given_name', 'fetch_middle_name', 'fetch_family_name', 'fetch_search_method')
    def compute_X005(self):
        for record in self:
            current_datetime = datetime.datetime.now()
            uuid_value = str(uuid.uuid4())
            current_datetime_str = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            contents_elements = []

            if self.fetch_search_method == 'nrn' and self.fetch_nrnExamination:
                contents_elements.append(f'<nhis:nrnExamination value="{self.fetch_nrnExamination}"></nhis:nrnExamination>')

            elif self.fetch_search_method == 'identifier_date' and self.fetch_identifier_type and self.fetch_identifier and self.fetch_fromDate:
                contents_elements.append(f'<nhis:identifierType value="{self.fetch_identifier_type.key}"></nhis:identifierType>')
                contents_elements.append(f'<nhis:identifier value="{self.fetch_identifier}"></nhis:identifier>')
                contents_elements.append(f'<nhis:openDate value="{self.fetch_fromDate:%Y-%m-%d}"></nhis:openDate>')

            elif self.fetch_search_method == 'names_date' and self.fetch_given_name and self.fetch_family_name and self.fetch_fromDate:
                contents_elements.append('<nhis:name>')
                contents_elements.append(f'<nhis:given value="{self.fetch_given_name}"></nhis:given>')
                if self.fetch_middle_name:
                    contents_elements.append(f'<nhis:middle value="{self.fetch_middle_name}"></nhis:middle>')
                contents_elements.append(f'<nhis:family value="{self.fetch_family_name}"></nhis:family>')
                contents_elements.append('</nhis:name>')
                contents_elements.append(f'<nhis:openDate value="{self.fetch_fromDate:%Y-%m-%d}"></nhis:openDate>')

            elif self.fetch_search_method == 'lrn_date' and self.fetch_lrn and self.fetch_fromDate:
                contents_elements.append(f'<nhis:lrn value="{self.fetch_lrn}"></nhis:lrn>')
                contents_elements.append(f'<nhis:openDate value="{self.fetch_fromDate:%Y-%m-%d}"></nhis:openDate>')

            if contents_elements:
                contents_xml = '\n                '.join(contents_elements)
                X005 = f"""<nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-X005.xsd">
            <nhis:header>
                <nhis:sender value="1"></nhis:sender>
                <nhis:senderId value="{self.main_dr_performing_doctor_id.doctor_id}"></nhis:senderId>
                <nhis:senderISName value="Supermed 1.0.1"></nhis:senderISName>
                <nhis:recipient value="4"></nhis:recipient>
                <nhis:recipientId value="NHIS"></nhis:recipientId>
                <nhis:messageId value="{uuid_value}"></nhis:messageId>
                <nhis:messageType value="X005"></nhis:messageType>
                <nhis:createdOn value="{current_datetime_str}"></nhis:createdOn>
            </nhis:header>
            <nhis:contents>
                {contents_xml}
            </nhis:contents>
        </nhis:message>"""
                self.X005 = X005.replace("False", "false").replace("True", "true")
                self.sign_X005()
            else:
                self.X005 = ""

    def sign_X005(self):
        self.prepare_first_digest('X005', 'SignedInfo_X005', 'X005_signed', 'SignedInfo_X005_signature')

    def action_download_X005(self):
        return self.download_file('X005')

    def X005_api_request(self):
        communicator = self.env['trinity.communicator'].search([('action_name', '=', 'X005_api_request')], limit=1)
        if communicator:
            self.make_api_post_request(communicator.field_origin, communicator.url_value, communicator.field_response, communicator.lrn_origin_field)

    def check_response(self, response, field_response, request_msg_type=None):
        if hasattr(response, 'text'):
            self.X006 = response.text
        else:
            self.X006 = str(response)

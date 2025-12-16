from odoo import api, models, fields
from odoo.exceptions import UserError
from xml.etree import ElementTree as ET
import datetime
from datetime import timezone, timedelta
import uuid
import logging

_logger = logging.getLogger(__name__)

class TrinityPrescriptionFetch(models.Model):
    _name = 'trinity.prescription.fetch'
    _description = 'Trinity Prescription Fetch'
    _rec_name = 'retrieve_nrnPrescription'
    _inherit = ["trinity.library.nhif.qes"]

    retrieve_nrnPrescription = fields.Char(string='Извличане по НРН на рецепта', required=True)

    P017 = fields.Text(string='P017', copy=False)
    P017_signed = fields.Char(string='P017 Signed Text', default='not signed', copy=False)
    SignedInfo_P017 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_P017_signature = fields.Char(string="SignedInfo signature", copy=False)

    P018 = fields.Text(string='P018', copy=False)

    @api.onchange('retrieve_nrnPrescription')
    def compute_P017(self):
        for record in self:
            current_datetime_utc = datetime.datetime.now(timezone.utc)
            bulgaria_tz = timezone(timedelta(hours=2))
            current_datetime_local = current_datetime_utc.astimezone(bulgaria_tz)
            timestamp_iso = current_datetime_local.isoformat(timespec='seconds')

            uuid_value = str(uuid.uuid4())

            P017 = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-P017.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.doctor_id.doctor_id if self.doctor_id and self.doctor_id.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="P017"/>
                    <nhis:createdOn value="{timestamp_iso}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:nrnPrescription value="{self.retrieve_nrnPrescription if self.retrieve_nrnPrescription else ''}"/>
                </nhis:contents>
            </nhis:message>"""

        P017 = P017.replace("False", "false").replace("True", "true")

        self.P017 = P017
        self.sign_P017()

    def getSignatureP017(self):
        return

    def sign_P017(self, field_name='P017', signedinfo='SignedInfo_P017', is_signed='P017_signed', signedinfo_signature='SignedInfo_P017_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_P017(self):
        return self.download_file('P017')

    def P017_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'P017_api_request')], limit=1)

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

        ET.indent(xml_root, space='    ')
        formatted_xml = ET.tostring(xml_root, encoding='unicode', method='xml')
        self.P018 = formatted_xml

        error_reason = xml_root.find('.//nhis:reason', ns)
        if error_reason is not None and 'value' in error_reason.attrib:
            error_message = error_reason.attrib['value']
            raise UserError(error_message)


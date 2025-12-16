# -*- coding: utf-8 -*-

import logging
import uuid
from xml.etree import ElementTree as ET

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class TrinityReferralCheck(models.Model):
    _name = 'trinity.referral.check'
    _description = 'Trinity Referral Check'
    _inherit = ["trinity.library.nhif.qes"]

    nrnReferral = fields.Char(string='НРН')

    response_authoredOn = fields.Char(string='Дата на НРН')
    response_nrnReferral = fields.Char(string='НРН')
    response_status = fields.Char(string='Статус')

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)

    R009 = fields.Text(string='R009', copy=False)
    R009_signed = fields.Char(string='R009 Signed Text', default='not signed', copy=False)
    SignedInfo_R009 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_R009_signature = fields.Char(string="SignedInfo signature", copy=False)

    R010 = fields.Text(string='R010', copy=False)

	# R009
    @api.onchange('nrnReferral')
    def compute_R009(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            R009 = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-R009.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.doctor_id.doctor_id if self.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="R009"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:nrnReferral value="{self.nrnReferral if self.nrnReferral else ''}"/>
                </nhis:contents>
            </nhis:message>"""

        # Replace "False" and "True" strings with "false" and "true"
        R009 = R009.replace("False", "false").replace("True", "true")

        self.R009 = R009
        self.sign_R009()

    def getSignatureR009(self):
        return

    def sign_R009(self, field_name='R009', signedinfo='SignedInfo_R009', is_signed='R009_signed', signedinfo_signature='SignedInfo_R009_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    # Download R009
    def action_download_R009(self):
        return self.download_file('R009')

    # POST signed R009.xml to NZIS API
    def R009_api_request(self):
        # Search for the record "R009_api_request" in trinity.communicator
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'R009_api_request')], limit=1)

        if communicator_record:
            # Use the values from the communicator record
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value

            self.make_api_post_request(field_origin, url, field_response)

    def check_response(self, response, field_response, request_msg_type=None):
        # Check if the response is XML
        try:
            xml_root = ET.fromstring(response.text)
        except ET.ParseError:
            # If not XML, check for the specific text
            if "401 Authorization Required" in response.text:
                raise UserError("НАПРАВЕТЕ ВРЪЗКА С НЗИС!")
            return  # Return if not XML and no error

        # If response is XML, extract the value using field_response
        ns = {'nhis': 'https://www.his.bg'}
        nrnReferral = xml_root.find('.//nhis:nrnReferral', ns)
        status = xml_root.find('.//nhis:status', ns)
        authoredOn = xml_root.find('.//nhis:authoredOn', ns)
        error_reason = xml_root.find('.//nhis:reason', ns)

        if nrnReferral is not None and 'value' in nrnReferral.attrib:
            self.response_nrnReferral = nrnReferral.attrib['value']

        if status is not None and 'value' in status.attrib:
            self.response_status = status.attrib['value']

        if authoredOn is not None and 'value' in authoredOn.attrib:
            self.response_authoredOn = authoredOn.attrib['value']

        if error_reason is not None and 'value' in error_reason.attrib:
            error_message = error_reason.attrib['value']
            raise UserError(error_message)

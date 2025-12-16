# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import base64
import datetime
import hashlib
import logging
import re

_logger = logging.getLogger(__name__)

class TrinityExaminationPenSignature(models.Model):
    _inherit = 'trinity.examination'

    signPen_X_message = fields.Text(string='signPen base', copy=False)
    signPen_X_message_hash_sha256 = fields.Text(string='signPen X message hash sha256', copy=False)
    SignData = fields.Text(string='SignData', copy=False)
    RsaSignature = fields.Text(string='RsaSignature', copy=False)
    signatureCert = fields.Text(string='signatureCert', copy=False)
    Signature_b64 = fields.Text(string='signature b64', copy=False)
    signature_file = fields.Binary(copy=False, string='Подпис на пациент/родител:')

    PadType = fields.Char(string='Pad Type', copy=False)
    SerialNumber = fields.Char(string='Serial Number', copy=False)
    FirmwareVersion = fields.Char(string='Firmware Version', copy=False)
    RSASupport = fields.Char(string='RSA Support', copy=False)
    biometryCertID = fields.Char(string='Biometry Cert ID', copy=False)
    RSAScheme = fields.Char(string='RSAScheme', copy=False)
    pad_manufacturer = fields.Many2one('trinity.nomenclature.cl120', string='Manufacturer', store=True, copy=False)
    pad_model = fields.Many2one('trinity.nomenclature.cl121', string='Model', store=True, copy=False)

    status = fields.Char(string='status', default='Not connected', copy=False)
    isPatientSigner = fields.Boolean(string='Подписът е положен от пациента', compute='compute_is_patient_signer_default', store=True, copy=False)
    parent_identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    parent_identifier_id = fields.Char(string='ЕГН/ЛНЧ/Друг №')
    parent_first_name = fields.Char(string='Собствено име')
    parent_last_name = fields.Char(string='Фамилно име')

    def signPenXmessage(self):
        source = self.X013 if not self.e_examination_nrn and isinstance(self.X013, str) else \
                self.X009 if self.e_examination_nrn and isinstance(self.X009, str) else None

        if not source:
            return

        start_tag = '<nhis:contents>'
        end_tag = '</nhis:contents>'
        start_idx = source.find(start_tag)
        end_idx = source.find(end_tag)

        if start_idx == -1 or end_idx == -1:
            return

        start_idx += len(start_tag)
        extracted = source[start_idx:end_idx].strip()

        if not extracted:
            return

        extracted = re.sub(r'\s*/>', r'/>', extracted)
        extracted = re.sub(r'/>', r' />', extracted)
        extracted = re.sub(r'>\s+<', '><', extracted)

        extracted = extracted.replace('<nhis:examination>', '<nhis:examination xmlns:nhis="https://www.his.bg">', 1)
        extracted = extracted.replace('<nhis:subject>', '<nhis:subject xmlns:nhis="https://www.his.bg">', 1)
        extracted = extracted.replace('<nhis:performer>', '<nhis:performer xmlns:nhis="https://www.his.bg">', 1)

        self.signPen_X_message = extracted

        hash_binary = hashlib.sha256(extracted.encode('utf-8')).digest()
        self.signPen_X_message_hash_sha256 = base64.b64encode(hash_binary).decode('utf-8')

    def clear_signPen_X_message_fields(self):
        self.write({
            'SignData': '',
            'RsaSignature': '',
            'signatureCert': '',
            'PadType': '',
            'SerialNumber': '',
            'FirmwareVersion': '',
            'RSASupport': '',
            'biometryCertID': '',
            'RSAScheme': '',
            'signPen_X_message': '',
            'signPen_X_message_hash_sha256': '',
            'Signature_b64': '',
            'signature_file': False,
        })
        return True

    @api.depends('patient_birth_date', 'examination_open_dtm')
    def compute_is_patient_signer_default(self):
        for record in self:
            if record.patient_birth_date and record.examination_open_dtm:
                birth_date = fields.Date.from_string(record.patient_birth_date)
                birth_datetime = datetime.datetime.combine(birth_date, datetime.time.min)

                open_datetime = fields.Datetime.from_string(record.examination_open_dtm)
                open_date = open_datetime.date()

                age_years = open_date.year - birth_date.year
                if open_date.month < birth_date.month or (open_date.month == birth_date.month and open_date.day < birth_date.day):
                    age_years -= 1

                record.isPatientSigner = age_years >= 18
            else:
                record.isPatientSigner = True
                record.parent_identifier_type = False
                record.parent_identifier_id = ''
                record.parent_first_name = ''
                record.parent_last_name = ''

    @api.onchange('Signature_b64')
    def signature_file_from_signature_b64(self):
        if len(self) == 1:
            for record in self:
                if record.Signature_b64:
                    record.signature_file = record.Signature_b64
                    record.Signature_b64 = False


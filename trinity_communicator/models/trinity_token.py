from odoo import models, fields, api
import xml.etree.ElementTree as ET
from datetime import datetime
from odoo.exceptions import UserError

class TrinityToken(models.Model):
    _name = 'trinity.token'
    _description = 'Get Token'
    _order = 'issuedOn desc'

    token = fields.Char(string="Token")

    accessToken = fields.Char(string='Access Token')
    tokenType = fields.Char(string='Token Type')
    expiresIn = fields.Char(string='Expires In')
    issuedOn = fields.Char(string='Issued On')
    expiresOn = fields.Char(string='Expires On')
    refreshToken = fields.Char(string='Refresh Token')
    user_id = fields.Many2one('res.users', string='User ID', default=lambda self: self.env.uid)

    issuedOnDatetime = fields.Datetime(string='Issued On (Datetime)')
    expiresOnDatetime = fields.Datetime(string='Expires On (Datetime)')

    def extract_token_values(self):
        if self.token:
            root = ET.fromstring(self.token)
            ns = {'nhis': 'https://www.his.bg'}
            contents = root.find('.//nhis:contents', ns)

            accessTokenElement = contents.find('.//nhis:accessToken', ns)
            self.accessToken = accessTokenElement.attrib.get('value') if accessTokenElement is not None else None

            tokenTypeElement = contents.find('.//nhis:tokenType', ns)
            self.tokenType = tokenTypeElement.attrib.get('value') if tokenTypeElement is not None else None

            expiresInElement = contents.find('.//nhis:expiresIn', ns)
            self.expiresIn = expiresInElement.attrib.get('value') if expiresInElement is not None else None

            issuedOnElement = contents.find('.//nhis:issuedOn', ns)
            self.issuedOn = issuedOnElement.attrib.get('value') if issuedOnElement is not None else None

            expiresOnElement = contents.find('.//nhis:expiresOn', ns)
            self.expiresOn = expiresOnElement.attrib.get('value') if expiresOnElement is not None else None

            refreshTokenElement = contents.find('.//nhis:refreshToken', ns)
            self.refreshToken = refreshTokenElement.attrib.get('value') if refreshTokenElement is not None else None

            if not all([self.accessToken, self.tokenType, self.expiresIn, self.issuedOn, self.expiresOn, self.refreshToken]):
                raise UserError('Поставете Вашия КЕП, рестартирайте браузъра и опитайте отново!')

            if self.issuedOn:
                issued_on = self.issuedOn[:-2]  # Remove last two
                self.issuedOnDatetime = datetime.strptime(issued_on, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                self.issuedOnDatetime = False

            if self.expiresOn:
                expires_on = self.expiresOn[:-2]
                self.expiresOnDatetime = datetime.strptime(expires_on, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                self.expiresOnDatetime = False

            self.update_doctor_token_values({})

    def update_doctor_token_values(self, vals):
        doctor = self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1)

        if doctor:
            doctor_vals = {}
            if self.accessToken:
                doctor_vals['accessToken'] = self.accessToken
            if self.expiresOnDatetime:
                doctor_vals['expiresOnDatetime'] = self.expiresOnDatetime

            if doctor_vals:
                doctor.sudo().write(doctor_vals)

        return True

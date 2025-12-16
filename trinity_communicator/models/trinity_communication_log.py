# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrinityCommunicationLog(models.Model):
    _name = 'trinity.communication.log'
    _description = 'Trinity Communication Log'
    _rec_name = 'response_date'
    _order = 'response_date desc'

    response_date = fields.Datetime(string='Response Date', default=fields.Datetime.now)
    response_text = fields.Text(string='Response')
    request_text = fields.Text(string='Request')
    lrn_origin = fields.Char(string='LRN Origin')

    def create(self, vals):
        record = super(TrinityCommunicationLog, self).create(vals)
        record.create_trinity_token_record()
        return record

    def create_trinity_token_record(self):
        if self.response_text and 'accessToken' in self.response_text:
            token_record = self.env['trinity.token'].create({
                'token': self.response_text
            })
            token_record.extract_token_values()
            return True
        return False

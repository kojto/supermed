# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrinityPatient(models.Model):
    _inherit = 'trinity.patient'

    examination_ids = fields.One2many('trinity.examination', 'patient_identifier_id', string='Прегледи', compute='_compute_examination_ids', store=False)

    @api.depends('identifier')
    def _compute_examination_ids(self):
        for patient in self:
            if patient.id:
                patient.examination_ids = self.env['trinity.examination'].search([('patient_identifier_id', '=', patient.id)])
            else:
                patient.examination_ids = False


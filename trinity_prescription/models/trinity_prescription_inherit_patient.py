# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrinityPatient(models.Model):
    _inherit = 'trinity.patient'

    prescription_ids = fields.One2many('trinity.prescription', 'subject_identifier', string='Рецепти', compute='_compute_prescription_ids', store=False)

    @api.depends('identifier')
    def _compute_prescription_ids(self):
        for patient in self:
            if patient.id:
                patient.prescription_ids = self.env['trinity.prescription'].search([('subject_identifier', '=', patient.id)])
            else:
                patient.prescription_ids = False


# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrinityPatient(models.Model):
    _inherit = 'trinity.patient'

    referral_issue_ids = fields.One2many('trinity.referral.issue', 'subject_identifier', string='Издадени направления', compute='_compute_referral_issue_ids', store=False)

    @api.depends('identifier')
    def _compute_referral_issue_ids(self):
        for patient in self:
            if patient.id:
                patient.referral_issue_ids = self.env['trinity.referral.issue'].search([('subject_identifier', '=', patient.id)])
            else:
                patient.referral_issue_ids = False

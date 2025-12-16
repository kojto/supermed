# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class TrinityExaminationTemplate(models.Model):
    _name = 'trinity.examination.template'
    _description = 'Trinity Report Template'
    _rec_name = 'template_id'

    template_id = fields.Char(string='Име на шаблона', required=True)

    icd_codes = fields.Many2many(comodel_name='trinity.nomenclature.cl011', string='МКБ кодове')

    diagnosis = fields.Text(string='Диагноза')
    medical_history = fields.Text(string='Анамнеза')
    objective_condition = fields.Text(string='Обективно')
    assessment_notes = fields.Text(string='Изследвания')
    therapy_note = fields.Text(string='Лечение')
    conclusion = fields.Text(string='Заключение')

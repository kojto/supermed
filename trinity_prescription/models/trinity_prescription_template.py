from odoo import api, models, fields, exceptions, _

class TrinityPrescriptionTemplate(models.Model):
    _name = 'trinity.prescription.template'
    _description = 'Trinity Prescription Template'
    _rec_name = 'prescription_template_name'
    _inherit = ["trinity.library.user.company.fields"]

    prescription_template_name = fields.Char(string='Име на шаблона')

    prescription_category = fields.Many2one('trinity.nomenclature.cl007', string='Категория', default=lambda self: self.env['trinity.nomenclature.cl007'].search([('key', '=', 'T1')], limit=1))
    prescription_financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Източник на финансиране', default=lambda self: self.env['trinity.nomenclature.cl069'].search([('key', '=', '4')], limit=1))
    prescription_dispensationType = fields.Many2one('trinity.nomenclature.cl008', string='Тип на отпускане', default=lambda self: self.env['trinity.nomenclature.cl008'].search([('key', '=', '1')], limit=1))
    prescription_allowedRepeatsNumber = fields.Integer(string='Разрешени повторения', default='0')
    prescription_supplements = fields.Char(string='Хранителни добавки', default='няма изписани')

    group_groupIdentifier = fields.Many2one('trinity.nomenclature.cl019', string='Идентификатор на Група', default=lambda self: self.env['trinity.nomenclature.cl019'].search([('key', '=', 'A')], limit=1))

    # MEDICATION
    medication_sequenceId = fields.Integer(string='Пореден Номер на Медикамент', default='1')
    medication_medicationCode_name = fields.Many2one('trinity.nomenclature.cl009', string='Код на Медикамент')
    medication_medicationCode = fields.Char(related='medication_medicationCode_name.key', string='Код на Медикамент')
    medication_medicationCode_DisplayValue = fields.Char(related='medication_medicationCode_name.description', string='Код на Медикамент')

    medication_form_name = fields.Many2one('trinity.nomenclature.cl010', string='Лекарствена форма')
    medication_form = fields.Char(related='medication_form_name.key', string='Лекарствена форма')
    medication_priority = fields.Many2one('trinity.nomenclature.cl027', string='Приоритет', default=lambda self: self.env['trinity.nomenclature.cl027'].search([('key', '=', '1')], limit=1))
    medication_note = fields.Text(string='Указания за изпълнение', default='Няма допълнителни указания')
    medication_icd_code = fields.Many2one('trinity.nomenclature.cl011', string='МКБ Код')
    medication_nhifCode_name = fields.Many2one('trinity.nomenclature.cl026', string='НЗОК име')
    medication_nhifCode = fields.Char(related='medication_nhifCode_name.key', string='НЗОК код')
    medication_nhifCode_description = fields.Char(related='medication_nhifCode_name.description', string='НЗОК наименование')
    medication_quantityValue = fields.Float(string='Колич. по лекарств. форма', default=1, digits=(6, 0))
    medication_isQuantityByForm = fields.Boolean(string='Колич. e по лекарств. форма?', default=False)
    medication_isSubstitutionAllowed = fields.Boolean(string='Позволена ли е самяна?', default=True)

    dosageInstruction_asNeeded = fields.Boolean(string='При нужда', default=False)
    dosageInstruction_route_name = fields.Many2one('trinity.nomenclature.cl013', string='Начин на приемане')
    dosageInstruction_route = fields.Char(related='dosageInstruction_route_name.key', string='Начин на приемане (код)')

    dosageInstruction_doseQuantityValue = fields.Float(string='Кол. за еднократен прием', default=1, digits=(6, 0))
    dosageInstruction_doseQuantityCode_UCUM = fields.Char(string='Форма според UCUM')
    dosageInstruction_doseQuantityCode_name = fields.Many2one('trinity.nomenclature.cl035', string='Форма на дозировката')
    dosageInstruction_doseQuantityCode = fields.Char(related='dosageInstruction_doseQuantityCode_name.key', string='Форма на дозировката (код)')
    dosageInstruction_doseQuantityCode_description = fields.Char(related='dosageInstruction_doseQuantityCode_name.description', string='Форма на дозировката')

    dosageInstruction_frequency = fields.Char(string='Честота на приема', default='1')
    dosageInstruction_period = fields.Float(string='Период определящ честота на приема (брой)', default=1, digits=(6, 0))
    dosageInstruction_periodUnit_name = fields.Many2one('trinity.nomenclature.cl020', string='Период определящ честота на приема', default='4')
    dosageInstruction_periodUnit = fields.Char(related='dosageInstruction_periodUnit_name.key', string='Период определящ честота на приема', default='4')
    dosageInstruction_periodUnit_description = fields.Char(related='dosageInstruction_periodUnit_name.description', string='Период определящ честота на приема (описание)', default='4')

    dosageInstruction_boundsDuration = fields.Float(string='Продължителност на приема (брой)', default=1, digits=(6, 0))
    dosageInstruction_boundsDurationUnit_name = fields.Many2one('trinity.nomenclature.cl020', string='Продължителност на приема', default='4')
    dosageInstruction_boundsDurationUnit = fields.Char(related='dosageInstruction_boundsDurationUnit_name.key', string='Продължителност на приема (код)', default='4')
    dosageInstruction_boundsDurationUnit_description_extended = fields.Char(related='dosageInstruction_boundsDurationUnit_name.description', string='Продължителност на приема (описание)', default='4')

    dosageInstructions_id = fields.One2many('trinity.prescription.dosage.instruction', 'prescription_template_id', string='Dosage Instructions')

    dosageInstruction_text = fields.Text(string='Текст', default='Допълнителни указания за приема на лекарството:\n')

    @api.onchange('medication_medicationCode_name')
    def _onchange_medication_medicationCode_name(self):
        if self.medication_medicationCode_name:
            self.medication_form_name = self.env['trinity.nomenclature.cl010'].search([('key', '=', self.medication_medicationCode_name.meta_form_id)], limit=1)
            self.prescription_category = self.medication_medicationCode_name.meta_required_prescription_category if self.medication_medicationCode_name.meta_required_prescription_category else self.env['trinity.nomenclature.cl007'].search([('key', '=', 'T1')], limit=1)

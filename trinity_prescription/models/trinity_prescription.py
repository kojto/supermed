from odoo import api, models, fields
from odoo.exceptions import UserError
from xml.etree import ElementTree as ET
import datetime
import uuid
import logging

_logger = logging.getLogger(__name__)

class TrinityPrescription(models.Model):
    _name = 'trinity.prescription'
    _description = 'Trinity Prescription'
    _rec_name = 'prescription_lrn'
    _inherit = ["trinity.library.nhif.qes"]

    prescription_basedOn_lrn = fields.Many2one('trinity.examination', string='Основано на амб. №', required=True)
    prescription_basedOn_nrn = fields.Char(related='prescription_basedOn_lrn.e_examination_nrn', string='Основано на НРН', readonly=True)

    prescription_lrn = fields.Char(string='Рецепта №', required=True, default=lambda self: self.generate_prescription_lrn(), copy=False)

    response_nrnPrescription = fields.Char(string='НРН на рецепта', copy=False)
    response_lrnPrescription = fields.Char(string='ЛРН на рецепта', copy=False)
    response_status = fields.Many2one('trinity.nomenclature.cl002', string='Статус на рецептата')
    response_status_key = fields.Char(related='response_status.key', string='Статус на рецептата (ключ)')

    prescription_authoredOn = fields.Date(string='Дата на съставяне', default=lambda self: datetime.datetime.now().strftime('%Y-%m-%d'))
    prescription_category = fields.Many2one('trinity.nomenclature.cl007', string='Категория', default=lambda self: self.env['trinity.nomenclature.cl007'].search([('key', '=', 'T1')], limit=1))
    prescription_isProtocolBased = fields.Boolean(string='Използва ли протокол', default=False)
    prescription_protocolNumber = fields.Char(string='Номер на протокол')
    prescription_protocolDate = fields.Date(string='Дата на протокола')
    prescription_rhifNumber = fields.Many2one('trinity.nomenclature.cl015', string='РЗОК Номер', default=lambda self: self.prescription_basedOn_lrn.patient_rhifareanumber_key if self.prescription_basedOn_lrn else self.env['trinity.nomenclature.cl015'].search([('key', '=', '22')], limit=1))
    prescription_financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Източник на финансиране')
    prescription_dispensationType = fields.Many2one('trinity.nomenclature.cl008', string='Тип на отпускане', default=lambda self: self.env['trinity.nomenclature.cl008'].search([('key', '=', '1')], limit=1))
    prescription_allowedRepeatsNumber = fields.Integer(string='Разрешени повторения', default='0')
    prescription_supplements = fields.Char(string='Хранителни добавки', default='няма изписани')
    prescription_nrnPreValidation = fields.Char(string='Пре-валидационен НРН')

    group_groupIdentifier = fields.Many2one('trinity.nomenclature.cl019', string='Идентификатор на Група', default=lambda self: self.env['trinity.nomenclature.cl019'].search([('key', '=', 'A')], limit=1))

    medication_sequenceId = fields.Integer(string='Пореден Номер на Медикамент', default='1')
    medication_medicationCode_name = fields.Many2one('trinity.nomenclature.cl009', string='Код на Медикамент')
    medication_medicationCode = fields.Char(related='medication_medicationCode_name.key', string='Код на Медикамент')
    medication_medicationCode_DisplayValue = fields.Char(related='medication_medicationCode_name.description', string='Код на Медикамент')

    medication_form_name = fields.Many2one('trinity.nomenclature.cl010', string='Лекарствена форма')

    medication_form = fields.Char(related='medication_form_name.key', string='Лекарствена форма')
    medication_priority = fields.Many2one('trinity.nomenclature.cl027', string='Приоритет', default=lambda self: self.env['trinity.nomenclature.cl027'].search([('key', '=', '1')], limit=1))
    medication_note = fields.Text(string='Указания за изпълнение', default='Няма допълнителни указания')
    medication_icd_code = fields.Many2one('trinity.nomenclature.cl011', string='МКБ Код')
    medication_nhifCode_name = fields.Many2one('trinity.nomenclature.cl026', string='Име по НЗОК')
    medication_nhifCode = fields.Char(related='medication_nhifCode_name.key', string='Код по НЗОК')
    medication_nhifCode_description = fields.Char(related='medication_nhifCode_name.description', string='НЗОК наименование')
    medication_quantityValue = fields.Float(string='Колич. по лекарств. форма', default=1, digits=(6, 0))
    medication_isQuantityByForm = fields.Boolean(string='Колич. e по лекарств. форма?', default=False)
    medication_isSubstitutionAllowed = fields.Boolean(string='Позволена ли е самяна?', default=True)
    medication_intakeDuration = fields.Integer(string='Обща продължителност на приема (дни)')

    effectiveDosePeriod_start = fields.Date(string='Начална Дата', default=fields.Date.today)
    effectiveDosePeriod_end = fields.Date(string='Крайна Дата', default=lambda self: fields.Date.today() + datetime.timedelta(days=7))

    dosageInstruction_sequence = fields.Char(string='Пореден №', default='1')
    dosageInstruction_asNeeded = fields.Boolean(string='При нужда', default=False)
    dosageInstruction_route_name = fields.Many2one('trinity.nomenclature.cl013', string='Начин на приемане')
    dosageInstruction_route = fields.Char(related='dosageInstruction_route_name.key', string='Начин на приемане (код)')

    dosageInstruction_doseQuantityValue = fields.Float(string='Кол. за еднократен прием', default=1, digits=(6, 0))
    dosageInstruction_doseQuantityCode_UCUM = fields.Char(string='Форма според UCUM')
    dosageInstruction_doseQuantityCode_name = fields.Many2one('trinity.nomenclature.cl035', string='Форма на дозировката')
    dosageInstruction_doseQuantityCode = fields.Char(related='dosageInstruction_doseQuantityCode_name.key', string='Форма на дозировката (код)')
    dosageInstruction_doseQuantityCode_description = fields.Char(related='dosageInstruction_doseQuantityCode_name.description', string='Форма на дозировката')

    dosageInstruction_frequency = fields.Char(string='Честота на приема', default='1')
    dosageInstruction_period = fields.Float(string='Честота на приема (брой)', default=1, digits=(6, 0))
    dosageInstruction_periodUnit_name = fields.Many2one('trinity.nomenclature.cl020', string='Период определящ честота на приема', default='Ден')
    dosageInstruction_periodUnit = fields.Char(related='dosageInstruction_periodUnit_name.key', string='Период определящ честота на приема', default='4')
    dosageInstruction_periodUnit_description = fields.Char(related='dosageInstruction_periodUnit_name.description', string='Период определящ честота на приема (описание)', default='4')
    dosageInstruction_periodUnit_plural = fields.Char(related='dosageInstruction_periodUnit_name.meta_plural_descriptionbg', string='Период определящ честота на приема (мн.ч.)')

    dosageInstruction_boundsDuration = fields.Float(string='Продължителност на приема (брой)', default=1, digits=(6, 0))
    dosageInstruction_boundsDurationUnit_name = fields.Many2one('trinity.nomenclature.cl020', string='Период на продължителност на приема', default='Ден')
    dosageInstruction_boundsDurationUnit = fields.Char(related='dosageInstruction_boundsDurationUnit_name.key', string='Продължителност на приема (код)', default='4')
    dosageInstruction_boundsDurationUnit_description_extended = fields.Char(related='dosageInstruction_boundsDurationUnit_name.description', string='Продължителност на приема (описание)', default='4')
    dosageInstruction_boundsDurationUnit_plural = fields.Char(related='dosageInstruction_boundsDurationUnit_name.meta_plural_descriptionbg', string='Продължителност на приема (мн.ч.)')

    prescription_template_name = fields.Many2one('trinity.prescription.template', string='Шаблон')
    see_details = fields.Boolean(string='Виж детайлите', default=False)

    dosageInstruction_text = fields.Text(string='Текст', default='Допълнителни указания за приема на лекарството:\n')
    dosageInstruction_interpretation = fields.Text(compute='compute_interpretation', string='Интерпретация')

    dosageInstructions_id = fields.One2many('trinity.prescription.dosage.instruction', 'prescription_id', string='Dosage Instructions')

    subject_identifier = fields.Many2one(related='prescription_basedOn_lrn.patient_identifier_id', string='Идентификатор')
    subject_identifierType = fields.Many2one(related='prescription_basedOn_lrn.patient_identifier_type', string='Тип на Идентификатора')
    subject_prBookNumber = fields.Char(string='Номер на Рецептурната Книжка')
    subject_nhifInsuranceNumber = fields.Char(string='Личен осигурителен №')
    subject_birthDate = fields.Date(string='Дата на Раждане', related='prescription_basedOn_lrn.patient_birth_date')
    subject_gender = fields.Many2one(related='prescription_basedOn_lrn.patient_gender')
    subject_age = fields.Float(related='prescription_basedOn_lrn.patient_age', string='Възраст')
    subject_weight = fields.Char(string='Тегло')
    subject_given = fields.Char(string='Име', related='prescription_basedOn_lrn.patient_first_name')
    subject_middle = fields.Char(string='Второ/Презиме/Бащино Име', related='prescription_basedOn_lrn.patient_middle_name')
    subject_family = fields.Char(string='Фамилия', related='prescription_basedOn_lrn.patient_last_name')
    subject_full = fields.Char(string='Пациент', related='prescription_basedOn_lrn.patient_full_name')
    subject_isPregnant = fields.Boolean(default=False, string='Бременна')
    subject_isBreastFeeding = fields.Boolean(default=False, string='Кърмачка')

    subject_country = fields.Many2one('trinity.nomenclature.cl005', related='prescription_basedOn_lrn.patient_country', string='Държава')
    subject_county = fields.Many2one('trinity.nomenclature.cl041', related='prescription_basedOn_lrn.patient_county', string='Област')
    subject_city = fields.Char(string='Град', related='prescription_basedOn_lrn.patient_city')
    subject_line = fields.Char(string='Пълен адрес')
    subject_postalCode = fields.Char(related='prescription_basedOn_lrn.patient_zip_code', string='Пощенски Код')
    subject_phone = fields.Char(string='Телефонен Номер')
    subject_email = fields.Char(string='Имейл')

    requester_pmi = fields.Many2one(related='prescription_basedOn_lrn.main_dr_performing_doctor_id')
    requester_pmi_full_name = fields.Char(related='prescription_basedOn_lrn.main_dr_performing_full_name')
    requester_pmiDeputy = fields.Many2one(related='prescription_basedOn_lrn.deputizing_dr_performing_doctor_id')
    requester_qualification = fields.Many2one(related='prescription_basedOn_lrn.main_dr_performing_qualification_code')
    requester_qualification_nhif = fields.Char(related='prescription_basedOn_lrn.main_dr_performing_qualification_code_nhif')
    requester_role = fields.Many2one(related='prescription_basedOn_lrn.performer_role')
    requester_practiceNumber = fields.Char(related='prescription_basedOn_lrn.main_dr_performing_practiceNumber')
    requester_rhifAreaNumber = fields.Many2one(related='prescription_basedOn_lrn.main_dr_performing_rhifareanumber_key')

    requester_nhifNumber = fields.Char(related='prescription_basedOn_lrn.main_dr_performing_nhif_Number')
    requester_phone = fields.Char(related='prescription_basedOn_lrn.main_dr_performing_phone')
    requester_email = fields.Char(related='prescription_basedOn_lrn.main_dr_performing_email')

    @api.depends('dosageInstruction_sequence', 'dosageInstruction_doseQuantityValue', 'dosageInstruction_doseQuantityCode', 'dosageInstruction_frequency', 'dosageInstruction_period', 'dosageInstruction_periodUnit', 'dosageInstruction_periodUnit_plural', 'dosageInstruction_text', 'dosageInstruction_boundsDuration', 'dosageInstruction_boundsDurationUnit', 'dosageInstruction_boundsDurationUnit_plural')
    def compute_interpretation(self):
        for record in self:
            doseQuantityValue = int(record.dosageInstruction_doseQuantityValue) if record.dosageInstruction_doseQuantityValue else 0
            frequency = int(record.dosageInstruction_frequency) if record.dosageInstruction_frequency else 0
            period = int(record.dosageInstruction_period) if record.dosageInstruction_period else 1
            boundsDuration = int(record.dosageInstruction_boundsDuration) if record.dosageInstruction_boundsDuration else 0
            interpretation = ""
            if doseQuantityValue and record.dosageInstruction_doseQuantityCode_description:
                dose_unit = record.dosageInstruction_doseQuantityCode_description.lower()
                if doseQuantityValue == 1:
                    interpretation += f"{doseQuantityValue} {dose_unit} "
                else:
                    if dose_unit.endswith('а'):
                        interpretation += f"{doseQuantityValue} {dose_unit[:-1]}и "
                    else:
                        interpretation += f"{doseQuantityValue} {dose_unit} "
            if frequency == 1:
                interpretation += "веднъж "
            elif frequency > 1:
                interpretation += f"{frequency} пъти "
            if record.dosageInstruction_periodUnit_description:
                periodUnit = record.dosageInstruction_periodUnit_description.lower()
                if period == 1:
                    unit_map = {
                        'ден': 'на ден',
                        'час': 'на час',
                        'седмица': 'седмично',
                        'месец': 'месечно'
                    }
                    interpretation += unit_map.get(periodUnit, f"на {periodUnit}") + " "
                else:
                    periodUnit_plural = record.dosageInstruction_periodUnit_plural.lower() if record.dosageInstruction_periodUnit_plural else periodUnit
                    interpretation += f"на всеки {period} {periodUnit_plural} "
            if boundsDuration and record.dosageInstruction_boundsDurationUnit_description_extended:
                boundsUnit = record.dosageInstruction_boundsDurationUnit_description_extended.lower()
                if boundsDuration > 1 and record.dosageInstruction_boundsDurationUnit_plural:
                    boundsUnit = record.dosageInstruction_boundsDurationUnit_plural.lower()
                interpretation += f"за {boundsDuration} {boundsUnit} "
            interpretation = interpretation.strip()
            record.dosageInstruction_interpretation = interpretation

    @api.model
    def generate_prescription_lrn(self):
        date_today = datetime.datetime.now().date().strftime('%Y-%m-%d')

        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.prescription'].sudo().search(
            [('prescription_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='prescription_lrn desc',
            limit=1
        )

        if existing_records:
            last_sequence = existing_records.prescription_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1

        lrn_value = f'Rx-{date_today}-{current_company_vat}-{sequence_number:04d}'

        return lrn_value


class TrinityPrescriptionDosageInstruction(models.Model):
    _name = 'trinity.prescription.dosage.instruction'
    _description = 'Trinity Prescription Dosage Instruction'
    _rec_name = 'id'

    prescription_id = fields.Many2one('trinity.prescription', string='Рецепта', copy=False)
    prescription_template_id = fields.Many2one('trinity.prescription.template', string='Шаблон', copy=False)

    dosageInstruction_when = fields.Many2one('trinity.nomenclature.cl034', string='Време за прием')
    dosageInstruction_when_name = fields.Char(related='dosageInstruction_when.name', string='Време за прием (код)')
    dosageInstruction_offset = fields.Float(string='Времево отместване в минути', digits=(6, 0))

    @api.onchange('dosageInstruction_when')
    def _onchange_when(self):
        if not self.dosageInstruction_when:
            self.dosageInstruction_offset = 0


class TrinityPrescriptionValidationWizard(models.TransientModel):
    _name = 'trinity.prescription.validation.wizard'
    _description = 'Prescription Validation Errors Wizard'

    prescription_id = fields.Many2one('trinity.prescription', string='Рецепта', readonly=True)
    error_messages = fields.Html(string='Validation Errors', readonly=True)
    error_count = fields.Integer(string='Брой грешки', readonly=True)
    is_success = fields.Boolean(string='Is Success', default=False)

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}

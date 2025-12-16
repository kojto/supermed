from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from lxml import etree
from odoo.http import request
from odoo import http
from xml.etree import ElementTree as ET
from PyPDF2 import PdfMerger
from datetime import timedelta
import base64
import datetime
import requests
import uuid
import re
import logging
import hashlib
import io

_logger = logging.getLogger(__name__)

class TrinityExamination(models.Model):
    _name = 'trinity.examination'
    _description = 'Trinity Examination'
    _rec_name = 'e_examination_lrn'
    _order = 'name desc'
    _inherit = ["trinity.library.printable", "trinity.library.nhif.qes"]

    e_examination_nrn = fields.Char(string='НРН', copy=False)
    e_examination_lrn = fields.Char(string='ЛРН', required=True, default=lambda self: self.generate_e_examination_lrn(), copy=False)

    name = fields.Char(string='Име', compute='_compute_name', store=True)

    nzis_error_message = fields.Char(string='НЗИС грешка', copy=False)

    examination_open_dtm = fields.Datetime('Дата на отваряне на прегледа', default=lambda self: self.compute_open_datetime(), copy=False)
    examination_close_dtm = fields.Datetime('Дата на затваряне на прегледа', default=lambda self: self.compute_open_datetime() + datetime.timedelta(minutes=21), copy=False)

    examination_open_dt = fields.Date(string='Дата на отваряне на прегледа', compute='_compute_examination_open_dt', store=True)

    @api.depends('examination_open_dtm')
    def _compute_examination_open_dt(self):
        for record in self:
            if record.examination_open_dtm:
                record.examination_open_dt = record.examination_open_dtm.date()
            else:
                record.examination_open_dt = False

    isLocked = fields.Boolean(string='Заключен', default=False, copy=False, help='Автоматично се заключва след 1 месец. Може да се отключи ръчно от администратор.')

    response_status = fields.Many2one('trinity.nomenclature.cl055', string='Статус на прегледа', default=lambda self: self.env['trinity.nomenclature.cl055'].search([('key', '=', '0')], limit=1), copy=False)
    response_status_key = fields.Char(related='response_status.key')
    response_status_name = fields.Char(related='response_status.name')

    basedOn_e_examination_lrn = fields.Char(string='Предходен Амб. №', copy=False)
    basedOn_e_examination_nrn = fields.Char(string='НРН на направление или предходен преглед', copy=False)
    basedOn_e_examination_nrn_date = fields.Date(string='Дата на създаване', copy=False)
    basedOn_e_examination_nrn_sentbyPractice = fields.Char(string='Практика изпращаща НРН', copy=False)
    basedOn_e_examination_nrn_sentbyDoctorId = fields.Char(string='ИД на лекар изпращащ НРН', copy=False)
    basedOn_e_examination_nrn_sentbyDoctor_qualification_code = fields.Char(string='Код на квалификация на лекар изпращащ НРН', copy=False)

    directedBy = fields.Many2one('trinity.nomenclature.cl060', string='Насочен от', default=lambda self: self.env['trinity.nomenclature.cl060'].search([('key', '=', '8')], limit=1))

    previous_e_examination_lrn = fields.Char(string='Амб. № на предходен преглед', copy=False)
    previous_e_examination_nrn = fields.Char(string='НРН на предходен преглед', copy=False)
    previous_examination_open_dtm = fields.Datetime(string='Дата на предходен преглед', copy=False)

    previous_examination_open_dtm_30d = fields.Boolean(string='Предходен преглед в рамките на 30 дни', copy=False, compute='compute_previous_examination_delta')
    previous_examination_delta = fields.Integer(string='Дни от последен преглед', copy=False, compute='compute_previous_examination_delta')

    patient_identifier_id = fields.Many2one(comodel_name='trinity.patient', required=True, string='ЕГН/ЛНЧ/Друг №')
    patient_identifier_type = fields.Many2one(related='patient_identifier_id.identifier_type')
    patient_first_name = fields.Char(related='patient_identifier_id.first_name', string='Собствено име')
    patient_middle_name = fields.Char(related='patient_identifier_id.middle_name', string='Бащино име')
    patient_last_name = fields.Char(related='patient_identifier_id.last_name', string='Фамилно име')
    patient_nationality = fields.Many2one(related='patient_identifier_id.nationality')
    patient_nationality_code = fields.Char(related='patient_identifier_id.nationality_code')
    patient_full_name = fields.Char(related='patient_identifier_id.patient_full_name')
    patient_signature = fields.Binary(string='Подпис на пациента')

    patient_examination_type_ids = fields.Many2many(related='patient_identifier_id.examination_type_ids')

    patient_maritalStatus = fields.Many2one(related='patient_identifier_id.maritalStatus')
    patient_education = fields.Many2one(related='patient_identifier_id.education')
    patient_workplace = fields.Char(related='patient_identifier_id.workplace')
    patient_profession = fields.Char(related='patient_identifier_id.profession')

    patient_zip_code = fields.Char(related='patient_identifier_id.zip_code')
    patient_city = fields.Char(related='patient_identifier_id.city')
    patient_county = fields.Many2one(related='patient_identifier_id.county_bulgarian')
    patient_county_key = fields.Char(related='patient_county.key')
    patient_country = fields.Many2one(related='patient_identifier_id.country_bulgarian')
    patient_country_key = fields.Char(related='patient_country.key')
    patient_ekatte_key = fields.Many2one(related='patient_identifier_id.ekatte_key')
    patient_rhifareanumber_key = fields.Many2one(related='patient_identifier_id.rhifareanumber_key')
    patient_RZOK = fields.Char(related='patient_rhifareanumber_key.key', string='РЗОК')
    patient_nhifInsuranceNumber = fields.Char(related='patient_identifier_id.nhifInsuranceNumber', string='Личен осигурителен №')

    patient_ZdrRajon = fields.Char(related='patient_rhifareanumber_key.key', string='Здравен район')
    patient_address_line = fields.Char(related='patient_identifier_id.address_line')

    patient_birth_date = fields.Date(related='patient_identifier_id.birth_date')
    patient_gender = fields.Many2one(related='patient_identifier_id.gender')

    patient_isPregnant = fields.Boolean(string='Е бременна', default=False)
    patient_isBreastFeeding = fields.Boolean(string='Кърми', default=False)

    patient_gestationalWeek = fields.Selection([('1', '1-ва седмица'), ('2', '2-ра седмица'), ('3', '3-та седмица'), ('4', '4-та седмица'), ('5', '5-та седмица'), ('6', '6-та седмица'), ('7', '7-ма седмица'), ('8', '8-ма седмица'), ('9', '9-та седмица'), ('10', '10-та седмица'), ('11', '11-та седмица'), ('12', '12-та седмица'), ('13', '13-та седмица'), ('14', '14-та седмица'), ('15', '15-та седмица'), ('16', '16-та седмица'), ('17', '17-та седмица'), ('18', '18-та седмица'), ('19', '19-та седмица'), ('20', '20-та седмица'), ('21', '21-ва седмица'), ('22', '22-ра седмица'), ('23', '23-та седмица'), ('24', '24-та седмица'), ('25', '25-та седмица'), ('26', '26-та седмица'), ('27', '27-ма седмица'), ('28', '28-ма седмица'), ('29', '29-та седмица'), ('30', '30-та седмица'), ('31', '31-ва седмица'), ('32', '32-ра седмица'), ('33', '33-та седмица'), ('34', '34-та седмица'), ('35', '35-та седмица'), ('36', '36-та седмица'), ('37', '37-ма седмица'), ('38', '38-ма седмица'), ('39', '39-та седмица'), ('40', '40-та седмица')], string='Гестационна седмица', widget='selection_input', copy=False)

    patient_age = fields.Float(string='Възраст', compute='compute_patient_age')
    patient_weight = fields.Char(string='Тегло')

    see_patient_details = fields.Boolean(string='Виж детайлите', default=False)

    def open_patient_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Отвори карта на пациента',
            'res_model': 'trinity.patient',
            'res_id': self.patient_identifier_id.id,
            'view_mode': 'form',
            'target': 'new',
        }

    icd_codes = fields.Many2many(comodel_name='trinity.nomenclature.cl011', string='МКБ кодове')
    icd_code = fields.Many2one(comodel_name='trinity.nomenclature.cl011', compute='compute_icd_code', string='МКБ код')

    @api.depends('icd_codes')
    def compute_icd_code(self):
        for record in self:
            record.icd_code = record.icd_codes[0] if record.icd_codes else False

    template_id = fields.Many2one(comodel_name='trinity.examination.template', string='Шаблон')
    template_e_examination_lrn = fields.Many2one(comodel_name='trinity.examination', string='Шаблон от предходен преглед', ondelete='set null')

    diagnosis = fields.Text(string='Диагноза')
    diagnosis_rareDisease = fields.Many2one('trinity.nomenclature.cl150', string='Рядко заболяване (Orphanet)')
    diagnosis_diseasesReporting = fields.Many2one('trinity.nomenclature.cl149', string='Категоризация на заразни болести')
    diagnosis_registerForObservation = fields.Boolean(string='Регистрация за проследяване', default=False)

    medical_history = fields.Text(string='Анамнеза')
    medical_history_nrnAllergy = fields.Char(string='НРН на е-документ за алергия')
    medical_history_nrnHistory = fields.Char(string='НРН на е-документ за семейна здравна история')

    objective_condition = fields.Text(string='Обективно състояние')
    assessment_notes = fields.Text(string='Изследвания')

    therapy_note = fields.Text(string='Терапия')
    therapy_nrnPrescription = fields.Char(string='НРН на рецепта')
    therapy_medicationCode = fields.Many2many('trinity.nomenclature.cl009', 'examination_therapy_medication_rel', string='Изписани лекарства')

    examination_conclusion = fields.Many2one('trinity.nomenclature.cl100', string='Заключение след прегледа')
    examination_dischargeDisposition = fields.Many2one('trinity.nomenclature.cl080', string='Място на провеждане на лечението')
    conclusion = fields.Text(string='Заключение')

    conversation_with_patient = fields.Text(string='Разговор с пациента')

    physicalExamination_code = fields.Char(string='Код на физикалния преглед')
    physicalExamination_nomenclature = fields.Char(string='Номенклатура с възможните състояния')
    physicalExamination_condition = fields.Char(string='Наблюдавано състояние')
    physicalExamination_conclusion = fields.Char(string='Клинично заключение')

    performer_role = fields.Many2one('trinity.nomenclature.cl023', string='Роля на лекаря', default=lambda self: self.env['trinity.nomenclature.cl023'].search([('key', '=', '1')], limit=1))

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)
    main_dr_performing_title = fields.Selection(related='main_dr_performing_doctor_id.title')
    main_dr_performing_first_name = fields.Char(related='main_dr_performing_doctor_id.first_name')
    main_dr_performing_middle_name = fields.Char(related='main_dr_performing_doctor_id.middle_name')
    main_dr_performing_last_name = fields.Char(related='main_dr_performing_doctor_id.last_name')
    main_dr_performing_full_name = fields.Char(related='main_dr_performing_doctor_id.full_name')
    main_dr_performing_identifier_type = fields.Many2one(related='main_dr_performing_doctor_id.identifier_type')
    main_dr_performing_identifier = fields.Char(related='main_dr_performing_doctor_id.identifier')
    main_dr_performing_practiceNumber = fields.Char(related='main_dr_performing_doctor_id.hospital_no')
    main_dr_performing_nhif_Number = fields.Char(related='main_dr_performing_doctor_id.nhif_Number')
    main_dr_performing_email = fields.Char(related='main_dr_performing_doctor_id.email')
    main_dr_performing_phone = fields.Char(related='main_dr_performing_doctor_id.phone')
    main_dr_performing_practiceName = fields.Char(related='main_dr_performing_doctor_id.hospital_name')
    main_dr_performing_initials = fields.Char(related='main_dr_performing_doctor_id.initials')
    main_dr_performing_nhif_ContractNo = fields.Char(related='main_dr_performing_doctor_id.nhif_ContractNo')
    main_dr_performing_nhif_ContractDate = fields.Date(related='main_dr_performing_doctor_id.nhif_ContractDate')
    main_dr_performing_qualification_code = fields.Many2one(related='main_dr_performing_doctor_id.qualification_code')
    main_dr_performing_qualification_code_nhif = fields.Char(related='main_dr_performing_doctor_id.qualification_code_nhif')
    main_dr_performing_qualification_name = fields.Char(related='main_dr_performing_doctor_id.description_bg')
    main_dr_performing_county_bulgarian = fields.Many2one(related='main_dr_performing_doctor_id.county_bulgarian')
    main_dr_performing_country_bulgarian = fields.Many2one(related='main_dr_performing_doctor_id.country_bulgarian')
    main_dr_performing_ekatte_key = fields.Many2one(related='main_dr_performing_doctor_id.ekatte_key')
    main_dr_performing_rhifareanumber_key = fields.Many2one(related='main_dr_performing_doctor_id.rhifareanumber_key')

    main_dr_performing_qualification_code_nhif_and_name = fields.Char(string='Специалност', compute='compute_qualification_code_nhif_and_name')

    @api.depends('main_dr_performing_qualification_code', 'main_dr_performing_qualification_name')
    def compute_qualification_code_nhif_and_name(self):
        for record in self:
            code = record.main_dr_performing_qualification_code or ''
            name = record.main_dr_performing_qualification_name if record.main_dr_performing_qualification_name else ''
            record.main_dr_performing_qualification_code_nhif_and_name = f"{code} {name}"

    deputizing_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='УИН')
    deputizing_dr_performing_title = fields.Selection(related='deputizing_dr_performing_doctor_id.title', string='Титла')
    deputizing_dr_performing_first_name = fields.Char(related='deputizing_dr_performing_doctor_id.first_name', string='Име')
    deputizing_dr_performing_last_name = fields.Char(related='deputizing_dr_performing_doctor_id.last_name', string='Фамилия')
    deputizing_dr_performing_full_name = fields.Char(related='deputizing_dr_performing_doctor_id.full_name', string='Име')
    deputizing_dr_performing_qualification_code = fields.Many2one(related='deputizing_dr_performing_doctor_id.qualification_code', string='Код специалност')
    deputizing_dr_performing_qualification_code_nhif = fields.Char(related='deputizing_dr_performing_doctor_id.qualification_code_nhif')
    deputizing_dr_performing_qualification_name = fields.Char(related='deputizing_dr_performing_doctor_id.description_bg', string='Специалност')

    dr_directing_doctor_id = fields.Many2one('trinity.medical.facility.doctors.external', string='Изпращащ лекар')
    dr_directing_ext_doctor_full_name = fields.Char(related='dr_directing_doctor_id.name')
    dr_directing_qualification_name = fields.Text(related='dr_directing_doctor_id.description_bg_agent')
    dr_directing_qualification_code = fields.Many2one(related='dr_directing_doctor_id.qualification_code')
    dr_directing_hospital_no = fields.Char(string='Номер на болница', related='dr_directing_doctor_id.hospital_no')

    originating_document_no = fields.Char(string='Номер на оригиналния документ')
    date_originating_doc = fields.Date(string='Дата на оригиналния документ')

    diagnosis_use = fields.Many2one('trinity.nomenclature.cl076', string='Използване на диагнозата', default=lambda self: self.env['trinity.nomenclature.cl079'].search([('key', '=', '3')], limit=1).id)
    diagnosis_rank = fields.Many2one('trinity.nomenclature.cl080', string='Ранг на диагнозата', default=lambda self: self.env['trinity.nomenclature.cl080'].search([('key', '=', '1')], limit=1).id)
    clinicalStatus = fields.Many2one('trinity.nomenclature.cl077', string='Статус на диагнозата', default=lambda self: self.env['trinity.nomenclature.cl077'].search([('key', '=', '10')], limit=1).id)
    verificationStatus = fields.Many2one('trinity.nomenclature.cl078', string='Верификация на диагнозата', default=lambda self: self.env['trinity.nomenclature.cl078'].search([('key', '=', '20')], limit=1).id)
    onsetDateTime = fields.Datetime(string='Начало на болестта', default=lambda self: self.examination_open_dtm or fields.Datetime.now(), copy=False)

    examination_type_id = fields.Many2one('trinity.examination.type', string='Вид услуга', copy=False)
    examination_type_ids = fields.Many2many('trinity.examination.type', related='patient_identifier_id.examination_type_ids')
    secondary_examination = fields.Boolean(string='Е вторичен', related='examination_type_id.secondary_examination')
    financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Източник на финансиране', related='examination_type_id.financingSource')
    financingSource_key = fields.Char(related='financingSource.key', string='Код на източник на финансиране')
    examination_type = fields.Char(related='examination_type_id.examination_type', string='Вид услуга')

    examination_type_id_price = fields.Many2one('trinity.examination.type.prices', string='Цена', compute='_compute_examination_type_id_price', store=True)
    examination_type_id_price_onsite = fields.Float(related='examination_type_id_price.price_onsite', string='Цена на място')

    examination_purpose = fields.Many2one(related='examination_type_id.examination_purpose')
    examination_class = fields.Many2one(related='examination_type_id.examination_class')
    examination_screening = fields.Many2one('trinity.nomenclature.cl143', string='Скринингова програма', copy=False)
    examination_partOf = fields.Char(string='НРН на документ за здравословен проблем', copy=False)
    examination_plannedType = fields.Many2one('trinity.nomenclature.cl132', string='Вид профилактичен преглед', copy=False)
    examination_correctionReason = fields.Text(string='Причина за корекция', copy=False, default='Явна фактическа грешка в документацията')
    examination_correctionHistory = fields.Text(string='История на корекции', copy=False, readonly=True)
    examination_incidentalVisit = fields.Boolean(string='Инцидентно посещение', default=True, copy=False)
    examination_adverseConditions = fields.Boolean(string='Неблагоприятни условия', default=False, copy=False)
    nhif_procedure_code = fields.Char(string='НЗОК код на процедура', related='examination_type_id.nhif_procedure_code')
    cost_bearer_id = fields.Many2one('trinity.costbearer', related='examination_type_id.cost_bearer_id', string='Разходоносител')
    cost_bearer_id_full_name = fields.Char(related='cost_bearer_id.full_name')

    diagnosticReport = fields.Boolean(related='examination_type_id.diagnosticReport')
    diagnosticReport_code = fields.Many2one(related='examination_type_id.diagnosticReport_code', string='Процедура')
    diagnosticReport_status = fields.Many2one(related='examination_type_id.diagnosticReport_status', string='Статус на диагностичната процедура')
    diagnosticReport_numberPerformed = fields.Integer(related='examination_type_id.diagnosticReport_numberPerformed')

    invoice_id = fields.Many2one('kojto.finance.invoices', string='Свързана фактура', copy=False)

    rejected_payment = fields.Selection([('yes', 'да'), ('no', 'не')], string='Отхвърлено плащане', default='no', copy=False)

    examination_paid = fields.Boolean(string='Платено', copy=False)
    examination_paid_date = fields.Date(string='Дата на плащане', copy=False)

    def toggle_rejected_payment(self):
        if self.rejected_payment == 'yes':
            self.rejected_payment = 'no'
        else:
            self.rejected_payment = 'yes'

    def _get_examination_type_domain(self):
        return [('active', '=', True)]

    documents = fields.Boolean(string='Издадени документи', default=False)
    documents_nrnImmunization = fields.Char(string='Номера (НРН на е-имунизации) на ваксинации, извършени като резултат от този преглед')
    documents_nrnReferral = fields.Char(string='Номера (НРН за е-направления) на направления (НЗОК бланки 3, 3а, 4), изписани като резултат от този преглед')
    documents_nrnPrescription = fields.Char(string='Номера (НРН за е-рецепти) на рецепти, изписани като резултат от този преглед')
    documents_medExpNumber = fields.Char(string='Номера на медицинска експертиза като резултат от този преглед')
    documents_issuedTelkDocument = fields.Boolean(string='Указва дали е издаден талон за ТЕЛК в резултат от този преглед', default=False)
    documents_issuedQuickNotice = fields.Boolean(string='Указва дали е издадено бързо известие в резултат от този преглед', default=False)
    documents_issuedInterimReport = fields.Boolean(string='Указва дали е издадена етапна епикриза в резултат от този преглед', default=False)
    documents_issuedMedicalNotice = fields.Boolean(string='Указва дали е издадена медицинска бележка в резултат от този преглед', default=False)

    @api.model
    def create(self, vals):
        record = super(TrinityExamination, self).create(vals)
        record.compute_previous_e_examination()
        return record

    def write(self, vals):
        # Reset payment status if examination_type_id or examination_open_dtm changes
        if 'examination_type_id' in vals or 'examination_open_dtm' in vals:
            vals['examination_paid'] = False
            vals['examination_paid_date'] = False

        result = super(TrinityExamination, self).write(vals)
        self.compute_previous_e_examination()
        return result

    def copy(self, default=None):
        default = dict(default or {})
        current_date = datetime.datetime.now()
        new_record = super(TrinityExamination, self).copy(default=default)
        new_record.compute_open_datetime()
        new_record.compute_patient_age()
        new_record.compute_is_patient_signer_default()
        new_record.compute_previous_e_examination()

        return new_record

    def copy_and_open(self):
        new_record = self.copy()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'trinity.examination',
            'res_id': new_record.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': {'no_breadcrumbs': True},
        }

    @api.depends('e_examination_lrn')
    def _compute_name(self):
        for record in self:
            record.name = record.e_examination_lrn

    def cron_lock_old_examinations(self, batch_size=100):
        locking_period = datetime.datetime.now() - datetime.timedelta(days=45)

        records_to_lock = self.filtered(
            lambda r: r.examination_open_dtm and
                     r.examination_open_dtm < locking_period and
                     not r.isLocked
        )

        if not records_to_lock:
            return True

        total_locked = 0
        total_records = len(records_to_lock)

        for i in range(0, total_records, batch_size):
            batch = records_to_lock[i:i + batch_size]
            batch.write({'isLocked': True})
            total_locked += len(batch)
            _logger.info(f"Locked batch {i//batch_size + 1}: {len(batch)} records (Total: {total_locked}/{total_records})")

        _logger.info(f"Completed: Locked {total_locked} examination(s) older than 30 days")
        return True

    @api.model
    def compute_open_datetime(self):
        date_today = fields.Date.today().strftime('%Y-%m-%d')
        current_user_id = self.env.user.id

        existing_records = self.env['trinity.examination'].search(
            [('e_examination_lrn', 'like', date_today), ('user_id', '=', current_user_id)],
            order='examination_close_dtm desc',
            limit=1
        )

        if existing_records:
            return existing_records.examination_close_dtm + datetime.timedelta(minutes=1)
        else:
            return fields.Datetime.now()

    @api.depends('examination_open_dtm', 'previous_examination_open_dtm')
    def compute_previous_examination_delta(self):
        for record in self:
            if record.examination_open_dtm and record.previous_examination_open_dtm:
                delta = (record.examination_open_dtm - record.previous_examination_open_dtm).days
                record.previous_examination_delta = delta if delta > 0 else False

                if 1 <= delta <= 30:
                    record.previous_examination_open_dtm_30d = True
                else:
                    record.previous_examination_open_dtm_30d = False
            else:
                record.previous_examination_delta = False
                record.previous_examination_open_dtm_30d = False

    @api.depends('patient_identifier_id', 'examination_open_dtm', 'cost_bearer_id')
    def compute_previous_e_examination(self):
        for record in self:
            if not record.patient_identifier_id or not record.examination_open_dtm:
                # Use super().write to avoid recursion
                super(TrinityExamination, record).write({
                    'previous_e_examination_lrn': False,
                    'previous_e_examination_nrn': False,
                    'previous_examination_open_dtm': False,
                })
                continue

            examination_open_date = record.examination_open_dtm.date()
            date_31_days_ago = examination_open_date - datetime.timedelta(days=31)
            day_before_examination_open = examination_open_date - datetime.timedelta(days=1)

            domain = [
                ('patient_identifier_id', '=', record.patient_identifier_id.id),
                ('examination_open_dtm', '>=', date_31_days_ago),
                ('examination_open_dtm', '<', day_before_examination_open),
            ]

            if record.cost_bearer_id:
                domain.append(('cost_bearer_id', '=', record.cost_bearer_id.id))

            last_record = self.search(domain, order='examination_open_dtm desc', limit=1)

            if last_record:
                # Use super().write to avoid recursion
                super(TrinityExamination, record).write({
                    'previous_e_examination_lrn': last_record.e_examination_lrn,
                    'previous_e_examination_nrn': last_record.e_examination_nrn,
                    'previous_examination_open_dtm': last_record.examination_open_dtm
                })
            else:
                super(TrinityExamination, record).write({
                    'previous_e_examination_lrn': False,
                    'previous_e_examination_nrn': False,
                    'previous_examination_open_dtm': False,
                })

    @api.onchange('diagnosis', 'patient_workplace', 'medical_history', 'objective_condition', 'assessment_notes', 'therapy_note', 'conclusion')
    def check_forbidden_characters(self):
        forbidden_fields = {
            'diagnosis': self.diagnosis,
            'medical_history': self.medical_history,
            'objective_condition': self.objective_condition,
            'assessment_notes': self.assessment_notes,
            'therapy_note': self.therapy_note,
            'conclusion': self.conclusion,
        }

        for field, value in forbidden_fields.items():
            if re.search(r'[<>&]', value or ''):
                return {
                    'warning': {
                        'title': _("ГРЕШКА!"),
                        'message': _("Символи <, >, и & не са разрешени в полето %s") % field,
                    }
                }


    def dropdown_empty(self):
        return

    def print_amb_list_as_pdf(self, report_ref=None, report_css_ref=None):
        report_ref = report_ref or getattr(self, "_report_ref_amb_list", None)
        report_css_ref = report_css_ref or getattr(self, "_report_css_ref", None)

        if not report_ref:
            raise UserError(_("Не е предоставен или дефиниран report_ref в модела."))
        if not self.name or not self.name.strip():
            raise UserError(_("Името е задължително за генериране на името на PDF файла."))

        html = self.generate_report_html(report_ref)
        html = self.inject_report_css(html, report_css_ref)

        attachment = self.create_pdf_attachment(html)
        file_name = f"Амбулаторен_лист_{self.name}.pdf"
        attachment.write({'name': file_name})

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true&filename={file_name}",
            "target": "new",
        }

    def print_etap_epikrisis_as_pdf(self, report_ref=None, report_css_ref=None):
        report_ref = report_ref or getattr(self, "_report_ref_etap_epikrisis", None)
        report_css_ref = report_css_ref or getattr(self, "_report_css_ref", None)

        if not report_ref:
            raise UserError(_("Не е предоставен или дефиниран report_ref в модела."))
        if not self.name or not self.name.strip():
            raise UserError(_("Името е задължително за генериране на името на PDF файла."))

        html = self.generate_report_html(report_ref)
        html = self.inject_report_css(html, report_css_ref)

        attachment = self.create_pdf_attachment(html)
        file_name = f"Етапна_епикриза_{self.name}.pdf"
        attachment.write({'name': file_name})

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true&filename={file_name}",
            "target": "new",
        }

    def print_nhif_mri_letter_as_pdf(self, report_ref=None, report_css_ref=None):
        report_ref = report_ref or getattr(self, "_report_ref_nhif_mri_letter", None)
        report_css_ref = report_css_ref or getattr(self, "_report_css_ref_mri", None)

        if not report_ref:
            raise UserError(_("Не е предоставен или дефиниран report_ref в модела."))
        if not self.name or not self.name.strip():
            raise UserError(_("Името е задължително за генериране на името на PDF файла."))

        html = self.generate_report_html(report_ref)
        html = self.inject_report_css(html, report_css_ref)

        attachment = self.create_pdf_attachment(html)
        file_name = f"Писмо_НЗОК_за_ЯМР_{self.name}.pdf"
        attachment.write({'name': file_name})

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true&filename={file_name}",
            "target": "new",
        }

    def print_combined_amb_mri_pdf(self, report_ref_amb=None, report_css_ref_amb=None, report_ref_mri=None, report_css_ref_mri=None):
        amb_result = self.print_amb_list_as_pdf(report_ref_amb, report_css_ref_amb)
        mri_result = self.print_nhif_mri_letter_as_pdf(report_ref_mri, report_css_ref_mri)

        amb_attachment_id = int(amb_result['url'].split('/web/content/')[1].split('?')[0])
        mri_attachment_id = int(mri_result['url'].split('/web/content/')[1].split('?')[0])

        attachment_model = self.env['ir.attachment']
        amb_attachment = attachment_model.browse(amb_attachment_id)
        mri_attachment = attachment_model.browse(mri_attachment_id)

        if not (amb_attachment.exists() and mri_attachment.exists()):
            raise UserError(_("Един или и двата PDF прикачени файла не могат да бъдат намерени."))

        merger = PdfMerger()
        for attachment in [mri_attachment, amb_attachment]:
            pdf_content = base64.b64decode(attachment.datas)  # Decode base64 attachment data
            merger.append(io.BytesIO(pdf_content))

        merged_pdf_io = io.BytesIO()
        merger.write(merged_pdf_io)
        merged_pdf_data = base64.b64encode(merged_pdf_io.getvalue()).decode('utf-8')
        file_name = f"Писмо_НЗОК_за_ЯМР_с_АЛ{self.name}.pdf"

        combined_attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': merged_pdf_data,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        merged_pdf_io.close()
        merger.close()

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{combined_attachment.id}?download=true&filename={file_name}",
            "target": "new",
        }

    _report_ref_amb_list = "trinity_examination.trinity_examination_pdf_wp_al"
    _report_ref_etap_epikrisis = "trinity_examination.trinity_examination_pdf_wp_ee"
    _report_ref_nhif_mri_letter = "trinity_examination.trinity_examination_pdf_wp_nhif_mri_letter"

    _report_css_ref = "trinity_examination_pdf_wp_al.css"
    _report_css_ref_mri = "trinity_examination_pdf_wp_mri.css"

    @api.model
    def generate_e_examination_lrn(self):
        date_today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat
        existing_records = self.env['trinity.examination'].sudo().search(
            [('e_examination_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='e_examination_lrn desc',
            limit=1
        )

        if existing_records:
            last_sequence = existing_records.e_examination_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1

        lrn_value = f'{date_today}-{current_company_vat}-{sequence_number:04d}'

        return lrn_value

    @api.onchange('template_id')
    def use_template(self):
        if self.template_id:
            self.icd_codes = self.template_id.icd_codes
            self.diagnosis = self.template_id.diagnosis
            self.medical_history = self.template_id.medical_history
            self.objective_condition = self.template_id.objective_condition
            self.assessment_notes = self.template_id.assessment_notes
            self.therapy_note = self.template_id.therapy_note
            self.conclusion = self.template_id.conclusion

    @api.onchange('template_e_examination_lrn')
    def use_template_e_examination_lrn(self):
        if self.template_e_examination_lrn:
            self.icd_codes = self.template_e_examination_lrn.icd_codes
            self.diagnosis = self.template_e_examination_lrn.diagnosis
            self.medical_history = self.template_e_examination_lrn.medical_history
            self.objective_condition = self.template_e_examination_lrn.objective_condition
            self.assessment_notes = self.template_e_examination_lrn.assessment_notes
            self.therapy_note = self.template_e_examination_lrn.therapy_note
            self.conclusion = self.template_e_examination_lrn.conclusion

    @api.depends('patient_birth_date', 'examination_open_dtm')
    def compute_patient_age(self):
        for patient in self:
            if patient.patient_birth_date and patient.examination_open_dtm:
                birth_date = fields.Datetime.from_string(patient.patient_birth_date)
                open_date = fields.Datetime.from_string(patient.examination_open_dtm)
                age_years = open_date.year - birth_date.year
                if open_date.month < birth_date.month or (open_date.month == birth_date.month and open_date.day < birth_date.day):
                    age_years -= 1
                patient.patient_age = age_years
            else:
                patient.patient_age = False

    def create_kojto_finance_invoice_from_examination(self):

        def get_or_create(model, search_domain, create_vals=None, limit=1):
            record = self.env[model].sudo().search(search_domain, limit=limit)
            if not record and create_vals:
                record = self.env[model].sudo().create(create_vals)
            return record

        def get_with_fallback(model, contact_id, lang='bg_BG'):
            record = self.env[model].search([
                ('contact_id', '=', contact_id),
                ('language_id.code', '=', lang),
                ('active', '=', True)
            ], limit=1)
            if not record:
                record = self.env[model].search([
                    ('contact_id', '=', contact_id),
                    ('active', '=', True)
                ], limit=1)
            return record

        for report in self:
            company = self.env['kojto.contacts'].search(
                [('res_company_id', '=', self.env.company.id)], limit=1
            )
            if not company:
                raise UserError(_("No company found for the current user. Please configure a company first."))

            # Codes
            year_suffix = str(fields.Date.today().year)[-2:]
            maincode = get_or_create(
                'kojto.commission.main.codes',
                [('maincode', '=', "MC")],
                {'maincode': "MC", 'name': "MC", 'description': "MC"}
            )
            code = get_or_create(
                'kojto.commission.codes',
                [('code', '=', f"{year_suffix}000"), ('maincode_id', '=', maincode.id)],
                {
                    'code': f"{year_suffix}000",
                    'name': f"MC.{year_suffix}000",
                    'description': f"MC.{year_suffix}000",
                    'maincode_id': maincode.id,
                }
            )
            subcode = get_or_create(
                'kojto.commission.subcodes',
                [('subcode', '=', "001"), ('maincode_id', '=', maincode.id), ('code_id', '=', code.id)],
                {
                    'subcode': "001",
                    'name': f"MC.{year_suffix}000.001",
                    'description': f"MC.{year_suffix}000.001",
                    'maincode_id': maincode.id,
                    'code_id': code.id,
                }
            )

            # VAT treatment
            vat_treatment = self.env['kojto.finance.vat.treatment'].search([('code', '=', '101')], limit=1)
            if not vat_treatment:
                self.env['kojto.finance.vat.treatment'].create({
                    'code': '101',
                    'vat_in_out_type': 'outgoing',
                    'vat_treatment_type': 'no_vat',
                })
                raise UserError(_("VAT treatment '101' not found. Please configure it first."))

            # Counterparty (patient)
            patient = getattr(report, 'patient_identifier_id', None)
            if not patient:
                raise UserError(_("No patient found for this examination. Cannot create invoice without counterparty."))

            counterparty = self.env['kojto.contacts'].search([
                ('registration_number', '=', patient.identifier),
                ('contact_type', '=', 'person')
            ], limit=1)
            if not counterparty:
                counterparty = self.env['kojto.contacts'].create({
                    'name': patient.patient_full_name or f"{patient.first_name} {patient.last_name}".strip(),
                    'contact_type': 'person',
                    'language_id': self.env.ref('base.lang_bg').id,
                    'registration_number': patient.identifier,
                    'registration_number_type': getattr(patient.identifier_type, 'description', False),
                })

            company = self.env['kojto.contacts'].search([('res_company_id', '=', self.env.user.company_id.id)], limit=1)

            if company:
                company_bank_account = self.env['kojto.base.bank.accounts'].search([
                    ('contact_id', '=', company.id),
                    ('account_type', '=', 'cash'),
                    ('active', '=', True)
                ], limit=1)

                if not company_bank_account:
                    raise UserError(_("No bank account found for the company. Please configure a bank account first."))

            # Lookups with fallback
            company_name = get_with_fallback('kojto.base.names', company.id)
            company_address = get_with_fallback('kojto.base.addresses', company.id)
            counterparty_name = get_with_fallback('kojto.base.names', counterparty.id)
            counterparty_address = get_with_fallback('kojto.base.addresses', counterparty.id)

            company_email = self.env['kojto.base.emails'].search([('contact_id', '=', company.id), ('active', '=', True)], limit=1)
            company_phone = self.env['kojto.base.phones'].search([('contact_id', '=', company.id), ('active', '=', True)], limit=1)
            counterparty_email = self.env['kojto.base.emails'].search([('contact_id', '=', counterparty.id), ('active', '=', True)], limit=1)
            counterparty_phone = self.env['kojto.base.phones'].search([('contact_id', '=', counterparty.id), ('active', '=', True)], limit=1)

            # Invoice
            invoice_vals = {
                'document_in_out_type': 'outgoing',
                'invoice_type': 'invoice',
                'company_id': company.id,
                'company_name_id': company_name.id or False,
                'company_address_id': company_address.id or False,
                'company_email_id': company_email.id or False,
                'company_phone_id': company_phone.id or False,
                'counterparty_id': counterparty.id,
                'counterparty_name_id': counterparty_name.id or False,
                'counterparty_address_id': counterparty_address.id or False,
                'counterparty_email_id': counterparty_email.id or False,
                'counterparty_phone_id': counterparty_phone.id or False,
                'company_bank_account_id': company_bank_account.id,
                'subcode_id': subcode.id,
                'currency_id': self.env.ref('base.BGN').id,
                'language_id': self.env.ref('base.lang_bg').id,
                'date_issue': fields.Date.today(),
                'date_due': fields.Date.today() + timedelta(days=7),
                'date_tax_event': fields.Date.today(),
                'payment_terms_id': False,
                'invoice_vat_treatment_id': vat_treatment.id,
                'exchange_rate_to_bgn': 1.0,
                'exchange_rate_to_eur': 0.51129,
                'subject': self.examination_type_id.name,
                'accounting_op_date': (fields.Date.today().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
                'payment_terms_id': self.env['kojto.base.payment.terms'].search([('name', '=', 'Плащане в брой')], limit=1).id,
            }
            invoice = self.env['kojto.finance.invoices'].create(invoice_vals)

            report.invoice_id = invoice.id

            content = self.env['kojto.finance.invoice.contents'].create({
                'invoice_id': invoice.id,
                'position': 1,
                'name': report.examination_type_id.name if report.examination_type_id else report.examination_type or 'Неизвестен тип преглед',
                'quantity': 1.0,
                'unit_price': report.examination_type_id_price.price_onsite if report.examination_type_id_price else 0.0,
                'vat_rate': 0.0,
                'vat_treatment_id': False,
                'subcode_id': subcode.id,
            })
            content._compute_pre_vat_total()

            return {
                'name': _('Invoice'),
                'type': 'ir.actions.act_window',
                'res_model': 'kojto.finance.invoices',
                'view_mode': 'form',
                'target': 'current',
                'res_id': invoice.id,
            }

    def issue_referral(self):
        for report in self:
            issue_vals = {
                'referral_basedOn_lrn': report.id,
                'diagnosis_code': report.icd_codes[0].id if report.icd_codes else False,
            }

            referral = self.env['trinity.referral.issue'].create(issue_vals)

            referral.compute_R001()

            action = {
                'name': 'Издаване на направление',
                'type': 'ir.actions.act_window',
                'res_model': 'trinity.referral.issue',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'res_id': referral.id,
            }

            return action

    def issue_prescription(self):
        for report in self:
            issue_vals = {
                'prescription_basedOn_lrn': report.id,
                'medication_icd_code': report.icd_codes[0].id if report.icd_codes else False,
            }

            prescription = self.env['trinity.prescription'].create(issue_vals)

            prescription.compute_P001()

            action = {
                'name': 'Издаване на рецепта',
                'type': 'ir.actions.act_window',
                'res_model': 'trinity.prescription',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'res_id': prescription.id,
            }

            return action

    def issue_medical_notice(self):
        for report in self:
            issue_vals = {
                'medicalNotice_basedOn_lrn': report.id,
                'medicalNotice_code': report.icd_codes[0].id if report.icd_codes else False,
            }

            medical_notice = self.env['trinity.medical.notice'].create(issue_vals)

            medical_notice.compute_C041()

            action = {
                'name': 'Издаване на медицинска бележка',
                'type': 'ir.actions.act_window',
                'res_model': 'trinity.medical.notice',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
                'res_id': medical_notice.id,
            }

            return action

    @api.depends('examination_type_id', 'examination_open_dtm')
    def _compute_examination_type_id_price(self):
        for record in self:
            if not record.examination_type_id or not record.examination_open_dtm:
                record.examination_type_id_price = False
                continue

            examination_date = record.examination_open_dtm.date()
            active_prices = record.examination_type_id.prices.filtered(
                lambda p: p.active_from <= examination_date and
                (p.active_until is False or p.active_until >= examination_date)
            )

            if active_prices:
                record.examination_type_id_price = active_prices[0].id
            else:
                record.examination_type_id_price = False

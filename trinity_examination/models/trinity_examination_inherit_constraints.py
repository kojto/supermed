# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError

class TrinityExaminationInheritConstraints(models.Model):
    _inherit = "trinity.examination"

    @api.constrains('patient_identifier_id', 'patient_identifier_id.identifier_type')
    def _check_patient_identifier_type(self):
        for record in self:
            if record.patient_identifier_id and record.patient_identifier_id.identifier:
                if not record.patient_identifier_id.identifier_type:
                    raise ValidationError(_('CDX08: Типът на идентификатора на пациента е задължителен, когато е предоставен идентификатор.'))

    @api.constrains('patient_isPregnant', 'patient_gestationalWeek')
    def _check_pregnancy_gestational_week(self):
        for record in self:
            if record.patient_isPregnant:
                if not record.patient_gestationalWeek:
                    raise ValidationError(_('CDX02: Гестационната седмица е задължителна за бременни жени.'))

    @api.constrains('patient_country', 'patient_county', 'patient_ekatte_key')
    def _check_bulgarian_address(self):
        for record in self:
            if record.patient_country and record.patient_country.key == 'BG':
                if not record.patient_county:
                    raise ValidationError(_('CDX04: Областта е задължителна за български адреси.'))
                if not record.patient_ekatte_key:
                    raise ValidationError(_('CDX04: ЕКАТТЕ е задължително за български адреси.'))

    @api.constrains('performer_role', 'deputizing_dr_performing_doctor_id')
    def _check_deputy_doctor(self):
        for record in self:
            if record.performer_role and record.performer_role.key != "1":
                if not record.deputizing_dr_performing_doctor_id:
                    raise ValidationError(_('CDX05: Заместващият лекар е задължителен, когато ролята на изпълняващия не е "1" (титуляр).'))
    """
    @api.constrains('basedOn_e_examination_nrn', 'directedBy')
    def _check_directed_by(self):
        for record in self:
            if not record.basedOn_e_examination_nrn:
                if not record.directedBy:
                    raise ValidationError(_('CDX06: Насочващият лекар е задължителен, когато не е предоставен basedOn.'))

    @api.constrains('main_dr_performing_qualification_code', 'financingSource', 'examination_purpose', 'secondary_examination', 'basedOn_e_examination_nrn', 'previous_e_examination_nrn')
    def _check_based_on_examination(self):
        for record in self:
            if ((record.main_dr_performing_qualification_code and
                 record.main_dr_performing_qualification_code.key not in ('1043', '0000') and
                 record.financingSource and record.financingSource.key == '2' and
                 record.examination_purpose and record.examination_purpose.key != '12') or
                record.secondary_examination):
                if not (record.basedOn_e_examination_nrn or record.previous_e_examination_nrn):
                    raise ValidationError(_('CDX09: Задължително е да се въвдеде НРН на преглед или направление, на което този преглед е основан.'))

    @api.constrains('isPatientSigner', 'parent_identifier_id')
    def _check_patient_signer(self):
        for record in self:
            if not record.isPatientSigner:
                if not record.parent_identifier_id:
                    raise ValidationError(_('CDX22: Информацията за подписващия е задължителна, когато пациентът не е подписващият.'))
    """

    @api.constrains('patient_identifier_id', 'patient_isPregnant', 'patient_isBreastFeeding')
    def _check_female_patient_status(self):
        for record in self:
            if (record.patient_identifier_id and record.patient_identifier_id.gender and
                record.patient_identifier_id.gender.key == "2"):
                if record.patient_isPregnant is None:
                    raise ValidationError(_('CDX23: Статус на бременността е задължителен за женски пациенти.'))
                if record.patient_isBreastFeeding is None:
                    raise ValidationError(_('CDX23: Статус на кърменето е задължителен за женски пациенти.'))

    @api.constrains('examination_purpose', 'examination_plannedType')
    def _check_planned_examination_type(self):
        for record in self:
            if (record.examination_purpose and
                record.examination_purpose.key in ['2', '3', '5', '6']):
                if not record.examination_plannedType:
                    raise ValidationError(_('CDX24: Планираният тип преглед е задължителен за тази цел на прегледа.'))

    @api.constrains('examination_type_id', 'financingSource', 'icd_codes')
    def _check_icd_codes_for_financing_source(self):
        for record in self:
            if (record.financingSource and record.financingSource.key in ['2', '3']):
                if not record.icd_codes or len(record.icd_codes) == 0:
                    raise ValidationError(_('CDX25: Поне един МКБ код е задължителен, когато източникът на финансиране е НЗОК или ДЗОФ.'))

    @api.constrains('e_examination_lrn', 'examination_open_dtm', 'patient_identifier_id', 'patient_first_name', 'patient_last_name')
    def _check_examination_identification(self):
        for record in self:
            if not record.e_examination_nrn:
                if not (record.examination_open_dtm and
                        (record.patient_identifier_id.identifier if record.patient_identifier_id else False or
                         (record.patient_first_name and record.patient_last_name) or
                         record.e_examination_lrn)):
                    raise ValidationError(_('CDX10: Идентификацията на прегледа е задължителна - трябва да има отворена дата и идентификатор/име/LRN.'))

    @api.constrains('patient_identifier_id', 'examination_open_dtm', 'examination_close_dtm', 'icd_code', 'icd_codes', 'diagnosis', 'medical_history', 'objective_condition', 'assessment_notes', 'therapy_note', 'main_dr_performing_doctor_id', 'examination_type_id', 'patient_isPregnant', 'patient_isBreastFeeding', 'patient_gestationalWeek', 'patient_weight', 'clinicalStatus', 'verificationStatus', 'onsetDateTime', 'conclusion', 'basedOn_e_examination_lrn', 'basedOn_e_examination_nrn', 'directedBy', 'financingSource', 'examination_paid', 'examination_paid_date')
    def _check_examination_locked(self):
        if self.env.context.get('skip_lock_check'):
            return

        if not self.env.user.has_group('trinity_medical_facility.group_trinity_doctor_users'):
            return

        for record in self:
            if record.isLocked:
                raise ValidationError(_('ПРЕГЛЕДЪТ Е ЗАКЛЮЧЕН! МОЛЯ ОТКЛЮЧЕТЕ ГО ПРЕДИ РЕДАКЦИЯ.'))

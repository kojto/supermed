# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrinityReferralIssueTemplate(models.Model):
    _name = 'trinity.referral.issue.template'
    _description = 'Trinity Referral Issue Template'
    _rec_name = 'name'
    _order = 'referral_category asc, referral_type asc, referral_qualification asc'

    name = fields.Char(string='Име на шаблон', required=True)

    referral_issue_id = fields.Many2one('trinity.referral.issue', string='Създаден от направление')

    @api.onchange('referral_issue_id')
    def _onchange_referral_issue_id(self):
        if self.referral_issue_id:
            referral = self.referral_issue_id

            self.referral_category = referral.referral_category
            self.referral_type = referral.referral_type
            self.referral_financingSource = referral.referral_financingSource
            self.referral_qualification = referral.referral_qualification
            self.laboratory_code_root = referral.laboratory_code_root
            self.specializedActivities_code_root = referral.specializedActivities_code_root
            self.hospitalization_admissionType = referral.hospitalization_admissionType
            self.hospitalization_directedBy = referral.hospitalization_directedBy
            self.hospitalization_clinicalPathway = referral.hospitalization_clinicalPathway
            self.hospitalization_outpatientProcedure = referral.hospitalization_outpatientProcedure
            self.medicalExpertise_examType = referral.medicalExpertise_examType
            self.workIncapacity_reason = referral.workIncapacity_reason
            self.workIncapacity_addressType = referral.workIncapacity_addressType
            self.workIncapacity_isHomeVisitNecessary = referral.workIncapacity_isHomeVisitNecessary
            self.employer_name = referral.employer_name
            self.employer_identificationCode = referral.employer_identificationCode
            self.employer_position = referral.employer_position
            self.employer_phone = referral.employer_phone
            self.employer_email = referral.employer_email
            self.employer_country = referral.employer_country
            self.employer_county = referral.employer_county
            self.employer_ekatte = referral.employer_ekatte
            self.employer_city = referral.employer_city
            self.employer_line = referral.employer_line
            self.employer_postalCode = referral.employer_postalCode
            self.attached_documents_type = referral.attached_documents_type
            self.attached_documents_date = referral.attached_documents_date
            self.attached_documents_number = referral.attached_documents_number
            self.attached_documents_isNrn = referral.attached_documents_isNrn
            self.attached_documents_note = referral.attached_documents_note
            self.comorbidity_code = referral.comorbidity_code
            self.comorbidity_additionalCode = referral.comorbidity_additionalCode
            self.comorbidity_use = referral.comorbidity_use
            self.comorbidity_rank = referral.comorbidity_rank
            self.comorbidity_clinicalStatus = referral.comorbidity_clinicalStatus
            self.comorbidity_verificationStatus = referral.comorbidity_verificationStatus
            self.comorbidity_onsetDateTime = referral.comorbidity_onsetDateTime
            self.comorbidity_diagnosis_note = referral.comorbidity_diagnosis_note
            self.comorbidity_note = referral.comorbidity_note
            self.subject_nhifInsuranceNumber = referral.subject_nhifInsuranceNumber
            self.subject_nationality = referral.subject_nationality
            self.response_sender = referral.response_sender
            self.response_senderId = referral.response_senderId
            self.response_recipient = referral.response_recipient
            self.response_recipientId = referral.response_recipientId
            self.response_messageId = referral.response_messageId
            self.response_messageType = referral.response_messageType
            self.response_createdOn = referral.response_createdOn
            self.cancelReason = referral.cancelReason


    # Referral fields
    referral_category = fields.Many2one('trinity.nomenclature.cl014', string='Категория')
    referral_category_key = fields.Char(related='referral_category.key', string='Вид направление')
    referral_category_name = fields.Char(related='referral_category.name', string='Вид направление')
    referral_type = fields.Many2one('trinity.nomenclature.cl021', string='Причина за издаване на направление')
    referral_financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Източник на финансиране')
    referral_qualification = fields.Many2one('trinity.nomenclature.cl006', string='Код на специалност')
    referral_qualification_name = fields.Char(related='referral_qualification.meta_nhif_name', string='За специалност')
    referral_qualification_nhif = fields.Char(related='referral_qualification.meta_nhif_code', string='Специалност по НЗОК')

    # Laboratory fields
    laboratory_code_root = fields.Many2one('trinity.nomenclature.cl022', string='Код на МД дейност')
    laboratory_code = fields.Char(related='laboratory_code_root.meta_nhif_code', string='НЗОК код')
    laboratory_code_price = fields.Float(related='laboratory_code_root.price', string='Цена')

    # Specialized Activities fields
    specializedActivities_code_root = fields.Many2one('trinity.nomenclature.cl050', string='Код на ВС дейност')
    specializedActivities_code = fields.Char(related='specializedActivities_code_root.meta_nhif_code', string='ВС дейност по НЗОК')
    specializedActivities_code_price = fields.Float(string='Цена')

    # Hospitalization fields
    hospitalization_admissionType = fields.Many2one('trinity.nomenclature.cl059', string='Вид прием')
    hospitalization_directedBy = fields.Many2one('trinity.nomenclature.cl060', string='Насочен от')
    hospitalization_clinicalPathway = fields.Many2one('trinity.nomenclature.cl062', string='КП')
    hospitalization_clinicalPathway_key = fields.Char(related='hospitalization_clinicalPathway.key', string='КП')
    hospitalization_outpatientProcedure = fields.Many2one('trinity.nomenclature.cl063', string='Амбулаторни процедури')

    # Medical Expertise fields
    medicalExpertise_examType = fields.Many2one('trinity.nomenclature.cl051', string="Вид експертиза")

    # Work Incapacity fields
    workIncapacity_reason = fields.Many2one('trinity.nomenclature.cl052', string='Причина')
    workIncapacity_addressType = fields.Many2one('trinity.nomenclature.cl053', string='Вид адрес')
    workIncapacity_isHomeVisitNecessary = fields.Boolean(string='Нужно ли е домашно посещение', default=False)

    # Employer fields
    employer_name = fields.Char(string='Име')
    employer_identificationCode = fields.Char(string='Идентификационен код')
    employer_position = fields.Char(string='Длъжност')
    employer_phone = fields.Char(string='Телефон')
    employer_email = fields.Char(string='Имейл')
    employer_country = fields.Many2one('trinity.nomenclature.cl005', string='Държава')
    employer_county = fields.Many2one('trinity.nomenclature.cl041', string='Област')
    employer_ekatte = fields.Many2one('trinity.nomenclature.cl044', string='ЕКАТТЕ')
    employer_city = fields.Char(string='Град', default='София')
    employer_line = fields.Char(string='Адрес')
    employer_postalCode = fields.Char(string='Пощенски код', default='1000')

    # Attached Documents fields
    attached_documents_type = fields.Many2one('trinity.nomenclature.cl102', string='Прикачени документи')
    attached_documents_date = fields.Date(string='Дата')
    attached_documents_number = fields.Char(string='Number')
    attached_documents_isNrn = fields.Char(string='Is NRN')
    attached_documents_note = fields.Char(string='Note')

    # Comorbidity fields
    comorbidity_code = fields.Char(string='МКБ код')
    comorbidity_additionalCode = fields.Char(string='Допълнителен МКБ')
    comorbidity_use = fields.Many2one('trinity.nomenclature.cl076', string='Use')
    comorbidity_rank = fields.Char(string='Ранг')
    comorbidity_clinicalStatus = fields.Char(string='Клинично състояние')
    comorbidity_verificationStatus = fields.Char(string='Статус на верификация')
    comorbidity_onsetDateTime = fields.Char(string='Дата и час на началото')
    comorbidity_diagnosis_note = fields.Char(string='Бележка')
    comorbidity_note = fields.Char(string='Бележка')

    # Subject fields (patient information)
    subject_nhifInsuranceNumber = fields.Char(string='Номер на застраховка')
    subject_nationality = fields.Char(string='Националност')

    # Response fields
    response_sender = fields.Many2one('trinity.nomenclature.cl018', string='Изпращач')
    response_senderId = fields.Char(string='Sender ID')
    response_recipient = fields.Many2one('trinity.nomenclature.cl018', string='Получател')
    response_recipientId = fields.Char(string='Recipient ID')
    response_messageId = fields.Char(string='ID на съобщението')
    response_messageType = fields.Char(string='Тип на съобщението')
    response_createdOn = fields.Date(string='Създадено на')

    # Cancel reason
    cancelReason = fields.Char(string='Причина за анулирането', default='Пациентът няма нужда от направлението')

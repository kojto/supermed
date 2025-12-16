# -*- coding: utf-8 -*-

import base64
import datetime
import logging
import uuid
import xml.etree.ElementTree as ET

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class TrinityReferralIssue(models.Model):
    _name = 'trinity.referral.issue'
    _description = 'Trinity Referral Issue'
    _rec_name = 'referral_lrn'
    _order = 'referral_authoredOn desc, create_date desc'
    _inherit = ["trinity.library.nhif.qes"]

    template_id = fields.Many2one('trinity.referral.issue.template', string='Шаблон')

    referral_basedOn_lrn = fields.Many2one('trinity.examination', string='Основано на амб. №', required=True)
    referral_basedOn_nrn = fields.Char(related='referral_basedOn_lrn.e_examination_nrn', string='Основано на преглед: ')
    referral_financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Източник на финансиране', default=lambda self: self.env['trinity.nomenclature.cl069'].search([('key', '=', '2')], limit=1))
    referral_rhifAreaNumber = fields.Many2one('trinity.nomenclature.cl029', related='referral_basedOn_lrn.patient_rhifareanumber_key')
    referral_main_dr_performing_doctor_id = fields.Many2one(related='referral_basedOn_lrn.main_dr_performing_doctor_id')

    referral_lrn = fields.Char(string='LRN', required=True, default=lambda self: self.generate_referral_lrn(), copy=False)

    referral_authoredOn = fields.Date(string='Дата на издаване', default=fields.Date.today)

    @api.model
    def generate_referral_lrn(self):
        date_today = datetime.datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat
        existing_records = self.env['trinity.referral.issue'].sudo().search(
            [('referral_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='referral_lrn desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.referral_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1

        lrn_value = f'R-{date_today}-{current_company_vat}-{sequence_number:04d}'
        return lrn_value

    referral_category = fields.Many2one('trinity.nomenclature.cl014', string='Категория', default=lambda self: self.env['trinity.nomenclature.cl014'].search([('key', '=', 'R2')], limit=1).id)
    referral_category_key = fields.Char(related='referral_category.key', string='Вид направление')
    referral_category_name = fields.Char(related='referral_category.name', string='Вид направление')
    referral_type = fields.Many2one('trinity.nomenclature.cl021', string='Причина за издаване на направление', default=lambda self: self.env['trinity.nomenclature.cl021'].search([('key', '=', '1')], limit=1).id)

    referral_qualification = fields.Many2one('trinity.nomenclature.cl006', string='Код на специалност')
    referral_qualification_name = fields.Char(related='referral_qualification.meta_nhif_name', string='За специалност')
    referral_qualification_nhif = fields.Char(related='referral_qualification.meta_nhif_code', string='Специалност по НЗОК')

    referral_price = fields.Float(string='Цена', compute='_compute_referral_price')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            template = self.template_id

            # Copy template fields to the current record
            self.referral_category = template.referral_category
            self.referral_type = template.referral_type
            self.referral_financingSource = template.referral_financingSource
            self.referral_qualification = template.referral_qualification
            self.laboratory_code_root = template.laboratory_code_root
            self.specializedActivities_code_root = template.specializedActivities_code_root
            self.hospitalization_admissionType = template.hospitalization_admissionType
            self.hospitalization_directedBy = template.hospitalization_directedBy
            self.hospitalization_clinicalPathway = template.hospitalization_clinicalPathway
            self.hospitalization_outpatientProcedure = template.hospitalization_outpatientProcedure
            self.medicalExpertise_examType = template.medicalExpertise_examType
            self.workIncapacity_reason = template.workIncapacity_reason
            self.workIncapacity_addressType = template.workIncapacity_addressType
            self.workIncapacity_isHomeVisitNecessary = template.workIncapacity_isHomeVisitNecessary
            self.employer_name = template.employer_name
            self.employer_identificationCode = template.employer_identificationCode
            self.employer_position = template.employer_position
            self.employer_phone = template.employer_phone
            self.employer_email = template.employer_email
            self.employer_country = template.employer_country
            self.employer_county = template.employer_county
            self.employer_ekatte = template.employer_ekatte
            self.employer_city = template.employer_city
            self.employer_line = template.employer_line
            self.employer_postalCode = template.employer_postalCode
            self.attached_documents_type = template.attached_documents_type
            self.attached_documents_date = template.attached_documents_date
            self.attached_documents_number = template.attached_documents_number
            self.attached_documents_isNrn = template.attached_documents_isNrn
            self.attached_documents_note = template.attached_documents_note
            self.comorbidity_code = template.comorbidity_code
            self.comorbidity_additionalCode = template.comorbidity_additionalCode
            self.comorbidity_use = template.comorbidity_use
            self.comorbidity_rank = template.comorbidity_rank
            self.comorbidity_clinicalStatus = template.comorbidity_clinicalStatus
            self.comorbidity_verificationStatus = template.comorbidity_verificationStatus
            self.comorbidity_onsetDateTime = template.comorbidity_onsetDateTime
            self.comorbidity_diagnosis_note = template.comorbidity_diagnosis_note
            self.comorbidity_note = template.comorbidity_note
            self.subject_nhifInsuranceNumber = template.subject_nhifInsuranceNumber
            self.subject_nationality = template.subject_nationality
            self.response_sender = template.response_sender
            self.response_senderId = template.response_senderId
            self.response_recipient = template.response_recipient
            self.response_recipientId = template.response_recipientId
            self.response_messageId = template.response_messageId
            self.response_messageType = template.response_messageType
            self.response_createdOn = template.response_createdOn
            self.cancelReason = template.cancelReason

    @api.onchange('referral_category', 'laboratory_code_root', 'specializedActivities_code_root')
    def _compute_referral_price(self):
        for record in self:
            if record.referral_category_key == 'R1':
                record.referral_price = record.laboratory_code_price if record.laboratory_code_price else False
            elif record.referral_category_key == 'R3':
                record.referral_price = record.specializedActivities_code_price if record.specializedActivities_code_price else False
            else:
                record.referral_price = False

    laboratory_code_root = fields.Many2one('trinity.nomenclature.cl022', string='Код на МД дейност')
    laboratory_code = fields.Char(related='laboratory_code_root.meta_nhif_code', string='НЗОК код')
    laboratory_code_price = fields.Float(related='laboratory_code_root.price', string='Цена')

    specializedActivities_code_root = fields.Many2one('trinity.nomenclature.cl050', string='Код на ВС дейност')
    specializedActivities_code = fields.Char(related='specializedActivities_code_root.meta_nhif_code', string='ВС дейност по НЗОК')
    specializedActivities_code_price = fields.Float(string='Цена')

    hospitalization_admissionType = fields.Many2one('trinity.nomenclature.cl059', string='Вид прием')
    hospitalization_directedBy = fields.Many2one('trinity.nomenclature.cl060', string='Насочен от')
    hospitalization_clinicalPathway = fields.Many2one('trinity.nomenclature.cl062', string='КП')
    hospitalization_clinicalPathway_key = fields.Char(related='hospitalization_clinicalPathway.key', string='КП')
    hospitalization_outpatientProcedure = fields.Many2one('trinity.nomenclature.cl063', string='Амбулаторни процедури')

    medicalExpertise_examType = fields.Many2one('trinity.nomenclature.cl051', string="Вид експертиза")

    workIncapacity_reason = fields.Many2one('trinity.nomenclature.cl052', string='Причина')
    workIncapacity_addressType = fields.Many2one('trinity.nomenclature.cl053', string='Вид адрес')
    workIncapacity_isHomeVisitNecessary = fields.Boolean(string='Нужно ли е домашно посещение', default=False)

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

    attached_documents_type = fields.Many2one('trinity.nomenclature.cl102', string='Прикачени документи')
    attached_documents_date = fields.Date(string='Дата')
    attached_documents_number = fields.Char(string='Number')
    attached_documents_isNrn = fields.Char(string='Is NRN')
    attached_documents_note = fields.Char(string='Note')

    diagnosis_code = fields.Many2one(related='referral_basedOn_lrn.icd_code')
    diagnosis_code_key = fields.Char(related='diagnosis_code.key')
    diagnosis_use = fields.Many2one(related='referral_basedOn_lrn.diagnosis_use')
    diagnosis_rank = fields.Many2one(related='referral_basedOn_lrn.diagnosis_rank')
    diagnosis_clinicalStatus = fields.Many2one(related='referral_basedOn_lrn.clinicalStatus')
    diagnosis_verificationStatus = fields.Many2one(related='referral_basedOn_lrn.verificationStatus')
    diagnosis_onsetDateTime = fields.Datetime(related='referral_basedOn_lrn.onsetDateTime')
    diagnosis_note = fields.Text(related='referral_basedOn_lrn.diagnosis')

    comorbidity_code = fields.Char(string='МКБ код')
    comorbidity_additionalCode = fields.Char(string='Допълнителен МКБ')
    comorbidity_use = fields.Many2one('trinity.nomenclature.cl076', string='Use', default=lambda self: self.env['trinity.nomenclature.cl076'].search([('key', '=', '3')], limit=1))
    comorbidity_rank = fields.Char(string='Ранг')
    comorbidity_clinicalStatus = fields.Char(string='Клинично състояние')
    comorbidity_verificationStatus = fields.Char(string='Статус на верификация')
    comorbidity_onsetDateTime = fields.Char(string='Дата и час на началото')
    comorbidity_diagnosis_note = fields.Char(string='Бележка')
    comorbidity_note = fields.Char(string='Бележка')

    subject_identifier = fields.Many2one(related='referral_basedOn_lrn.patient_identifier_id')
    subject_identifierType = fields.Many2one(related='referral_basedOn_lrn.patient_identifier_type')
    subject_nhifInsuranceNumber = fields.Char(string='Номер на застраховка')
    subject_birthDate = fields.Date(related='referral_basedOn_lrn.patient_birth_date')
    subject_gender = fields.Many2one(related='referral_basedOn_lrn.patient_gender')
    subject_given = fields.Char(related='referral_basedOn_lrn.patient_first_name')
    subject_middle = fields.Char(related='referral_basedOn_lrn.patient_middle_name')
    subject_family = fields.Char(related='referral_basedOn_lrn.patient_last_name')
    subject_full = fields.Char(related='referral_basedOn_lrn.patient_full_name')

    subject_phone = fields.Char(related='referral_basedOn_lrn.patient_identifier_id.phone')
    subject_country = fields.Many2one(related='referral_basedOn_lrn.patient_country')
    subject_county = fields.Many2one(related='referral_basedOn_lrn.patient_county')
    subject_ekatte = fields.Many2one(related='referral_basedOn_lrn.patient_ekatte_key')
    subject_nationality = fields.Char(string='Националност')
    subject_city = fields.Char(related='referral_basedOn_lrn.patient_city')
    subject_postalCode = fields.Char(related='referral_basedOn_lrn.patient_zip_code')

    subject_age = fields.Float(related='referral_basedOn_lrn.patient_age')
    subject_weight = fields.Char(related='referral_basedOn_lrn.patient_weight')
    subject_maritalStatus = fields.Many2one(related='referral_basedOn_lrn.patient_maritalStatus')
    subject_education = fields.Many2one(related='referral_basedOn_lrn.patient_education')
    subject_workplace = fields.Char(related='referral_basedOn_lrn.patient_workplace')
    subject_profession = fields.Char(related='referral_basedOn_lrn.patient_profession')

    requester_pmi = fields.Many2one(related='referral_basedOn_lrn.main_dr_performing_doctor_id', string='Издател')
    requester_doctor_full_name = fields.Char(related='referral_basedOn_lrn.main_dr_performing_full_name')
    requester_pmiDeputy = fields.Many2one(related='referral_basedOn_lrn.deputizing_dr_performing_doctor_id')
    requester_qualification_nhif = fields.Char(related='referral_basedOn_lrn.main_dr_performing_qualification_code_nhif')
    requester_qualification = fields.Many2one(related='referral_basedOn_lrn.main_dr_performing_qualification_code')
    requester_role = fields.Many2one(related="referral_basedOn_lrn.performer_role")
    requester_practiceNumber = fields.Char(related='referral_basedOn_lrn.main_dr_performing_practiceNumber')
    requester_rhifAreaNumber = fields.Many2one(related='referral_basedOn_lrn.main_dr_performing_rhifareanumber_key')
    requester_nhifNumber = fields.Char(related='referral_basedOn_lrn.main_dr_performing_nhif_Number')
    requester_phone = fields.Char(related='referral_basedOn_lrn.main_dr_performing_phone')
    requester_email = fields.Char(related='referral_basedOn_lrn.main_dr_performing_email')

    response_sender = fields.Many2one('trinity.nomenclature.cl018', string='Изпращач', default=lambda self: self.env['trinity.nomenclature.cl018'].search([('key', '=', '1')], limit=1))
    response_senderId = fields.Char(string='Sender ID')
    response_recipient = fields.Many2one('trinity.nomenclature.cl018', string='Получател', default=lambda self: self.env['trinity.nomenclature.cl018'].search([('key', '=', '4')], limit=1))
    response_recipientId = fields.Char(string='Recipient ID')
    response_messageId = fields.Char(string='ID на съобщението')
    response_messageType = fields.Char(string='Тип на съобщението')
    response_createdOn = fields.Date(string='Създадено на')

    response_nrnReferral = fields.Char(string='НРН направление')
    response_lrn = fields.Char(string='LRN')
    response_status = fields.Many2one('trinity.nomenclature.cl003', string='Статус', default=lambda self: self.env['trinity.nomenclature.cl003'].search([('key', '=', '0')], limit=1))

    warnings_code = fields.Char(string='Код')
    warnings_description = fields.Char(string='Описание')
    warnings_source = fields.Char(string='Източник')
    warnings_nrnTarget = fields.Char(string='НРН целево предупреждение')

    R001 = fields.Text(string='R001', copy=False)
    R001_signed = fields.Char(string='R001 подписан текст', default='not signed', copy=False)
    SignedInfo_R001 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_R001_signature = fields.Char(string="SignedInfo signature", copy=False)

    R007 = fields.Text(string='R007', copy=False)
    R007_signed = fields.Char(string='R007 Signed Text', default='not signed', copy=False)
    SignedInfo_R007 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_R007_signature = fields.Char(string="SignedInfo signature", copy=False)

    R002 = fields.Text(string='R002', copy=False)
    R008 = fields.Text(string='R008', copy=False)

    cancelReason = fields.Char(string='Причина за анулирането', default='Пациентът няма нужда от направлението')

    @api.onchange('referral_main_dr_performing_doctor_id', 'referral_lrn', 'referral_category', 'referral_type', 'referral_rhifAreaNumber', 'referral_basedOn_lrn', 'referral_financingSource', 'diagnosis_code', 'hospitalization_admissionType', 'hospitalization_directedBy', 'hospitalization_clinicalPathway', 'hospitalization_outpatientProcedure', 'laboratory_code_root', 'referral_qualification', 'referral_qualification_nhif', 'medicalExpertise_examType', 'workIncapacity_reason', 'workIncapacity_addressType', 'workIncapacity_isHomeVisitNecessary', 'employer_country', 'employer_city', 'employer_line', 'employer_postalCode', 'attached_documents_type', 'attached_documents_date', 'attached_documents_number', 'attached_documents_isNrn', 'referral_qualification', 'referral_qualification_nhif', 'referral_qualification', 'referral_qualification_nhif', 'specializedActivities_code_root', 'subject_identifierType', 'subject_identifier', 'subject_birthDate', 'subject_gender', 'subject_given', 'subject_middle', 'subject_family', 'subject_country', 'subject_county', 'subject_ekatte', 'subject_city', 'requester_pmi', 'requester_qualification', 'requester_qualification_nhif', 'requester_role', 'requester_practiceNumber', 'requester_rhifAreaNumber', 'response_sender', 'response_recipient', 'comorbidity_use', 'requester_pmiDeputy')
    def compute_R001(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            R001 = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-R001.xsd">
                <nhis:header>
                    <nhis:sender value="{self.response_sender.key if self.response_sender else '1'}"/>
                    <nhis:senderId value="{self.referral_main_dr_performing_doctor_id.doctor_id if self.referral_main_dr_performing_doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="{self.response_recipient.key if self.response_recipient else '4'}"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="R001"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:referral>
                        <nhis:lrn value="{self.referral_lrn if self.referral_lrn else ''}"/>
                        <nhis:authoredOn value="{current_datetime.strftime('%Y-%m-%d')}"/>
                        <nhis:category value="{self.referral_category.key if self.referral_category else ''}"/>"""

            if record.referral_category and record.referral_category.key in ['R1', 'R2', 'R3']:
                R001 += f"""
                        <nhis:type value="{self.referral_type.key if self.referral_type else ''}"/>"""

            R001 += f"""
                    <nhis:rhifAreaNumber value="{self.referral_rhifAreaNumber.key if self.referral_rhifAreaNumber else '2201'}"/>
                    <nhis:basedOn value="{self.referral_basedOn_nrn if self.referral_basedOn_nrn else ''}"/>
                    <nhis:financingSource value="{self.referral_financingSource.key if self.referral_financingSource else ''}"/>
                    <nhis:diagnosis>
                        <nhis:code value="{self.diagnosis_code.key if self.diagnosis_code else ''}"/>
                        <nhis:use value="{self.diagnosis_use.key if self.diagnosis_use else '3'}"/>
                        <nhis:rank value="{self.diagnosis_rank.key if self.diagnosis_rank else '1'}"/>
                    </nhis:diagnosis>"""

            if record.referral_category and record.referral_category.key == 'R1':
                R001 += f"""
                        <nhis:laboratory>
                            <nhis:code value="{self.laboratory_code_root.key.upper() if self.laboratory_code_root else ''}"/>
                        </nhis:laboratory>"""

            if record.referral_category and record.referral_category.key == 'R2':
                R001 += f"""
                        <nhis:consultation>
                            <nhis:qualification value="{self.referral_qualification.key if self.referral_qualification else ''}" nhifCode="{self.referral_qualification_nhif if self.referral_qualification_nhif else ''}"/>
                        </nhis:consultation>"""

            if record.referral_category and record.referral_category.key == 'R3':
                R001 += f"""
                        <nhis:specializedActivities>
                            <nhis:qualification value="{self.referral_qualification.key if self.referral_qualification else ''}" nhifCode="{self.referral_qualification_nhif if self.referral_qualification_nhif else ''}"/>
                            <nhis:code value="{self.specializedActivities_code_root.key if self.specializedActivities_code_root else ''}"/>
                        </nhis:specializedActivities>"""

            if record.referral_category and record.referral_category.key == 'R4':
                R001 += f"""
                        <nhis:hospitalization>
                            <nhis:admissionType value="{self.hospitalization_admissionType.key if self.hospitalization_admissionType else ''}"/>
                            <nhis:directedBy value="{self.hospitalization_directedBy.key if self.hospitalization_directedBy else ''}"/>
                            <nhis:clinicalPathway value="{self.hospitalization_clinicalPathway.key if self.hospitalization_clinicalPathway else ''}"/>
                            <nhis:outpatientProcedure value="{self.hospitalization_outpatientProcedure.key if self.hospitalization_outpatientProcedure else ''}"/>
                        </nhis:hospitalization>"""

            if record.referral_category and record.referral_category.key == 'R5':
                R001 += f"""
                        <nhis:medicalExpertise>
                            <nhis:qualification value="{self.referral_qualification.key if self.referral_qualification else ''}" nhifCode="{self.referral_qualification_nhif if self.referral_qualification_nhif else ''}"/>
                            <nhis:examType value="{self.medicalExpertise_examType.key if self.medicalExpertise_examType else ''}"/>
                        </nhis:medicalExpertise>"""

            if record.referral_category and record.referral_category.key == 'R8':
                R001 += f"""
                        <nhis:workIncapacity>
                            <nhis:reason value="{self.workIncapacity_reason.key if self.workIncapacity_reason else ''}"/>
                            <nhis:addressType value="{self.workIncapacity_addressType.key if self.workIncapacity_addressType else ''}"/>
                            <nhis:isHomeVisitNecessary value="{self.workIncapacity_isHomeVisitNecessary if self.workIncapacity_isHomeVisitNecessary else 'false'}"/>
                            <nhis:employer>
                                <nhis:name value="{self.employer_name if self.employer_name else ''}"/>
                                <nhis:identificationCode value="{self.employer_identificationCode if self.employer_identificationCode else ''}"/>
                                <nhis:phone value="{self.employer_phone if self.employer_phone else ''}"/>
                                <nhis:email value="{self.employer_email if self.employer_email else ''}"/>
                                <nhis:address>
                                    <nhis:country value="{self.employer_country.key if self.employer_country else ''}"/>
                                    <nhis:county value="{self.employer_county.key if self.employer_county else ''}"/>
                                    <nhis:ekatte value="{self.employer_ekatte.key if self.employer_ekatte else ''}"/>
                                    <nhis:city value="{self.employer_city if self.employer_city else ''}"/>
                                    <nhis:line value="{self.employer_line if self.employer_line else ''}"/>
                                    <nhis:postalCode value="{self.employer_postalCode if self.employer_postalCode else ''}"/>
                                </nhis:address>
                            </nhis:employer>
                            <nhis:documents>
                                <nhis:type value="{self.attached_documents_type.key if self.attached_documents_type else ''}"/>
                                <nhis:date value="{self.attached_documents_date.strftime('%Y-%m-%d') if self.attached_documents_date else ''}"/>
                                <nhis:number value="{self.attached_documents_number if self.attached_documents_number else ''}"/>
                                <nhis:isNrn value="{self.attached_documents_isNrn if self.attached_documents_isNrn else ''}"/>
                                <nhis:note value="{self.attached_documents_note if self.attached_documents_note else ''}"/>
                            </nhis:documents>
                        </nhis:workIncapacity>"""

            R001 += f"""
                    </nhis:referral>
                    <nhis:subject>
                        <nhis:identifierType value="{self.subject_identifierType.key if self.subject_identifierType else ''}"/>
                        <nhis:identifier value="{self.subject_identifier.identifier if self.subject_identifier else ''}"/>
                        <nhis:birthDate value="{self.subject_birthDate.strftime('%Y-%m-%d') if self.subject_birthDate else ''}"/>
                        <nhis:gender value="{self.subject_gender.key if self.subject_gender else ''}"/>
                        <nhis:name>
                            <nhis:given value="{self.subject_given if self.subject_given else ''}"/>
                            <nhis:middle value="{self.subject_middle if self.subject_middle else ''}"/>
                            <nhis:family value="{self.subject_family if self.subject_family else ''}"/>
                        </nhis:name>
                        <nhis:address>
                            <nhis:country value="{self.subject_country.key if self.subject_country else 'BG'}"/>
                            <nhis:county value="{self.subject_county.key if self.subject_county else 'SOF'}"/>
                            <nhis:ekatte value="{self.subject_ekatte.key if self.subject_ekatte else '68134'}"/>
                            <nhis:city value="{self.subject_city if self.subject_city else 'София'}"/>
                        </nhis:address>
                    </nhis:subject>
                    <nhis:requester>
                        <nhis:pmi value="{self.requester_pmi.doctor_id if self.requester_pmi else ''}"/>
                        <nhis:qualification value="{self.requester_qualification.key if self.requester_qualification else ''}" nhifCode="{self.requester_qualification_nhif if self.requester_qualification_nhif else ''}"/>
                        <nhis:role value="{self.requester_role.key if self.requester_role else ''}"/>
                        <nhis:practiceNumber value="{self.requester_practiceNumber if self.requester_practiceNumber else ''}"/>
                        <nhis:phone value="{self.requester_phone if self.requester_phone else '0035924215555'}"/>
                        <nhis:rhifAreaNumber value="{self.requester_rhifAreaNumber.key if self.requester_rhifAreaNumber else '2201'}"/>
                    </nhis:requester>
                </nhis:contents>
            </nhis:message>"""

            R001 = R001.replace("False", "false").replace("True", "true")
            self.R001 = R001
            self.sign_R001()

    @api.onchange('response_nrnReferral', 'response_sender', 'response_recipient', 'comorbidity_use', 'requester_pmiDeputy')
    def compute_R007(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            R007 = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-R007.xsd">
                <nhis:header>
                    <nhis:sender value="{self.response_sender.key if self.response_sender else '1'}"/>
                    <nhis:senderId value="{self.referral_main_dr_performing_doctor_id.doctor_id if self.referral_main_dr_performing_doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="{self.response_recipient.key if self.response_recipient else '4'}"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="R007"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:nrnReferral value="{self.response_nrnReferral if self.response_nrnReferral else ''}"/>
                    <nhis:cancelReason value="{self.cancelReason if self.cancelReason else ''}"/>
                </nhis:contents>
            </nhis:message>"""

            R007 = R007.replace("False", "false").replace("True", "true")
            self.R007 = R007
            self.sign_R007()

    def getSignatureR001(self):
        return

    def getSignatureR007(self):
        return

    def sign_R001(self, field_name='R001', signedinfo='SignedInfo_R001', is_signed='R001_signed', signedinfo_signature='SignedInfo_R001_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def sign_R007(self, field_name='R007', signedinfo='SignedInfo_R007', is_signed='R007_signed', signedinfo_signature='SignedInfo_R007_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_R001(self):
        return self.download_file('R001')

    def action_download_R007(self):
        return self.download_file('R007')

    def download_file(self, field_name):
        file_content = base64.b64decode(getattr(self, field_name))
        file_name = f'referral_{self.referral_lrn}_@_{self._fields[field_name].string}.xml'
        if not file_name.endswith('.xml'):
            file_name += '.xml'
        encoded_content = base64.b64encode(file_content)
        file_path = f'/web/content/{self._name}/{self.id}/{field_name}/{file_name}?download=true'
        download_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + file_path
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'self',
        }

    def R001_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'R001_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    def R007_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'R007_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    def check_response(self, response, field_response, request_msg_type=None):
        try:
            xml_root = ET.fromstring(response.text)
        except ET.ParseError:
            if "401 Authorization Required" in response.text:
                raise UserError("НАПРАВЕТЕ ВРЪЗКА С НЗИС!")
            return
        ns = {'nhis': 'https://www.his.bg'}
        nrnReferral = xml_root.find('.//nhis:nrnReferral', ns)
        status = xml_root.find('.//nhis:status', ns)
        error_reason = xml_root.find('.//nhis:reason', ns)
        if nrnReferral is not None and 'value' in nrnReferral.attrib:
            self.response_nrnReferral = nrnReferral.attrib['value']
        if status is not None and 'value' in status.attrib:
            status_value = status.attrib['value']
            status_record = self.env['trinity.nomenclature.cl003'].search([('key', '=', status_value)], limit=1)
            if status_record:
                self.response_status = status_record.id
            else:
                _logger.warning(f"Status value '{status_value}' not found in trinity.nomenclature.cl003")
        self.compute_R007()
        if error_reason is not None and 'value' in error_reason.attrib:
            error_message = error_reason.attrib['value']
            raise UserError(error_message)

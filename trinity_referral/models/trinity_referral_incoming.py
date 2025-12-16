import datetime
import logging
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class TrinityReferralIncoming(models.Model):
    _name = 'trinity.referral.incoming'
    _description = 'Trinity Referral Incoming'
    _inherit = ["trinity.library.user.company.fields"]

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)

    R016 = fields.Text(string='R016')

    examination_type_id = fields.Many2one('trinity.examination.type', string='Създай тип преглед', default=lambda self: self.env['trinity.examination.type'].search([('name', '=', 'НЗОК - Първичен преглед - 11-022')], limit=1))

    fetch_referral_id = fields.Many2one('trinity.referral.fetch', string='Изтегляне')

    referral_authoredOn = fields.Date(string='Дата на издаване')
    referral_category = fields.Many2one('trinity.nomenclature.cl014', string='Вид направление')
    referral_category_name = fields.Char(related='referral_category.name', string='Вид направление')
    referral_type = fields.Many2one('trinity.nomenclature.cl021', string='Причина за издаване')
    referral_basedOn_lrn = fields.Char(string='Основано на Амб. №')
    referral_basedOn_nrn = fields.Char(string='Основано на НРН')
    referral_financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Финансиране')
    referral_rhifAreaNumber = fields.Many2one('trinity.nomenclature.cl029', string='РЗИ №')
    referral_main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors.external', string='УИН')

    laboratory_code = fields.Many2one('trinity.nomenclature.cl022', string='МД')

    referral_qualification = fields.Many2one('trinity.nomenclature.cl006', string='Код')
    referral_qualification_name = fields.Char(related='referral_qualification.name', string='Специалност')
    referral_qualification_nhif = fields.Char(related='referral_qualification.meta_nhif_code', string='Код по НЗОК')

    specializedActivities_code = fields.Many2one('trinity.nomenclature.cl050', string='ВС')

    hospitalization_admissionType = fields.Many2one('trinity.nomenclature.cl059', string='Тип на прием')
    hospitalization_directedBy = fields.Many2one('trinity.nomenclature.cl060', string='Насочено от')
    hospitalization_clinicalPathway = fields.Many2one('trinity.nomenclature.cl062', string='КП')
    hospitalization_outpatientProcedure = fields.Many2one('trinity.nomenclature.cl063', string='Амбулаторни процедури')

    medicalExpertise_examType = fields.Many2one('trinity.nomenclature.cl051', string='За вид изследване')

    workIncapacity_reason = fields.Many2one('trinity.nomenclature.cl052', string='Причина')
    workIncapacity_addressType = fields.Many2one('trinity.nomenclature.cl053', string='Тип адрес')
    workIncapacity_isHomeVisitNecessary = fields.Boolean(string='Необходимо ли е домашно посещение')

    employer_name = fields.Char(string='Име')
    employer_identificationCode = fields.Char(string='Идентификационен код')
    employer_position = fields.Char(string='Длъжност')
    employer_phone = fields.Char(string='Телефон')
    employer_email = fields.Char(string='Ел. поща')
    employer_country = fields.Many2one('trinity.nomenclature.cl005', string='Държава')
    employer_county = fields.Many2one('trinity.nomenclature.cl041', string='Област')
    employer_ekatte = fields.Many2one('trinity.nomenclature.cl044', string='ЕКАТТЕ')
    employer_city = fields.Char(string='Град')
    employer_line = fields.Char(string='Адрес')
    employer_postalCode = fields.Char(string='Пощенски код')

    attached_documents_type = fields.Many2one('trinity.nomenclature.cl102', string='Тип статус')
    attached_documents_date = fields.Date(string='Дата')
    attached_documents_number = fields.Char(string='Номер')
    attached_documents_isNrn = fields.Char(string='Е НРН')
    attached_documents_note = fields.Char(string='Бележка')

    diagnosis_code = fields.Many2one('trinity.nomenclature.cl011', string='МКБ')
    diagnosis_additionalCode = fields.Many2one('trinity.nomenclature.cl011', string='Допълнителен МКБ')
    diagnosis_use = fields.Many2one('trinity.nomenclature.cl076', string='Употреба')
    diagnosis_rank = fields.Char(string='Ранг')
    diagnosis_clinicalStatus = fields.Many2one('trinity.nomenclature.cl077', string='Клинично състояние')
    diagnosis_verificationStatus = fields.Many2one('trinity.nomenclature.cl078', string='Статус на верификация')
    diagnosis_onsetDateTime = fields.Datetime(string='Дата и час на началото')
    diagnosis_note = fields.Text(string='Бележка')

    comorbidity_code = fields.Many2one('trinity.nomenclature.cl011', string='МКБ на съпътстващо заболяване')
    comorbidity_additionalCode = fields.Many2one('trinity.nomenclature.cl011', string='Допълнителен МКБ')
    comorbidity_use = fields.Many2one('trinity.nomenclature.cl076', string='Употреба')
    comorbidity_rank = fields.Char(string='Ранг')
    comorbidity_clinicalStatus = fields.Many2one('trinity.nomenclature.cl077', string='Клинично състояние')
    comorbidity_verificationStatus = fields.Many2one('trinity.nomenclature.cl078', string='Статус на верификация')
    comorbidity_onsetDateTime = fields.Datetime(string='Дата и час на началото')
    comorbidity_note = fields.Char(string='Бележка')

    subject_identifierType = fields.Many2one('trinity.nomenclature.cl004', string='Тип на идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    subject_identifier = fields.Char(string='ЕГН/ЛНЧ/друг №')
    subject_birthDate = fields.Date(string='Дата на раждане')
    subject_gender = fields.Many2one('trinity.nomenclature.cl001', string='Пол')
    subject_given = fields.Char(string='Име')
    subject_middle = fields.Char(string='Презиме')
    subject_family = fields.Char(string='Фамилия')
    subject_full_name = fields.Char(string='Направление издадено за', compute='compute_subject_full_name')

    @api.depends('subject_given', 'subject_family')
    def compute_subject_full_name(self):
        for record in self:
            record.subject_full_name = f"{record.subject_given} {record.subject_family}, ЕГН/ЛНЧ: {record.subject_identifier}, пол: {record.subject_gender.description}, гражданство: {record.subject_nationality.description}"

    subject_phone = fields.Char(string='Телефон')
    subject_country = fields.Many2one('trinity.nomenclature.cl005', string='Държава')
    subject_county = fields.Many2one('trinity.nomenclature.cl041', string='Област')
    subject_ekatte = fields.Many2one('trinity.nomenclature.cl044', string='ЕКАТТЕ')
    subject_nationality = fields.Many2one('trinity.nomenclature.cl005', string='Националност')
    subject_city = fields.Char(string='Град')
    subject_postalCode = fields.Char(string='Пощенски код')
    subject_nhifInsuranceNumber = fields.Char(string='Номер на застраховка НЗОК')
    subject_identificationDocument_number = fields.Char(string='Номер на документа')
    subject_identificationDocument_issueDate = fields.Date(string='Дата на издаване')
    subject_identificationDocument_issuer = fields.Char(string='Издател')
    subject_identificationDocument_nationality = fields.Many2one('trinity.nomenclature.cl005', string='Националност')
    subject_identificationDocument_phone = fields.Char(string='Телефон')
    subject_identificationDocument_email = fields.Char(string='Ел. поща')
    subject_age = fields.Char(string='Възраст')
    subject_weight = fields.Char(string='Тегло')
    subject_maritalStatus = fields.Many2one('trinity.nomenclature.cl064', string='Семеен статус')
    subject_education = fields.Many2one('trinity.nomenclature.cl065', string='Образование')
    subject_workplace = fields.Text(string='Място на работа')
    subject_profession = fields.Char(string='Професия')

    requester_pmi = fields.Char(string='УИН')
    requester_full_name = fields.Char(string='Изпращащ', compute='compute_requester_full_name')

    @api.depends('requester_given', 'requester_family')
    def compute_requester_full_name(self):
        for record in self:
            record.requester_full_name = f"д-р {record.requester_given or ''} {record.requester_family or ''}, УИН: {record.requester_pmi or ''}".strip()

    requester_pmiDeputy = fields.Char(string='УИН на заместник')
    requester_qualification_nhif = fields.Char(string='Код на НЗОК')
    requester_qualification = fields.Many2one('trinity.nomenclature.cl006', string='Код')
    requester_qualification_name = fields.Char(related='requester_qualification.name', string='Специалност')
    requester_role = fields.Many2one('trinity.nomenclature.cl023', string='Роля на изпълнителя')
    requester_practiceNumber = fields.Char(string='Номер на практика')
    requester_rhifAreaNumber = fields.Many2one('trinity.nomenclature.cl029', string='Номер на РЗОК област')
    requester_nhifNumber = fields.Char(string='Номер на НЗОК')
    requester_phone = fields.Char(string='Телефон')
    requester_given = fields.Char(string='Име')
    requester_family = fields.Char(string='Фамилия')

    response_sender = fields.Char(string='Изпращач')
    response_senderId = fields.Char(string='ID на изпращача')
    response_recipient = fields.Char(string='Получател')
    response_recipientId = fields.Char(string='ID на получателя')
    response_messageId = fields.Char(string='ID на съобщението')
    response_messageType = fields.Char(string='Тип на съобщението')
    response_createdOn = fields.Date(string='Създадено на')
    response_nrnReferral = fields.Char(string='Направление НРН')
    response_lrnReferral = fields.Char(string='LRN')
    response_status = fields.Many2one('trinity.nomenclature.cl003', string='Статус')

    warnings_code = fields.Char(string='Код')
    warnings_description = fields.Char(string='Описание')
    warnings_source = fields.Char(string='Източник')
    warnings_nrnTarget = fields.Char(string='Целеви НРН')

    @api.depends('R016')
    def parse_xml_and_set_fields(self):
        if not self.R016:
            return

        try:
            root = ET.fromstring(self.R016)
            ns = {'nhis': 'https://www.his.bg'}

            def get_val(node, attr='value'):
                return node.get(attr) if node is not None else None

            for field_name, xpath in [
                ('response_sender', './/nhis:sender'),
                ('response_senderId', './/nhis:senderId'),
                ('response_recipient', './/nhis:recipient'),
                ('response_recipientId', './/nhis:recipientId'),
                ('response_messageId', './/nhis:messageId'),
                ('response_messageType', './/nhis:messageType'),
                ('response_createdOn', './/nhis:createdOn'),
            ]:
                setattr(self, field_name, get_val(root.find(xpath, ns)))

            referral = root.find('.//nhis:referral', ns)
            if referral: self._parse_referral(referral, ns)

            subject = root.find('.//nhis:subject', ns)
            if subject: self._parse_subject(subject, ns)

            requester = root.find('.//nhis:requester', ns)
            if requester: self._parse_requester(requester, ns)

        except ET.ParseError as e:
            _logger.error(f"XML parse error for record {self.id}: {e}")

    def _parse_referral(self, referral, ns):
        def search_model(model, key):
            return self.env[model].search([('key', '=', key)], limit=1).id if key else None

        def get_value(path):
            node = referral.find(path, ns)
            return node.get('value') if node is not None else None

        def get_val(node):
            return node.get('value') if node is not None else None

        self.response_nrnReferral = get_value('./nhis:nrnReferral')
        self.response_lrnReferral = get_value('./nhis:lrn')
        self.referral_authoredOn = get_value('./nhis:authoredOn')
        self.referral_category = search_model('trinity.nomenclature.cl014', get_value('./nhis:category'))
        self.referral_type = search_model('trinity.nomenclature.cl021', get_value('./nhis:type'))
        self.referral_rhifAreaNumber = search_model('trinity.nomenclature.cl029', get_value('./nhis:rhifAreaNumber'))
        self.referral_basedOn_nrn = get_value('./nhis:basedOn')
        self.referral_financingSource = search_model('trinity.nomenclature.cl069', get_value('./nhis:financingSource'))

        diag_node = referral.find('./nhis:diagnosis', ns)
        if diag_node:
            self.diagnosis_code = search_model('trinity.nomenclature.cl011', get_val(diag_node.find('./nhis:code', ns)))
            self.diagnosis_use = search_model('trinity.nomenclature.cl076', get_val(diag_node.find('./nhis:use', ns)))
            self.diagnosis_rank = get_val(diag_node.find('./nhis:rank', ns))
            self.diagnosis_additionalCode = search_model('trinity.nomenclature.cl011', get_val(diag_node.find('./nhis:additionalCode', ns)))

        comorbidity_node = referral.find('./nhis:comorbidity', ns)
        if comorbidity_node:
            self.comorbidity_code = search_model('trinity.nomenclature.cl011', get_val(comorbidity_node.find('./nhis:code', ns)))
            self.comorbidity_use = search_model('trinity.nomenclature.cl076', get_val(comorbidity_node.find('./nhis:use', ns)))
            self.comorbidity_rank = get_val(comorbidity_node.find('./nhis:rank', ns))
            self.comorbidity_additionalCode = search_model('trinity.nomenclature.cl011', get_val(comorbidity_node.find('./nhis:additionalCode', ns)))

        self.referral_qualification = self._parse_qualification(referral.find('./nhis:consultation/nhis:qualification', ns)) or self._parse_qualification(referral.find('./nhis:specializedActivities/nhis:qualification', ns)) or self._parse_qualification(referral.find('./nhis:medicalExpertise/nhis:qualification', ns))

        self.specializedActivities_code = search_model('trinity.nomenclature.cl050', get_val(referral.find('./nhis:specializedActivities/nhis:code', ns)))

        self.medicalExpertise_examType = search_model('trinity.nomenclature.cl051', get_val(referral.find('./nhis:medicalExpertise/nhis:examType', ns)))

        self.workIncapacity_reason = search_model('trinity.nomenclature.cl052', get_val(referral.find('./nhis:workIncapacity/nhis:reason', ns)))

        self.laboratory_code = search_model('trinity.nomenclature.cl022', get_val(referral.find('./nhis:laboratory/nhis:code', ns)))

        hosp_node = referral.find('./nhis:hospitalization', ns)
        if hosp_node:
            self.hospitalization_admissionType = search_model('trinity.nomenclature.cl059', get_val(hosp_node.find('./nhis:admissionType', ns)))
            self.hospitalization_directedBy = search_model('trinity.nomenclature.cl060', get_val(hosp_node.find('./nhis:directedBy', ns)))
            self.hospitalization_clinicalPathway = search_model('trinity.nomenclature.cl062', get_val(hosp_node.find('./nhis:clinicalPathway', ns)))
            self.hospitalization_outpatientProcedure = search_model('trinity.nomenclature.cl063', get_val(hosp_node.find('./nhis:outpatientProcedure', ns)))

    def _parse_subject(self, subject, ns):
        def search_model(model, key):
            return self.env[model].search([('key', '=', key)], limit=1).id if key else None

        get_val = lambda node: node.get('value') if node is not None else None

        self.subject_identifierType = search_model('trinity.nomenclature.cl004', get_val(subject.find('./nhis:identifierType', ns)))
        self.subject_identifier = get_val(subject.find('./nhis:identifier', ns))
        self.subject_birthDate = get_val(subject.find('./nhis:birthDate', ns))
        self.subject_gender = search_model('trinity.nomenclature.cl001', get_val(subject.find('./nhis:gender', ns)))
        self.subject_nationality = search_model('trinity.nomenclature.cl005', get_val(subject.find('./nhis:nationality', ns)))

        name_node = subject.find('./nhis:name', ns)
        if name_node:
            self.subject_given = get_val(name_node.find('./nhis:given', ns))
            self.subject_middle = get_val(name_node.find('./nhis:middle', ns))
            self.subject_family = get_val(name_node.find('./nhis:family', ns))

        addr_node = subject.find('./nhis:address', ns)
        if addr_node:
            self.subject_country = search_model('trinity.nomenclature.cl005', get_val(addr_node.find('./nhis:country', ns)))
            self.subject_county = search_model('trinity.nomenclature.cl041', get_val(addr_node.find('./nhis:county', ns)))
            self.subject_ekatte = search_model('trinity.nomenclature.cl044', get_val(addr_node.find('./nhis:ekatte', ns)))
            self.subject_city = get_val(addr_node.find('./nhis:city', ns))

    def _parse_requester(self, requester, ns):
        def search_qualification(node):
            if node is None: return None, None
            value = node.get('value')
            rec = self.env['trinity.nomenclature.cl006'].search([('key', '=', value)], limit=1)
            if rec:
                return rec.id, getattr(rec, 'meta_nhif_code', None)
            return value, node.get('nhifCode')

        def search_model(model, key):
            return self.env[model].search([('key', '=', key)], limit=1).id if key else None

        get_val = lambda node: node.get('value') if node is not None else None
        self.requester_pmi = get_val(requester.find('./nhis:pmi', ns))
        qual_node = requester.find('./nhis:qualification', ns)
        self.requester_qualification, self.requester_qualification_nhif = search_qualification(qual_node)
        self.requester_role = search_model('trinity.nomenclature.cl023', get_val(requester.find('./nhis:role', ns)))
        self.requester_practiceNumber = get_val(requester.find('./nhis:practiceNumber', ns))
        self.requester_rhifAreaNumber = search_model('trinity.nomenclature.cl029', get_val(requester.find('./nhis:rhifAreaNumber', ns)))
        self.requester_phone = get_val(requester.find('./nhis:phone', ns))
        name_node = requester.find('./nhis:name', ns)
        if name_node:
            self.requester_given = get_val(name_node.find('./nhis:given', ns))
            self.requester_family = get_val(name_node.find('./nhis:family', ns))

        self.update_or_create_external_doctor()
        self.create_or_update_patient_record()

    def _parse_qualification(self, node, return_nhif=False):
        if node is None: return (None, None) if return_nhif else None
        value = node.get('value')
        rec = self.env['trinity.nomenclature.cl006'].search([('key', '=', value)], limit=1)
        if rec:
            return (rec.id, getattr(rec, 'meta_nhif_code', None)) if return_nhif else rec.id
        return (value, node.get('nhifCode')) if return_nhif else value

    def update_or_create_external_doctor(self):
        doctor_external_model = self.env['trinity.medical.facility.doctors.external']
        qualification = self.requester_qualification
        nhif_code = getattr(self, 'requester_nhifCode', False)

        nomenclature_model = self.env['trinity.nomenclature.cl004']
        domain = [('key', '=', qualification)]
        if nhif_code:
            domain.append(('nhif_code', '=', nhif_code))

        qualification_record = nomenclature_model.search(domain, limit=1)

        if not qualification_record:
            _logger.warning(
                f"No qualification found for key {qualification} and nhifCode {nhif_code} in nomenclature table"
            )

        vals = {
            'doctor_id': self.requester_pmi,
            'first_name': self.requester_given,
            'last_name': self.requester_family,
            'hospital_no': self.requester_practiceNumber,
            'phone': self.requester_phone,
            'qualification_code': qualification_record.id if qualification_record else False,
            'rhifAreaNumber': self.requester_rhifAreaNumber,
            'nhifNumber': self.requester_nhifNumber,
        }

        doctor = doctor_external_model.search([('doctor_id', '=', self.requester_pmi)], limit=1)
        if doctor:
            try:
                doctor.write(vals)
                _logger.info(f"Updated doctor record for PMI: {self.requester_pmi}")
            except Exception as e:
                _logger.error(f"Failed to update doctor record for PMI {self.requester_pmi}: {str(e)}")
        else:
            try:
                doctor_external_model.create(vals)
                _logger.info(f"Created new doctor record for PMI: {self.requester_pmi}")
            except Exception as e:
                _logger.error(f"Failed to create doctor record for PMI {self.requester_pmi}: {str(e)}")

    def create_or_update_patient_record(self):
        try:
            default_identifier_type = self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1)
            default_nationality = self.env['trinity.nomenclature.cl005'].search([('key', '=', 'BG')], limit=1)
            default_country = self.env['trinity.nomenclature.cl005'].search([('key', '=', 'BG')], limit=1)
            default_county = self.env['trinity.nomenclature.cl041'].search([('key', '=', 'SOF')], limit=1)
            default_ekatte = self.env['trinity.nomenclature.cl044'].search([('key', '=', '68134')], limit=1)

            patient_vals = {
                'identifier': self.subject_identifier,
                'identifier_type': self.subject_identifierType.id if self.subject_identifierType else (default_identifier_type.id if default_identifier_type else False),
                'birth_date': self.subject_birthDate,
                'gender': self.subject_gender.id if self.subject_gender else None,
                'nationality': self.subject_nationality.id if self.subject_nationality else (default_nationality.id if default_nationality else False),
                'first_name': self.subject_given,
                'middle_name': self.subject_middle,
                'last_name': self.subject_family,
                'country_bulgarian': self.subject_country.id if self.subject_country else (default_country.id if default_country else False),
                'county_bulgarian': self.subject_county.id if self.subject_county else (default_county.id if default_county else False),
                'ekatte_key': self.subject_ekatte.id if self.subject_ekatte else (default_ekatte.id if default_ekatte else False),
                'city': self.subject_city or 'София',
            }

            try:
                general_practitioner = self.env['trinity.medical.facility.doctors.external'].search([('doctor_id', '=', self.requester_pmi)], limit=1)
                patient_vals['general_practitioner_id'] = general_practitioner.id if general_practitioner else False
            except Exception as e:
                _logger.warning(f"Could not find general practitioner for PMI {self.requester_pmi}: {str(e)}")
                patient_vals['general_practitioner_id'] = False

            patient_model = self.env['trinity.patient']
            existing = patient_model.search([('identifier', '=', self.subject_identifier)], limit=1)

            if existing:
                try:
                    existing.write(patient_vals)
                    existing.create_nzok_insurance_record()
                    _logger.info(f"Successfully updated patient record for identifier: {self.subject_identifier}")
                except Exception as e:
                    _logger.error(f"Failed to update patient record for identifier {self.subject_identifier}: {str(e)}")
                    # Try to create insurance record even if update failed
                    try:
                        existing.create_nzok_insurance_record()
                    except Exception as insurance_e:
                        _logger.warning(f"Failed to create insurance record for existing patient {self.subject_identifier}: {str(insurance_e)}")
            else:
                try:
                    new_patient = patient_model.create(patient_vals)
                    new_patient.create_nzok_insurance_record()
                    _logger.info(f"Successfully created new patient record for identifier: {self.subject_identifier}")
                except Exception as e:
                    _logger.error(f"Failed to create patient record for identifier {self.subject_identifier}: {str(e)}")
                    # Try to create insurance record even if patient creation failed
                    try:
                        new_patient.create_nzok_insurance_record()
                    except Exception as insurance_e:
                        _logger.warning(f"Failed to create insurance record for new patient {self.subject_identifier}: {str(insurance_e)}")

        except Exception as e:
            _logger.error(f"Unexpected error in create_or_update_patient_record for identifier {getattr(self, 'subject_identifier', 'unknown')}: {str(e)}", exc_info=True)

    def create_trinity_examination_record(self):

        patient = self.env['trinity.patient'].search([('identifier', '=', self.subject_identifier)], limit=1)
        if not patient:
            return

        existing_examination = self.env['trinity.examination'].search([
            ('basedOn_e_examination_nrn', '=', self.response_nrnReferral)
        ], limit=1)
        if existing_examination:
            raise UserError(_('ВЕЧЕ СЪЩЕСТВУВА ПРЕГЛЕД ОСНОВАН НА ТОВА НАПРАВЛЕНИЕ!'))

        doctor = self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1)
        if not doctor or not doctor.qualification_code:
            raise UserError(_('НЕ Е НАМЕРЕН ЛЕКАР ИЛИ КВАЛИФИКАЦИЯ ЗА ТОЗИ ПОТРЕБИТЕЛ!'))

        doctor_qual_key = doctor.qualification_code.key if doctor.qualification_code else None
        if not doctor_qual_key:
            raise UserError(_('НЕ Е НАМЕРЕН ЛЕКАР ИЛИ КВАЛИФИКАЦИЯ ЗА ТОЗИ ПОТРЕБИТЕЛ!'))

        qualification_matches = False
        if self.referral_qualification and self.referral_qualification.key == doctor_qual_key:
            qualification_matches = True

        if not qualification_matches:
            raise UserError(_('ИЗПОЛЗВАТЕ НАПРАВЛЕНИЕ ЗА ДРУГА СПЕЦИАЛНОСТ!'))

        if self.referral_authoredOn < fields.Date.today() - timedelta(days=30):
            raise UserError(_('ИЗПОЛЗВАТЕ НАПРАВЛЕНИЕ ПО СТАРО ОТ 30 ДНИ!'))

        domain = []
        if self.diagnosis_code: domain.append(('id', '=', self.diagnosis_code))
        if self.diagnosis_additionalCode: domain = ['|'] + domain + [('id', '=', self.diagnosis_additionalCode)]
        icd_records = self.env['trinity.nomenclature.cl011'].search(domain) if domain else self.env['trinity.nomenclature.cl011']
        icd_ids = icd_records.ids

        report_vals = {
            'patient_identifier_id': patient.id,
            'basedOn_e_examination_nrn': self.response_nrnReferral,
            'basedOn_e_examination_nrn_date': self.referral_authoredOn,
            'basedOn_e_examination_nrn_sentbyDoctorId': self.requester_pmi,
            'basedOn_e_examination_nrn_sentbyPractice': self.requester_practiceNumber,
            'basedOn_e_examination_nrn_sentbyDoctor_qualification_code': self.requester_qualification_nhif,
            'examination_type_id': self.examination_type_id.id,
            'financingSource': self.referral_financingSource or '2',
            'icd_code': icd_ids[0] if icd_ids else False,
            'icd_codes': [(6, 0, icd_ids)] if icd_ids else False,
        }

        report = self.env['trinity.examination'].create(report_vals)
        report.compute_is_patient_signer_default()

        if report and report.id:
            self.fetch_referral_id.fetch_new_referral()

        return {
            'name': 'Report',
            'type': 'ir.actions.act_window',
            'res_model': 'trinity.examination',
            'view_mode': 'form',
            'target': 'current',
            'res_id': report.id,
        }

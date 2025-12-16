import datetime
import logging
import xml.etree.ElementTree as ET

from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class TrinityHospitalisationIncoming(models.Model):
    _name = 'trinity.hospitalisation.incoming'
    _description = 'Trinity Hospitalisation Incoming'
    _inherit = ["trinity.library.user.company.fields"]

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='Лекар', default=lambda self: self.env['trinity.medical.facility.doctors'].search([('user_id', '=', self.env.user.id)], limit=1).id or False)

    H002 = fields.Text(string='H002')

    fetch_hospitalisation_id = fields.Many2one('trinity.hospitalisation.fetch', string='Изтегляне')

    # Hospitalization fields
    hospitalization_nrnHospitalization = fields.Char(string='НРН хоспитализация')
    hospitalization_lrn = fields.Char(string='LRN')
    hospitalization_status = fields.Many2one('trinity.nomenclature.cl074', string='Статус')
    hospitalization_authoredOn = fields.Date(string='Дата на създаване')
    hospitalization_correctionReason = fields.Text(string='Причини за корекции')
    hospitalization_basedOn = fields.Char(string='НРН направление')
    hospitalization_admissionType = fields.Many2one('trinity.nomenclature.cl059', string='Тип на прием')
    hospitalization_clinicalPathway = fields.Many2one('trinity.nomenclature.cl062', string='КП при прием')
    hospitalization_outpatientProcedure = fields.Many2one('trinity.nomenclature.cl063', string='Амбулаторни процедури при прием')
    hospitalization_dischargeClinicalPathway = fields.Many2one('trinity.nomenclature.cl062', string='КП при изписване')
    hospitalization_dischargeOutpatientProcedure = fields.Many2one('trinity.nomenclature.cl063', string='Амбулаторни процедури при изписване')
    hospitalization_directedBy = fields.Many2one('trinity.nomenclature.cl060', string='Насочено от')
    hospitalization_reasonCode = fields.Many2one('trinity.nomenclature.cl061', string='Причина за хоспитализацията')
    hospitalization_note = fields.Text(string='Бележки')
    hospitalization_journalNumber = fields.Char(string='Номер от журнал')
    hospitalization_practiceNumber = fields.Char(string='Номер на практика')
    hospitalization_admissionDate = fields.Datetime(string='Дата на постъпване')
    hospitalization_elapsedTime = fields.Many2one('trinity.nomenclature.cl067', string='Изминало време')
    hospitalization_severity = fields.Many2one('trinity.nomenclature.cl066', string='Степен на тежест')
    hospitalization_financingSource = fields.Many2one('trinity.nomenclature.cl069', string='Финансиране')
    hospitalization_bloodType = fields.Many2one('trinity.nomenclature.cl070', string='Кръвна група')
    hospitalization_dietPreference = fields.Many2one('trinity.nomenclature.cl079', string='Режим на хранене')
    hospitalization_dischargeDate = fields.Datetime(string='Дата на изписване')
    hospitalization_outcome = fields.Many2one('trinity.nomenclature.cl075', string='Изход')
    hospitalization_dischargeDisposition = fields.Many2one('trinity.nomenclature.cl080', string='Разпореждане след изписване')
    hospitalization_dischargeNote = fields.Text(string='Бележки към изписването')
    hospitalization_daysHospitalized = fields.Integer(string='Дни пролежани')
    hospitalization_deceasedDate = fields.Datetime(string='Дата на смърт')
    hospitalization_autopsyDate = fields.Datetime(string='Дата на аутопсия')
    hospitalization_workability = fields.Many2one('trinity.nomenclature.cl081', string='Работоспособност')

    # Patient fields
    subject_identifierType = fields.Many2one('trinity.nomenclature.cl004', string='Тип на идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    subject_identifier = fields.Char(string='ЕГН/ЛНЧ/друг №')
    subject_birthDate = fields.Date(string='Дата на раждане')
    subject_gender = fields.Many2one('trinity.nomenclature.cl001', string='Пол')
    subject_given = fields.Char(string='Име')
    subject_middle = fields.Char(string='Презиме')
    subject_family = fields.Char(string='Фамилия')
    subject_full_name = fields.Char(string='Пациент', compute='compute_subject_full_name')

    @api.depends('subject_given', 'subject_family')
    def compute_subject_full_name(self):
        for record in self:
            record.subject_full_name = f"{record.subject_given} {record.subject_family}, ЕГН/ЛНЧ: {record.subject_identifier}"

    subject_country = fields.Many2one('trinity.nomenclature.cl005', string='Държава')
    subject_county = fields.Many2one('trinity.nomenclature.cl041', string='Област')
    subject_city = fields.Char(string='Град')
    subject_line = fields.Char(string='Адрес')
    subject_postalCode = fields.Char(string='Пощенски код')
    subject_nationality = fields.Many2one('trinity.nomenclature.cl005', string='Националност')
    subject_phone = fields.Char(string='Телефон')
    subject_email = fields.Char(string='Ел. поща')
    subject_age = fields.Float(string='Възраст')
    subject_weight = fields.Float(string='Тегло')
    subject_maritalStatus = fields.Many2one('trinity.nomenclature.cl064', string='Семеен статус')
    subject_education = fields.Many2one('trinity.nomenclature.cl065', string='Образование')
    subject_workplace = fields.Text(string='Място на работа')
    subject_profession = fields.Char(string='Професия')

    # Response metadata
    response_sender = fields.Char(string='Изпращач')
    response_senderId = fields.Char(string='ID на изпращача')
    response_recipient = fields.Char(string='Получател')
    response_recipientId = fields.Char(string='ID на получателя')
    response_messageId = fields.Char(string='ID на съобщението')
    response_messageType = fields.Char(string='Тип на съобщението')
    response_createdOn = fields.Date(string='Създадено на')
    foundNumber = fields.Integer(string='Намерени бройки')

    @api.depends('H002')
    def parse_xml_and_set_fields(self):
        if not self.H002:
            return

        try:
            root = ET.fromstring(self.H002)
            ns = {'nhis': 'https://www.his.bg'}

            def get_val(node, attr='value'):
                return node.get(attr) if node is not None else None

            # Parse header
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

            # Parse foundNumber
            found_number_node = root.find('.//nhis:foundNumber', ns)
            if found_number_node is not None:
                self.foundNumber = int(found_number_node.get('value', '0'))

            # Parse results/hospitalization
            hospitalization = root.find('.//nhis:hospitalization', ns)
            if hospitalization:
                self._parse_hospitalization(hospitalization, ns)

            # Parse patient
            patient = root.find('.//nhis:subject', ns)
            if patient:
                self._parse_patient(patient, ns)

        except ET.ParseError as e:
            _logger.error(f"XML parse error for record {self.id}: {e}")

    def _parse_hospitalization(self, hosp_node, ns):
        def search_model(model, key):
            return self.env[model].search([('key', '=', key)], limit=1).id if key else None

        def get_value(path):
            node = hosp_node.find(path, ns)
            return node.get('value') if node is not None else None

        self.hospitalization_nrnHospitalization = get_value('./nhis:nrnHospitalization')
        self.hospitalization_lrn = get_value('./nhis:lrn')
        self.hospitalization_status = search_model('trinity.nomenclature.cl074', get_value('./nhis:status'))
        self.hospitalization_authoredOn = get_value('./nhis:authoredOn')

        # Parse correction reasons (multiple)
        correction_reasons = hosp_node.findall('./nhis:correctionReason', ns)
        if correction_reasons:
            self.hospitalization_correctionReason = '\n'.join([cr.get('value', '') for cr in correction_reasons if cr.get('value')])

        self.hospitalization_basedOn = get_value('./nhis:basedOn')
        self.hospitalization_admissionType = search_model('trinity.nomenclature.cl059', get_value('./nhis:admissionType'))
        self.hospitalization_clinicalPathway = search_model('trinity.nomenclature.cl062', get_value('./nhis:clinicalPathway'))
        self.hospitalization_outpatientProcedure = search_model('trinity.nomenclature.cl063', get_value('./nhis:outpatientProcedure'))
        self.hospitalization_dischargeClinicalPathway = search_model('trinity.nomenclature.cl062', get_value('./nhis:dischargeClinicalPathway'))
        self.hospitalization_dischargeOutpatientProcedure = search_model('trinity.nomenclature.cl063', get_value('./nhis:dischargeOutpatientProcedure'))
        self.hospitalization_directedBy = search_model('trinity.nomenclature.cl060', get_value('./nhis:directedBy'))
        self.hospitalization_reasonCode = search_model('trinity.nomenclature.cl061', get_value('./nhis:reasonCode'))
        self.hospitalization_note = get_value('./nhis:note')
        self.hospitalization_journalNumber = get_value('./nhis:journalNumber')
        self.hospitalization_practiceNumber = get_value('./nhis:practiceNumber')
        self.hospitalization_admissionDate = get_value('./nhis:admissionDate')
        self.hospitalization_elapsedTime = search_model('trinity.nomenclature.cl067', get_value('./nhis:elapsedTime'))
        self.hospitalization_severity = search_model('trinity.nomenclature.cl066', get_value('./nhis:severity'))
        self.hospitalization_financingSource = search_model('trinity.nomenclature.cl069', get_value('./nhis:financingSource'))
        self.hospitalization_bloodType = search_model('trinity.nomenclature.cl070', get_value('./nhis:bloodType'))
        self.hospitalization_dietPreference = search_model('trinity.nomenclature.cl079', get_value('./nhis:dietPreference'))
        self.hospitalization_dischargeDate = get_value('./nhis:dischargeDate')
        self.hospitalization_outcome = search_model('trinity.nomenclature.cl075', get_value('./nhis:outcome'))
        self.hospitalization_dischargeDisposition = search_model('trinity.nomenclature.cl080', get_value('./nhis:dischargeDisposition'))
        self.hospitalization_dischargeNote = get_value('./nhis:dischargeNote')
        self.hospitalization_daysHospitalized = int(get_value('./nhis:daysHospitalized') or 0)
        self.hospitalization_deceasedDate = get_value('./nhis:deceasedDate')
        self.hospitalization_autopsyDate = get_value('./nhis:autopsyDate')
        self.hospitalization_workability = search_model('trinity.nomenclature.cl081', get_value('./nhis:workability'))

    def _parse_patient(self, patient_node, ns):
        def search_model(model, key):
            return self.env[model].search([('key', '=', key)], limit=1).id if key else None

        get_val = lambda node: node.get('value') if node is not None else None

        self.subject_identifierType = search_model('trinity.nomenclature.cl004', get_val(patient_node.find('./nhis:identifierType', ns)))
        self.subject_identifier = get_val(patient_node.find('./nhis:identifier', ns))
        self.subject_birthDate = get_val(patient_node.find('./nhis:birthDate', ns))
        self.subject_gender = search_model('trinity.nomenclature.cl001', get_val(patient_node.find('./nhis:gender', ns)))
        self.subject_nationality = search_model('trinity.nomenclature.cl005', get_val(patient_node.find('./nhis:nationality', ns)))
        self.subject_phone = get_val(patient_node.find('./nhis:phone', ns))
        self.subject_email = get_val(patient_node.find('./nhis:email', ns))

        # Parse name
        name_node = patient_node.find('./nhis:name', ns)
        if name_node:
            self.subject_given = get_val(name_node.find('./nhis:given', ns))
            self.subject_middle = get_val(name_node.find('./nhis:middle', ns))
            self.subject_family = get_val(name_node.find('./nhis:family', ns))

        # Parse address
        addr_node = patient_node.find('./nhis:address', ns)
        if addr_node:
            self.subject_country = search_model('trinity.nomenclature.cl005', get_val(addr_node.find('./nhis:country', ns)))
            self.subject_county = search_model('trinity.nomenclature.cl041', get_val(addr_node.find('./nhis:county', ns)))
            self.subject_city = get_val(addr_node.find('./nhis:city', ns))
            self.subject_line = get_val(addr_node.find('./nhis:line', ns))
            self.subject_postalCode = get_val(addr_node.find('./nhis:postalCode', ns))

        # Parse various
        various_node = patient_node.find('./nhis:various', ns)
        if various_node:
            age_val = get_val(various_node.find('./nhis:age', ns))
            self.subject_age = float(age_val) if age_val else 0.0
            weight_val = get_val(various_node.find('./nhis:weight', ns))
            self.subject_weight = float(weight_val) if weight_val else 0.0
            self.subject_maritalStatus = search_model('trinity.nomenclature.cl064', get_val(various_node.find('./nhis:maritalStatus', ns)))
            self.subject_education = search_model('trinity.nomenclature.cl065', get_val(various_node.find('./nhis:education', ns)))
            self.subject_workplace = get_val(various_node.find('./nhis:workplace', ns))
            self.subject_profession = get_val(various_node.find('./nhis:profession', ns))


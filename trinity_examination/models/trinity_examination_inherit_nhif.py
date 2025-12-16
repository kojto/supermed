# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.misc import html_escape
from odoo.exceptions import ValidationError, UserError
from lxml import etree
from xml.etree import ElementTree as ET
import base64
import datetime
from datetime import timezone, timedelta
import uuid
import logging

_logger = logging.getLogger(__name__)

class TrinityExamination(models.Model):
    _inherit = 'trinity.examination'

    X001 = fields.Text(string='X001', copy=False)
    X003 = fields.Text(string='X003', copy=False)
    X005 = fields.Text(string='X005', copy=False)
    X007 = fields.Text(string='X007', copy=False)
    X009 = fields.Text(string='X009', copy=False)
    X011 = fields.Text(string='X011', copy=False)
    X013 = fields.Text(string='X013', copy=False)

    X001_signed = fields.Char(string='X001 Signed Text', default='not signed', copy=False)
    X003_signed = fields.Char(string='X003 Signed Text', default='not signed', copy=False)
    X005_signed = fields.Char(string='X005 Signed Text', default='not signed', copy=False)
    X007_signed = fields.Char(string='X007 Signed Text', default='not signed', copy=False)
    X009_signed = fields.Char(string='X009 Signed Text', default='not signed', copy=False)
    X011_signed = fields.Char(string='X011 Signed Text', default='not signed', copy=False)
    X013_signed = fields.Char(string='X013 Signed Text', default='not signed', copy=False)

    SignedInfo_X001 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_X003 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_X005 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_X007 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_X009 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_X011 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_X013 = fields.Char(string="SignedInfo", copy=False)

    SignedInfo_X001_signature = fields.Char(string="SignedInfo signature", copy=False)
    SignedInfo_X003_signature = fields.Char(string="SignedInfo signature", copy=False)
    SignedInfo_X005_signature = fields.Char(string="SignedInfo signature", copy=False)
    SignedInfo_X007_signature = fields.Char(string="SignedInfo signature", copy=False)
    SignedInfo_X009_signature = fields.Char(string="SignedInfo signature", copy=False)
    SignedInfo_X011_signature = fields.Char(string="SignedInfo signature", copy=False)
    SignedInfo_X013_signature = fields.Char(string="SignedInfo signature", copy=False)

    X002 = fields.Text('X002', copy=False)
    X004 = fields.Text('X004', copy=False)
    X006 = fields.Text('X006', copy=False)
    X008 = fields.Text('X008', copy=False)
    X010 = fields.Text('X010', copy=False)
    X012 = fields.Text('X012', copy=False)
    X014 = fields.Text('X014', copy=False)

    hospitalization_active_today = fields.Char(string='Активна хоспитализация днес', copy=False)
    isHospitalised = fields.Boolean(string='Има активна хоспитализация', compute='_compute_is_hospitalised', store=True)

    @api.depends('hospitalization_active_today')
    def _compute_is_hospitalised(self):
        for record in self:
            message = (record.hospitalization_active_today or '').lower()
            record.isHospitalised = bool(message and 'има' in message)

    def clear_X_fields(self):
        for record in self:
            x_types = ['X001', 'X003', 'X005', 'X007', 'X011', 'X013']
            x_types_no_raw = ['X009']
            fields_to_clear = {}
            for x_type in x_types:
                fields_to_clear.update({
                    x_type: "",
                    f"{x_type}_signed": "",
                    f"SignedInfo_{x_type}": "",
                    f"SignedInfo_{x_type}_signature": "",
                })
            for x_type in x_types_no_raw:
                fields_to_clear.update({
                    x_type: "",
                    f"{x_type}_signed": "",
                    f"SignedInfo_{x_type}": "",
                    f"SignedInfo_{x_type}_signature": "",
                })

            record.write(fields_to_clear)

    tokenRequest = fields.Text(string='tokenRequest', copy=False)
    SignedInfo_tokenRequest = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_tokenRequest_signature = fields.Char(string="SignedInfo signature", copy=False)
    tokenRequest_signed = fields.Char(string="tokenRequest signed", copy=False)
    tokenResponse = fields.Text('tokenResponse', copy=False)


    def getPatientPadSignature(self):
        self.signPenXmessage()
        return

    ############################################################################
    #                             onchange fields                              #
    ############################################################################

    # --- onchange --- #

    @api.onchange('patient_identifier_id', 'e_examination_lrn', 'examination_open_dtm', 'examination_close_dtm', 'examination_class', 'financingSource', 'patient_rhifareanumber_key.key', 'basedOn_e_examination_nrn', 'previous_e_examination_nrn', 'secondary_examination', 'examination_purpose', 'medical_history', 'patient_isPregnant', 'patient_isBreastFeeding', 'patient_gestationalWeek', 'icd_codes', 'diagnosis', 'objective_condition', 'assessment_notes', 'therapy_note', 'conclusion', 'documents', 'documents_nrnImmunization', 'documents_nrnReferral', 'documents_issuedTelkDocument', 'documents_issuedQuickNotice', 'documents_issuedInterimReport', 'nhif_procedure_code', 'diagnosticReport_status', 'diagnosticReport_numberPerformed', 'main_dr_performing_doctor_id', 'motherHealthcare_isPregnant', 'motherHealthcare_isBreastFeeding', 'gestational_week', 'icd_code', 'diagnosis_use', 'patient_birth_date', 'patient_first_name', 'patient_last_name', 'patient_country', 'patient_county', 'patient_ekatte_key', 'performer_role', 'deputizing_dr_performing_doctor_id', 'deputizing_dr_performing_qualification_code', 'deputizing_dr_performing_qualification_code_nhif', 'main_dr_performing_practiceNumber','examination_correctionReason', 'examination_conclusion', 'examination_dischargeDisposition')
    def generate_X_SignPen_fields(self):
        self.clear_signPen_X_message_fields()
        self.generate_X_fields()
        self.signPenXmessage()

    @api.onchange('SignData', 'RsaSignature', 'signatureCert')
    def generate_X_fields(self):
        self.compute_X009()
        self.compute_X013()

    ############################################################################
    #                           NHIF XML GENERATION                            #
    ############################################################################

    nhif_xml = fields.Text(string='nhif_xml', copy=False)

    def compute_nhif_xml(self):
        for record in self:
            esc = html_escape
            nhif_xml = f"""<AmbList>
                <NoAl>{esc(record.e_examination_nrn if record.e_examination_nrn else '')}</NoAl>
                <dataAl>{esc(record.examination_open_dtm.strftime("%Y-%m-%d") if isinstance(record.examination_open_dtm, datetime.datetime) else '')}</dataAl>
                <time>{esc(record.examination_open_dtm.strftime("%H:%M:%S") if isinstance(record.examination_open_dtm, datetime.datetime) else '')}</time>
                <Pay>1</Pay>
                <Patient>
                <EGN>{esc(record.patient_identifier_id.identifier if record.patient_identifier_id.identifier else '')}</EGN>
                <RZOK>{esc(record.patient_RZOK[:2] if record.patient_RZOK else '22')}</RZOK>
                <ZdrRajon>{esc(record.patient_RZOK[-2:] if record.patient_RZOK else '01')}</ZdrRajon>
                <Name>
                <Given>{esc(record.patient_first_name if record.patient_first_name else '')}</Given>
                <Sur>{esc(record.patient_middle_name if record.patient_middle_name else '')}</Sur>
                <Family>{esc(record.patient_last_name if record.patient_last_name else '')}</Family>
                </Name>
                <Address>{esc(record.patient_identifier_id.city if record.patient_identifier_id.city else '')}</Address>
                <IsHealthInsurance>0</IsHealthInsurance>
                </Patient>
                <Disadv>0</Disadv>
                <Incidentally>0</Incidentally>
                <MainDiag>
                <imeMD>{esc(record.icd_codes[0].description if record.icd_codes and record.icd_codes[0].description else 'Общ медицински преглед')}</imeMD>
                <MKB>{esc(record.icd_codes[0].key if record.icd_codes and record.icd_codes[0].key else 'Z00.0')}</MKB>
                </MainDiag>
                <Procedure>
                <imeP>Медицински преглед в амбулаторни или домашни условия, със снемане на анамнеза, общ и локален статус,</imeP>
                <kodP>89.03</kodP>
                </Procedure>
                <Anamnesa>{esc(record.medical_history if record.medical_history else '')}</Anamnesa>
                <HState>{esc(record.objective_condition if record.objective_condition else '')}</HState>
                <Examine>{esc(record.assessment_notes if record.assessment_notes else '')}</Examine>
                <Therapy>
                <Nonreimburce>{esc(record.conclusion if record.conclusion else '')}\n{esc(record.therapy_note if record.therapy_note else '')}</Nonreimburce>
                </Therapy>
                <SIMPList>"""

            if record.secondary_examination == False:
                nhif_xml += f"""<PrimaryVisit>
                <VidNapr>1</VidNapr>
                <NoNapr>{esc(record.basedOn_e_examination_nrn if record.basedOn_e_examination_nrn else '')}</NoNapr>
                <NaprFor>1</NaprFor>
                <dateNapr>{esc(record.basedOn_e_examination_nrn_date if record.basedOn_e_examination_nrn_date else '')}</dateNapr>
                <SendedFrom>
                <PracticeCode>{esc(record.basedOn_e_examination_nrn_sentbyPractice if record.basedOn_e_examination_nrn_sentbyPractice else '')}</PracticeCode>
                <UIN>{esc(record.basedOn_e_examination_nrn_sentbyDoctorId if record.basedOn_e_examination_nrn_sentbyDoctorId else '')}</UIN>
                <SIMPCode>{esc(record.basedOn_e_examination_nrn_sentbyDoctor_qualification_code if record.basedOn_e_examination_nrn_sentbyDoctor_qualification_code else '')}</SIMPCode>
                </SendedFrom>
                </PrimaryVisit>"""

            if record.secondary_examination == True:
                nhif_xml += f"""<SecondaryVisit>
                <NoAmbL>{esc(record.basedOn_e_examination_nrn or record.previous_e_examination_nrn or '')}</NoAmbL>
                <dateAmbL>{esc(record.basedOn_e_examination_nrn_date or (record.previous_examination_open_dtm and record.previous_examination_open_dtm.strftime("%Y-%m-%d")) or '')}</dateAmbL>
                </SecondaryVisit>"""

            nhif_xml += f"""</SIMPList>
                <VisitFor>
                <Consult>1</Consult>
                <Disp>0</Disp>
                <Babycare>0</Babycare>
                <RpHosp>0</RpHosp>
                <LKKVisit>0</LKKVisit>
                <Telk>0</Telk>
                </VisitFor>"""

            if record.secondary_examination == True:
                nhif_xml += f"""
                <ExamType>12</ExamType>"""

            if record.secondary_examination == False:
                nhif_xml += f"""
                <ExamType>11</ExamType>"""

            nhif_xml += f"""
                <Docs>
                <TalonTELK>0</TalonTELK>
                <Izvestie>0</Izvestie>
                <EtEpikriza>0</EtEpikriza>
                <MedicalNote>0</MedicalNote>
                </Docs>
                <Sign>1</Sign>
                </AmbList>"""

            record.nhif_xml = nhif_xml

    def download_nhif_xml(self, docids):
        _logger.info("Generating combined XML for docids: %s", docids)
        records = self.env['trinity.examination'].browse(docids).filtered(
            lambda r: 'НЗОК' in r.cost_bearer_id.name if r.cost_bearer_id.name else False
        )

        if not records:
            _logger.warning("No records found.")
            return {}

        record = records[0]

        first_day = record.examination_open_dtm.replace(day=1).strftime('%Y-%m-%d')

        next_month = record.examination_open_dtm.replace(day=28) + datetime.timedelta(days=4)
        last_day = (next_month - datetime.timedelta(days=next_month.day)).strftime('%Y-%m-%d')

        combined_xml = (f'<Practice>'
                        f'<PracticeCode>{record.main_dr_performing_practiceNumber}</PracticeCode>\n'
                        f'<PracticeName>{record.main_dr_performing_practiceName}</PracticeName>\n'
                        f'<ContractNo>{record.main_dr_performing_nhif_ContractNo}</ContractNo>\n<ContractDate>{record.main_dr_performing_nhif_ContractDate.strftime("%Y-%m-%d")}</ContractDate>\n'
                        f'<DateFrom>{first_day}</DateFrom>\n<DateTo>{last_day}</DateTo>\n<ContrHA>0</ContrHA>\n'
                        f'<Doctor>\n<UIN>{record.main_dr_performing_doctor_id.doctor_id}</UIN>\n<EGN>{record.main_dr_performing_identifier}</EGN>\n'
                        f'<FullName>{record.main_dr_performing_full_name}</FullName>\n<SIMPCode>{record.main_dr_performing_qualification_code_nhif}</SIMPCode>\n'
                        f'</Doctor>\n</Practice>')

        insertion_point = combined_xml.find('</Doctor>')
        if insertion_point == -1:
            _logger.warning("Could not find </Doctor> tag, appending XML at the end.")
            insertion_point = len(combined_xml)

        for rec in records:
            if isinstance(rec.nhif_xml, str):
                combined_xml = combined_xml[:insertion_point] + rec.nhif_xml + combined_xml[insertion_point:]
                insertion_point += len(rec.nhif_xml)

        # Beautify XML using lxml
        pretty_xml = self.format_xml(combined_xml)

        if records:
            lrn_prefix = records[0].e_examination_lrn[:7]
            filename = f'МЦ_СВ_ТРОИЦА-ОТЧЕТ_НЗОК-{lrn_prefix}.xml'
        else:
            filename = f'празен.xml'

        file_b64 = base64.b64encode(pretty_xml.encode('utf-8'))

        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/xml'
        }
        attachment = self.env['ir.attachment'].sudo().create(attachment_data)

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def format_xml(self, xml_string):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(xml_string, parser)
        return etree.tostring(tree, pretty_print=True, encoding="utf-8", xml_declaration=True).decode('utf-8')


    ############################################################################
    #                              XML GENERATION                              #
    ############################################################################

    # --- start X001 --- #

    def compute_X001(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            esc = html_escape

            X001 = f"""<nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg">
            <nhis:header>
                <nhis:sender value="1" />
                <nhis:senderId value="{esc(record.main_dr_performing_doctor_id.doctor_id or '')}" />
                <nhis:senderISName value="Supermed 1.0.1" />
                <nhis:recipient value="4" />
                <nhis:recipientId value="NHIS" />
                <nhis:messageId value="{esc(uuid_value)}" />
                <nhis:messageType value="X001" />
                <nhis:createdOn value="{esc(current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))}" />
            </nhis:header>
            <nhis:contents>
                <nhis:examination>
                    <nhis:lrn value="{esc(record.e_examination_lrn or '')}" />
                    <nhis:openDate value="{esc(record.examination_open_dtm.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if isinstance(record.examination_open_dtm, datetime.datetime) else '')}" />
                    <nhis:class value="{esc(record.examination_class.key if record.examination_class else '')}" />
                    <nhis:financingSource value="{esc(record.financingSource.key if record.financingSource else '')}" />"""

            if record.examination_screening:
                X001 += f"""
                    <nhis:screening value="{esc(record.examination_screening.key if hasattr(record.examination_screening, 'key') else str(record.examination_screening))}" />"""

            X001 += f"""
                    <nhis:rhifAreaNumber value="{esc(record.patient_rhifareanumber_key.key if record.patient_rhifareanumber_key else '2201')}" />
                </nhis:examination>
                <nhis:subject>
                    <nhis:identifierType value="{esc(record.patient_identifier_id.identifier_type.key if record.patient_identifier_id and record.patient_identifier_id.identifier_type else '')}" />
                    <nhis:identifier value="{esc(record.patient_identifier_id.identifier or '')}" />"""

            if record.patient_nhifInsuranceNumber:
                X001 += f"""
                    <nhis:nhifInsuranceNumber value="{esc(record.patient_nhifInsuranceNumber)}" />"""

            X001 += f"""
                    <nhis:birthDate value="{esc(record.patient_birth_date.strftime('%Y-%m-%d') if record.patient_birth_date else '')}" />
                    <nhis:gender value="{esc(record.patient_identifier_id.gender.key if record.patient_identifier_id and record.patient_identifier_id.gender else '')}" />
                    <nhis:nationality value="{esc(record.patient_nationality.key if record.patient_nationality else 'BG')}" />
                    <nhis:name>
                        <nhis:given value="{esc(record.patient_first_name or '')}" />"""

            if record.patient_middle_name:
                X001 += f"""
                        <nhis:middle value="{esc(record.patient_middle_name)}" />"""

            X001 += f"""
                        <nhis:family value="{esc(record.patient_last_name or '')}" />
                    </nhis:name>
                </nhis:subject>
                <nhis:performer>
                    <nhis:pmi value="{esc(record.main_dr_performing_doctor_id.doctor_id or '')}" />"""

            if record.performer_role and record.performer_role.key != "1":
                X001 += f"""
                    <nhis:pmiDeputy value="{esc(record.deputizing_dr_performing_doctor_id.doctor_id or '')}" />"""

            X001 += f"""
                    <nhis:qualification value="{esc(record.main_dr_performing_qualification_code.key or '')}" nhifCode="{esc(record.main_dr_performing_qualification_code_nhif or '')}" />
                    <nhis:role value="{esc(record.performer_role.key if record.performer_role else '1')}" />"""

            if record.performer_role and record.performer_role.key != "1":
                X001 += f"""
                    <nhis:accompanying>
                        <nhis:pmi value="{esc(record.deputizing_dr_performing_doctor_id.doctor_id or '')}" />
                        <nhis:qualification value="{esc(record.deputizing_dr_performing_qualification_code.key or '')}" nhifCode="{esc(record.deputizing_dr_performing_qualification_code_nhif or '')}" />
                    </nhis:accompanying>"""

            X001 += f"""
                    <nhis:practiceNumber value="{esc(record.main_dr_performing_practiceNumber or '2203131524')}" />
                    <nhis:nhifNumber value="{esc(record.main_dr_performing_nhif_Number or '8888')}" />
                    <nhis:phone value="{esc(record.main_dr_performing_phone or '+3594215555')}" />
                    <nhis:email value="{esc(record.main_dr_performing_email or 'supermed@supermed.bg')}" />
                    <nhis:rhifAreaNumber value="{esc(record.main_dr_performing_rhifareanumber_key.key if record.main_dr_performing_rhifareanumber_key else '2201')}" />
                </nhis:performer>
            </nhis:contents>
        </nhis:message>"""

            record.X001 = X001
            record.sign_X001()

    def getSignatureX001(self):
        self.compute_X001()
        return

    def sign_X001(self, field_name='X001', signedinfo='SignedInfo_X001', signedinfo_signature='SignedInfo_X001_signature', is_signed='X001_signed'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_X001(self):
        return self.download_file('X001')

    def X001_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'X001_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    # --- end X001 --- #

    # --- start X003 --- #

    def compute_X003(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            esc = html_escape

            if not record.e_examination_nrn:
                _logger.warning("Cannot generate X003 without examination NRN")
                record.X003 = ""
                return

            X003 = f"""<nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg">
            <nhis:header>
                <nhis:sender value="1" />
                <nhis:senderId value="{esc(record.main_dr_performing_doctor_id.doctor_id or '')}" />
                <nhis:senderISName value="Supermed 1.0.1" />
                <nhis:recipient value="4" />
                <nhis:recipientId value="NHIS" />
                <nhis:messageId value="{esc(uuid_value)}" />
                <nhis:messageType value="X003" />
                <nhis:createdOn value="{esc(current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))}" />
            </nhis:header>
            <nhis:contents>
                <nhis:examination>
                    <nhis:nrnExamination value="{esc(record.e_examination_nrn or '')}" />"""

            if (record.main_dr_performing_qualification_code and record.main_dr_performing_qualification_code.key not in ('1043', '0000') and record.financingSource and record.financingSource.key == '2' and record.examination_purpose and record.examination_purpose.key != '12') or record.secondary_examination:
                X003 += f"""
                    <nhis:basedOn value="{esc(record.basedOn_e_examination_nrn or record.previous_e_examination_nrn or '')}" />"""

            else:
                X003 += f"""
                    <nhis:directedBy value="{esc(record.directedBy.key if record.directedBy else '8')}" />"""

            X003 += f"""
                    <nhis:isSecondary value="{esc(str(record.secondary_examination).lower() if record.secondary_examination is not None else 'false')}" />
                    <nhis:closeDate value="{esc(record.examination_close_dtm.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if isinstance(record.examination_close_dtm, datetime.datetime) else '')}" />
                    <nhis:purpose value="{esc(record.examination_purpose.key if record.examination_purpose else '')}" />
                    <nhis:adverseConditions value="{esc(str(record.examination_adverseConditions).lower() if record.examination_adverseConditions is not None else 'false')}" />
                    <nhis:incidentalVisit value="{esc(str(record.examination_incidentalVisit).lower() if record.examination_incidentalVisit is not None else 'true')}" />
                    <nhis:diagnosis>
                        <nhis:code value="{esc(record.icd_codes[0].key if record.icd_codes and record.icd_codes[0].key else 'Z00.0')}" />
                        <nhis:use value="{esc(record.diagnosis_use.key if record.diagnosis_use else '')}" />
                        <nhis:rank value="1" />
                        <nhis:note value="{esc(record.icd_codes[0].description if record.icd_codes and record.icd_codes[0].description else '')}" />
                        <nhis:clinicalStatus value="{esc(record.clinicalStatus.key if record.clinicalStatus else '10')}" />
                        <nhis:verificationStatus value="{esc(record.verificationStatus.key if record.verificationStatus else '10')}" />
                        <nhis:onsetDateTime value="{esc(record.onsetDateTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if record.onsetDateTime else '')}" />
                    </nhis:diagnosis>
                    <nhis:medicalHistory>
                        <nhis:note value="{esc(record.medical_history or '')}" />
                    </nhis:medicalHistory>
                    <nhis:objectiveCondition>"""

            if record.patient_gender and record.patient_gender.key == "2":
                X003 += f"""
                        <nhis:isPregnant value="{esc(str(record.patient_isPregnant).lower() if record.patient_isPregnant is not None else 'false')}" />
                        <nhis:isBreastFeeding value="{esc(str(record.patient_isBreastFeeding).lower() if record.patient_isBreastFeeding is not None else 'false')}" />"""

            if record.patient_isPregnant:
                X003 += f"""
                        <nhis:gestationalWeek value="{esc(record.patient_gestationalWeek or '')}" />"""

            X003 += f"""
                        <nhis:note value="{esc(record.objective_condition or '')}" />
                    </nhis:objectiveCondition>
                    <nhis:assessment>
                        <nhis:note value="{esc(record.assessment_notes or '')}" />
                    </nhis:assessment>
                    <nhis:therapy>
                        <nhis:note value="{esc(record.therapy_note or '')} {esc(record.conclusion or '')}" />
                    </nhis:therapy>"""

            if record.documents:
                X003 += f"""
                        <nhis:documents>
                            <nhis:nrnImmunization value="{esc(record.documents_nrnImmunization or 'false')}" />
                            <nhis:nrnReferral value="{esc(record.documents_nrnReferral or 'false')}" />
                            <nhis:issuedTelkDocument value="{esc(record.documents_issuedTelkDocument or 'false')}" />
                            <nhis:issuedQuickNotice value="{esc(record.documents_issuedQuickNotice or 'false')}" />
                            <nhis:issuedInterimReport value="{esc(record.documents_issuedInterimReport or 'false')}" />
                        </nhis:documents>"""

            if record.diagnosticReport:
                X003 += f"""
                    <nhis:diagnosticReport>
                        <nhis:code value="{esc(record.diagnosticReport_code.meta_nhif_code or '')}" />
                        <nhis:status value="{esc(record.diagnosticReport_status.key or '')}" />
                        <nhis:numberPerformed value="{esc(record.diagnosticReport_numberPerformed or '1')}" />
                    </nhis:diagnosticReport>"""

            X003 += f"""
                </nhis:examination>
            </nhis:contents>"""

            sign_condition = record.SignData or (record.financingSource and record.financingSource.key not in ('7', '4'))

            if sign_condition:
                X003 += f"""
                    <nhis:patientSignature>
                        <nhis:device>
                            <nhis:manufacturer value="{html_escape(record.pad_manufacturer.key if record.pad_manufacturer else '2')}"/>
                            <nhis:model value="{html_escape(record.pad_model.key if record.pad_model else '6')}"/>
                        </nhis:device>
                        <nhis:isPatientSigner value="{'true' if record.isPatientSigner else 'false'}"/>
                        <nhis:signatureObject value="{html_escape(record.SignData or '')}"/>
                        <nhis:signatureCertificate value="{html_escape(record.signatureCert or '')}"/>
                        <nhis:signature value="{html_escape(record.RsaSignature or '')}"/>"""

                if not record.isPatientSigner:
                    X003 += f"""
                        <nhis:signer>
                            <nhis:identifierType value="{html_escape(record.parent_identifier_type.key) if record.parent_identifier_type else ''}" />
                            <nhis:identifier value="{html_escape(record.parent_identifier_id or '')}" />
                            <nhis:name>
                                <nhis:given value="{html_escape(record.parent_first_name or '')}" />
                                <nhis:family value="{html_escape(record.parent_last_name or '')}" />
                            </nhis:name>
                        </nhis:signer>"""

                X003 += f"""
                    </nhis:patientSignature>"""

            X003 += f"""
        </nhis:message>"""

        record.X003 = X003
        record.sign_X003()

    def getSignatureX003(self):
        self.compute_X003()
        return

    def sign_X003(self, field_name='X003', signedinfo='SignedInfo_X003', signedinfo_signature='SignedInfo_X003_signature', is_signed='X003_signed'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_X003(self):
        return self.download_file('X003')

    def X003_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'X003_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    # --- end X003 --- #

    # --- start X007 --- #

    def compute_X007(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            X007 = f"""<nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg">
            <nhis:header>
                <nhis:sender value="1" />
                <nhis:senderId value="{record.main_dr_performing_doctor_id.doctor_id or ''}" />
                <nhis:senderISName value="Supermed 1.0.1" />
                <nhis:recipient value="4" />
                <nhis:recipientId value="NHIS" />
                <nhis:messageId value="{uuid_value}" />
                <nhis:messageType value="X007" />
                <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}" />
            </nhis:header>
            <nhis:contents>
                <nhis:nrnExamination value="{record.e_examination_nrn or ''}" />
                <nhis:cancelReason value="Поради техническа грешка се налага анулиране на прегледа"/>
            </nhis:contents>
            </nhis:message>"""
        record.X007 = X007
        record.sign_X007()

    def getSignatureX007(self):
        return

    def sign_X007(self, field_name='X007', signedinfo='SignedInfo_X007', signedinfo_signature='SignedInfo_X007_signature', is_signed='X007_signed'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_X007(self):
        return self.download_file('X007')

    def X007_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'X007_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    # --- end X007 --- #

    # --- start X009 --- #
    def compute_X009(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            esc = html_escape

            if not record.e_examination_nrn:
                _logger.warning("Cannot generate X009 without examination NRN")
                record.X009 = ""
                return

            X009 = f"""<nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg">
            <nhis:header>
                <nhis:sender value="1" />
                <nhis:senderId value="{esc(record.main_dr_performing_doctor_id.doctor_id or '')}" />
                <nhis:senderISName value="Supermed 1.0.1" />
                <nhis:recipient value="4" />
                <nhis:recipientId value="NHIS" />
                <nhis:messageId value="{esc(uuid_value)}" />
                <nhis:messageType value="X009" />
                <nhis:createdOn value="{esc(current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))}" />
            </nhis:header>
            <nhis:contents>
                <nhis:examination>
                    <nhis:nrnExamination value="{esc(record.e_examination_nrn or '')}" />
                    <nhis:lrn value="{esc(record.e_examination_lrn or '')}" />
                    <nhis:class value="{esc(record.examination_class.key if record.examination_class else '')}" />
                    <nhis:financingSource value="{esc(record.financingSource.key if record.financingSource else '')}" />
                    <nhis:rhifAreaNumber value="{esc(record.patient_rhifareanumber_key.key or '2201')}" />"""

            if (record.main_dr_performing_qualification_code and record.main_dr_performing_qualification_code.key not in ('1043', '0000') and record.financingSource and record.financingSource.key == '2' and record.examination_purpose and record.examination_purpose.key != '12') or record.secondary_examination:
                X009 += f"""
                    <nhis:basedOn value="{esc(record.basedOn_e_examination_nrn or record.previous_e_examination_nrn or '')}" />"""

            else:
                X009 += f"""
                    <nhis:directedBy value="{esc(record.directedBy.key if record.directedBy else '8')}" />"""

            X009 += f"""
                    <nhis:correctionReason value="{esc(record.examination_correctionReason or 'Корекция на преглед')}" />
                    <nhis:isSecondary value="{esc(str(record.secondary_examination).lower() if record.secondary_examination is not None else 'false')}" />
                    <nhis:purpose value="{esc(record.examination_purpose.key if record.examination_purpose else '')}" />
                    <nhis:adverseConditions value="false" />
                    <nhis:incidentalVisit value="true" />
                    <nhis:diagnosis>
                        <nhis:code value="{esc(record.icd_codes[0].key if record.icd_codes and record.icd_codes[0].key else 'Z00.0')}" />
                        <nhis:use value="{esc(record.diagnosis_use.key if record.diagnosis_use else '')}" />
                        <nhis:rank value="1" />
                        <nhis:note value="{esc(record.icd_codes[0].description if record.icd_codes and record.icd_codes[0].description else '')}" />
                        <nhis:clinicalStatus value="{esc(record.clinicalStatus.key if record.clinicalStatus else '10')}" />
                        <nhis:verificationStatus value="{esc(record.verificationStatus.key if record.verificationStatus else '10')}" />
                        <nhis:onsetDateTime value="{esc(record.onsetDateTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if record.onsetDateTime else '')}" />
                    </nhis:diagnosis>
                    <nhis:medicalHistory>
                        <nhis:note value="{esc(record.medical_history or '')}" />
                    </nhis:medicalHistory>
                    <nhis:objectiveCondition>"""

            if record.patient_gender and record.patient_gender.key == "2":
                X009 += f"""
                        <nhis:isPregnant value="{esc(str(record.patient_isPregnant).lower() if record.patient_isPregnant is not None else 'false')}" />
                        <nhis:isBreastFeeding value="{esc(str(record.patient_isBreastFeeding).lower() if record.patient_isBreastFeeding is not None else 'false')}" />"""

            if record.patient_isPregnant:
                X009 += f"""
                        <nhis:gestationalWeek value="{esc(record.patient_gestationalWeek or '')}" />"""

            X009 += f"""
                        <nhis:note value="{esc(record.objective_condition or '')}" />
                    </nhis:objectiveCondition>
                    <nhis:assessment>
                        <nhis:note value="{esc(record.assessment_notes or '')}" />
                    </nhis:assessment>
                    <nhis:therapy>
                        <nhis:note value="{esc(record.therapy_note or '')} {esc(record.conclusion or '')}" />
                    </nhis:therapy>"""

            if record.examination_conclusion:
                X009 += f"""
                    <nhis:conclusion value="{esc(record.examination_conclusion.key)}" />"""

            if record.examination_dischargeDisposition:
                X009 += f"""
                    <nhis:dischargeDisposition value="{esc(record.examination_dischargeDisposition.key)}" />"""

            if record.documents:
                X009 += f"""
                        <nhis:documents>
                            <nhis:nrnImmunization value="{esc(record.documents_nrnImmunization or 'false')}" />
                            <nhis:nrnReferral value="{esc(record.documents_nrnReferral or 'false')}" />
                            <nhis:issuedTelkDocument value="{esc(record.documents_issuedTelkDocument or 'false')}" />
                            <nhis:issuedQuickNotice value="{esc(record.documents_issuedQuickNotice or 'false')}" />
                            <nhis:issuedInterimReport value="{esc(record.documents_issuedInterimReport or 'false')}" />
                        </nhis:documents>"""

            if record.diagnosticReport:
                X009 += f"""
                    <nhis:diagnosticReport>
                        <nhis:code value="{esc(record.diagnosticReport_code.meta_nhif_code or '')}" />
                        <nhis:status value="{esc(record.diagnosticReport_status.key or '')}" />
                        <nhis:numberPerformed value="{esc(record.diagnosticReport_numberPerformed or '1')}" />
                    </nhis:diagnosticReport>"""

            X009 += f"""
                </nhis:examination>
            </nhis:contents>"""

            sign_condition = record.SignData or (record.financingSource and record.financingSource.key not in ('7', '4'))

            if sign_condition:
                X009 += f"""
                    <nhis:patientSignature>
                        <nhis:device>
                            <nhis:manufacturer value="{html_escape(record.pad_manufacturer.key if record.pad_manufacturer else '2')}"/>
                            <nhis:model value="{html_escape(record.pad_model.key if record.pad_model else '6')}"/>
                        </nhis:device>
                        <nhis:isPatientSigner value="{'true' if record.isPatientSigner else 'false'}"/>
                        <nhis:signatureObject value="{html_escape(record.SignData or '')}"/>
                        <nhis:signatureCertificate value="{html_escape(record.signatureCert or '')}"/>
                        <nhis:signature value="{html_escape(record.RsaSignature or '')}"/>"""

                if not record.isPatientSigner:
                    X009 += f"""
                        <nhis:signer>
                            <nhis:identifierType value="{html_escape(record.parent_identifier_type.key) if record.parent_identifier_type else ''}" />
                            <nhis:identifier value="{html_escape(record.parent_identifier_id or '')}" />
                            <nhis:name>
                                <nhis:given value="{html_escape(record.parent_first_name or '')}" />
                                <nhis:family value="{html_escape(record.parent_last_name or '')}" />
                            </nhis:name>
                        </nhis:signer>"""

                X009 += f"""
                    </nhis:patientSignature>"""

            X009 += f"""
        </nhis:message>"""

        record.X009 = X009
        record.sign_X009()

    def getSignatureX009(self):
        return

    def sign_X009(self, field_name='X009', signedinfo='SignedInfo_X009', signedinfo_signature='SignedInfo_X009_signature', is_signed='X009_signed'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_X009(self):
        return self.download_file('X009')

    def X009_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'X009_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    # --- end X009 --- #

    # --- start X013 --- #
    def compute_X013(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            esc = html_escape

            X013 = f"""<nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:nhis="https://www.his.bg" xsi:schemaLocation="https://www.his.bg">
            <nhis:header>
                <nhis:sender value="1" />
                <nhis:senderId value="{esc(record.main_dr_performing_doctor_id.doctor_id or '')}" />
                <nhis:senderISName value="Supermed 1.0.1" />
                <nhis:recipient value="4" />
                <nhis:recipientId value="NHIS" />
                <nhis:messageId value="{esc(uuid_value)}" />
                <nhis:messageType value="X013" />
                <nhis:createdOn value="{esc(current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))}" />
            </nhis:header>
            <nhis:contents>
                <nhis:examination>
                    <nhis:lrn value="{esc(record.e_examination_lrn or '')}" />
                    <nhis:openDate value="{esc(record.examination_open_dtm.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if isinstance(record.examination_open_dtm, datetime.datetime) else '')}" />
                    <nhis:closeDate value="{esc(record.examination_close_dtm.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if isinstance(record.examination_close_dtm, datetime.datetime) else '')}" />
                    <nhis:class value="{esc(record.examination_class.key if record.examination_class else '')}" />
                    <nhis:financingSource value="{esc(record.financingSource.key if record.financingSource else '')}" />
                    <nhis:rhifAreaNumber value="{esc(record.patient_rhifareanumber_key.key or '2201')}" />"""

            if (record.main_dr_performing_qualification_code.key not in ('1043', '0000') and record.financingSource.key == '2' and record.examination_purpose.key != '12') or record.secondary_examination:
                X013 += f"""
                    <nhis:basedOn value="{esc(record.basedOn_e_examination_nrn or record.previous_e_examination_nrn or '')}" />"""

            else:
                X013 += f"""
                    <nhis:directedBy value="{esc(record.directedBy.key or '8')}" />"""

            X013 += f"""
                    <nhis:isSecondary value="{esc(str(record.secondary_examination).lower() if record.secondary_examination is not None else 'false')}" />
                    <nhis:purpose value="{esc(record.examination_purpose.key if record.examination_purpose else '')}" />
                    <nhis:adverseConditions value="false" />
                    <nhis:incidentalVisit value="true" />
                    <nhis:diagnosis>
                        <nhis:code value="{esc(record.icd_codes[0].key if record.icd_codes and record.icd_codes[0].key else 'Z00.0')}" />
                        <nhis:use value="{esc(record.diagnosis_use.key if record.diagnosis_use else '')}" />
                        <nhis:rank value="1" />
                        <nhis:note value="{esc(record.icd_codes[0].description if record.icd_codes and record.icd_codes[0].description else '')}" />
                        <nhis:clinicalStatus value="{esc(record.clinicalStatus.key if record.clinicalStatus else '10')}" />
                        <nhis:verificationStatus value="{esc(record.verificationStatus.key if record.verificationStatus else '10')}" />
                        <nhis:onsetDateTime value="{esc(record.onsetDateTime.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if record.onsetDateTime else '')}" />
                    </nhis:diagnosis>
                    <nhis:medicalHistory>
                        <nhis:note value="{esc(record.medical_history or '')}" />
                    </nhis:medicalHistory>
                    <nhis:objectiveCondition>"""

            if record.patient_gender.key == "2":
                X013 += f"""
                        <nhis:isPregnant value="{esc(str(record.patient_isPregnant).lower() if record.patient_isPregnant is not None else 'false')}" />
                        <nhis:isBreastFeeding value="{esc(str(record.patient_isBreastFeeding).lower() if record.patient_isBreastFeeding is not None else 'false')}" />"""

            if record.patient_isPregnant:
                X013 += f"""
                        <nhis:gestationalWeek value="{esc(record.patient_gestationalWeek or '')}" />"""

            X013 += f"""
                        <nhis:note value="{esc(record.objective_condition or '')}" />
                    </nhis:objectiveCondition>
                    <nhis:assessment>
                        <nhis:note value="{esc(record.assessment_notes or '')}" />
                    </nhis:assessment>
                    <nhis:therapy>
                        <nhis:note value="{esc(record.therapy_note or '')} {esc(record.conclusion or '')}" />
                    </nhis:therapy>"""

            # Examination Conclusion
            if record.examination_conclusion:
                X013 += f"""
                    <nhis:conclusion value="{esc(record.examination_conclusion.key)}" />"""

            # Discharge Disposition
            if record.examination_dischargeDisposition:
                X013 += f"""
                    <nhis:dischargeDisposition value="{esc(record.examination_dischargeDisposition.key)}" />"""

            if record.documents:
                X013 += f"""
                        <nhis:documents>
                            <nhis:nrnImmunization value="{esc(record.documents_nrnImmunization or 'false')}" />
                            <nhis:nrnReferral value="{esc(record.documents_nrnReferral or 'false')}" />
                            <nhis:issuedTelkDocument value="{esc(record.documents_issuedTelkDocument or 'false')}" />
                            <nhis:issuedQuickNotice value="{esc(record.documents_issuedQuickNotice or 'false')}" />
                            <nhis:issuedInterimReport value="{esc(record.documents_issuedInterimReport or 'false')}" />
                        </nhis:documents>"""

            if record.diagnosticReport:
                X013 += f"""
                    <nhis:diagnosticReport>
                        <nhis:code value="{esc(record.diagnosticReport_code.meta_nhif_code or '')}" />
                        <nhis:status value="{esc(record.diagnosticReport_status.key or '')}" />
                        <nhis:numberPerformed value="{esc(record.diagnosticReport_numberPerformed or '1')}" />
                    </nhis:diagnosticReport>"""

            X013 += f"""
                </nhis:examination>
                <nhis:subject>
                    <nhis:identifierType value="{esc(record.patient_identifier_id.identifier_type.key if record.patient_identifier_id.identifier_type else '')}" />
                    <nhis:identifier value="{esc(record.patient_identifier_id.identifier or '')}" />
                    <nhis:birthDate value="{esc(record.patient_birth_date.strftime('%Y-%m-%d') if record.patient_birth_date else '')}" />
                    <nhis:gender value="{esc(record.patient_identifier_id.gender.key if record.patient_identifier_id.gender else '')}" />
                    <nhis:name>
                        <nhis:given value="{esc(record.patient_first_name or '')}" />
                        <nhis:family value="{esc(record.patient_last_name or '')}" />
                    </nhis:name>
                    <nhis:nationality value="{esc(record.patient_nationality.key if record.patient_nationality else 'BG')}" />
                </nhis:subject>
                <nhis:performer>
                    <nhis:pmi value="{esc(record.main_dr_performing_doctor_id.doctor_id or '')}" />
                    <nhis:qualification value="{esc(record.main_dr_performing_qualification_code.key or '')}" nhifCode="{esc(record.main_dr_performing_qualification_code_nhif or '')}" />
                    <nhis:role value="{esc(record.performer_role.key if record.performer_role else '1')}" />"""

            if record.performer_role and record.performer_role.key != "1":
                X013 += f"""
                    <nhis:accompanying>
                        <nhis:pmi value="{esc(record.deputizing_dr_performing_doctor_id.doctor_id or '')}" />
                        <nhis:qualification value="{esc(record.deputizing_dr_performing_qualification_code.key or '')}" nhifCode="{esc(record.deputizing_dr_performing_qualification_code_nhif or '')}" />
                    </nhis:accompanying>"""

            X013 += f"""
                    <nhis:practiceNumber value="{esc(record.main_dr_performing_practiceNumber or '2203131524')}" />
                    <nhis:nhifNumber value="{esc(record.main_dr_performing_nhif_Number or '8888')}" />
                    <nhis:phone value="{esc(record.main_dr_performing_phone or '+3594215555')}" />
                    <nhis:email value="{esc(record.main_dr_performing_email or 'supermed@supermed.bg')}" />
                    <nhis:rhifAreaNumber value="{esc(record.main_dr_performing_rhifareanumber_key.key or '2201')}" />
                </nhis:performer>
            </nhis:contents>"""

            sign_condition = record.SignData or (record.financingSource and record.financingSource.key not in ('7', '4'))

            if sign_condition:
                X013 += f"""
                    <nhis:patientSignature>
                        <nhis:device>
                            <nhis:manufacturer value="{html_escape(record.pad_manufacturer.key if record.pad_manufacturer else '2')}"/>
                            <nhis:model value="{html_escape(record.pad_model.key if record.pad_model else '6')}"/>
                        </nhis:device>
                        <nhis:isPatientSigner value="{'true' if record.isPatientSigner else 'false'}"/>
                        <nhis:signatureObject value="{html_escape(record.SignData or '')}"/>
                        <nhis:signatureCertificate value="{html_escape(record.signatureCert or '')}"/>
                        <nhis:signature value="{html_escape(record.RsaSignature or '')}"/>"""

                if not record.isPatientSigner:
                    X013 += f"""
                        <nhis:signer>
                            <nhis:identifierType value="{html_escape(record.parent_identifier_type.key) if record.parent_identifier_type else ''}" />
                            <nhis:identifier value="{html_escape(record.parent_identifier_id or '')}" />
                            <nhis:name>
                                <nhis:given value="{html_escape(record.parent_first_name or '')}" />
                                <nhis:family value="{html_escape(record.parent_last_name or '')}" />
                            </nhis:name>
                        </nhis:signer>"""

                X013 += f"""
                    </nhis:patientSignature>"""

            X013 += f"""
        </nhis:message>"""

        record.X013 = X013
        record.sign_X013()

    def getSignatureX013(self):
        return

    def sign_X013(self, field_name='X013', signedinfo='SignedInfo_X013', signedinfo_signature='SignedInfo_X013_signature', is_signed='X013_signed'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_X013(self):
        return self.download_file('X013')

    def X013_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'X013_api_request')], limit=1)
        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field
            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    def check_response(self, response, field_response, request_msg_type=None):
        self.nzis_error_message = ''
        try:
            xml_root = ET.fromstring(response.text)
        except ET.ParseError:
            if "401 Authorization Required" in response.text:
                self.nzis_error_message = "НАПРАВЕТЕ ВРЪЗКА С НЗИС!"
            return

        ns = {'nhis': 'https://www.his.bg'}
        message_type = xml_root.find('.//nhis:messageType', ns)

        if message_type is not None and 'value' in message_type.attrib:
            msg_type_value = message_type.attrib['value']
        else:
            msg_type_value = None

        if request_msg_type in ['H001']:
            results_tags = xml_root.findall('.//nhis:results', ns)

            active_hospitalization_found = False
            for result_tag in results_tags:
                if result_tag is not None:
                    status_elem = result_tag.find('.//nhis:status', ns)
                    if status_elem is not None and status_elem.get('value') == '2':
                        active_hospitalization_found = True
                        break

            current_datetime = fields.Datetime.now()
            date_str = (current_datetime).strftime('%d.%m.%Y %H:%M')
            if active_hospitalization_found:
                self.hospitalization_active_today = f'Пациентът има активна хоспитализация на {date_str}!'
            else:
                self.hospitalization_active_today = f'Пациентът няма активна хоспитализация на {date_str}!'


        if request_msg_type not in ['H001']:
            self.clear_X_fields()
            nrn_examination = xml_root.find('.//nhis:nrnExamination', ns)
            nrn_basedOn = xml_root.find('.//nhis:basedOn', ns)
            status = xml_root.find('.//nhis:status', ns)
            error_reason = xml_root.find('.//nhis:reason', ns)

            if nrn_examination is not None and 'value' in nrn_examination.attrib:
                self.e_examination_nrn = nrn_examination.attrib['value']

            if nrn_basedOn is not None and 'value' in nrn_basedOn.attrib:
                self.basedOn_e_examination_nrn = nrn_basedOn.attrib['value']

            if error_reason is not None and 'value' in error_reason.attrib:
                self.nzis_error_message = error_reason.attrib['value']

            if status is not None and 'value' in status.attrib:
                status_key = status.attrib['value']
                status_record = self.env['trinity.nomenclature.cl055'].search([('key', '=', status_key)], limit=1)
                if status_record:
                    self.response_status = status_record.id

            if msg_type_value == 'X010':
                message_id_elem = xml_root.find('.//nhis:messageId', ns)
                created_on_elem = xml_root.find('.//nhis:createdOn', ns)

                if message_id_elem is not None and created_on_elem is not None:
                    message_id = message_id_elem.attrib.get('value', '')
                    created_on = created_on_elem.attrib.get('value', '')

                    correction_entry = f"Корекция №: {message_id} създадена на {created_on}"

                    if self.examination_correctionHistory:
                        self.examination_correctionHistory = f"{self.examination_correctionHistory}\n{correction_entry}"
                    else:
                        self.examination_correctionHistory = correction_entry

            if status is not None and 'value' in status.attrib and status.attrib['value'] == '2':
                self.compute_X007()

            if status is not None and 'value' in status.attrib and status.attrib['value'] == '3':
                self.e_examination_nrn = ''

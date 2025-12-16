from odoo import api, models, fields
from odoo.exceptions import UserError
from xml.etree import ElementTree as ET
import uuid
import logging
import datetime
from datetime import timezone, timedelta

_logger = logging.getLogger(__name__)

class TrinityPrescriptionInheritNhif(models.Model):
    _inherit = "trinity.prescription"

    P001 = fields.Text(string='P001', copy=False)
    P001_signed = fields.Char(string='P001 Signed Text', default='not signed', copy=False)
    SignedInfo_P001 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_P001_signature = fields.Char(string="SignedInfo signature", copy=False)

    P007 = fields.Text(string='P007', copy=False)
    P007_signed = fields.Char(string='P007 Signed Text', default='not signed', copy=False)
    SignedInfo_P007 = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_P007_signature = fields.Char(string="SignedInfo signature", copy=False)

    P002 = fields.Text(string='P002', copy=False)
    P008 = fields.Text(string='P008', copy=False)

    revokeReason  = fields.Char(string='Причина за анулирането', default='Пациентът няма нужда от лекарството')

    @api.onchange('prescription_basedOn_lrn', 'prescription_basedOn_nrn', 'prescription_lrn', 'response_nrnPrescription', 'response_lrnPrescription', 'response_status', 'prescription_authoredOn', 'prescription_category', 'prescription_isProtocolBased', 'prescription_protocolNumber', 'prescription_protocolDate', 'prescription_rhifNumber', 'prescription_financingSource', 'prescription_dispensationType', 'prescription_allowedRepeatsNumber', 'prescription_supplements', 'prescription_nrnPreValidation', 'group_groupIdentifier', 'medication_sequenceId', 'medication_medicationCode_name', 'medication_medicationCode', 'medication_medicationCode_DisplayValue', 'medication_form_name', 'medication_form', 'medication_priority', 'medication_note', 'medication_icd_code', 'medication_nhifCode_name', 'medication_nhifCode', 'medication_nhifCode_description', 'medication_quantityValue', 'medication_isQuantityByForm', 'medication_isSubstitutionAllowed', 'medication_intakeDuration', 'effectiveDosePeriod_start', 'effectiveDosePeriod_end', 'dosageInstruction_sequence', 'dosageInstruction_asNeeded', 'dosageInstruction_route_name', 'dosageInstruction_route', 'dosageInstruction_doseQuantityValue', 'dosageInstruction_doseQuantityCode_UCUM', 'dosageInstruction_doseQuantityCode_name', 'dosageInstruction_doseQuantityCode', 'dosageInstruction_doseQuantityCode_description', 'dosageInstruction_frequency', 'dosageInstruction_period', 'dosageInstruction_periodUnit_name', 'dosageInstruction_periodUnit', 'dosageInstruction_periodUnit_description', 'dosageInstruction_boundsDuration', 'dosageInstruction_boundsDurationUnit_name', 'dosageInstruction_boundsDurationUnit', 'dosageInstruction_boundsDurationUnit_description_extended', 'dosageInstructions_id', 'dosageInstruction_text', 'dosageInstruction_interpretation', 'subject_identifier', 'subject_identifierType', 'subject_prBookNumber', 'subject_nhifInsuranceNumber', 'subject_birthDate', 'subject_gender', 'subject_age', 'subject_weight', 'subject_given', 'subject_middle', 'subject_family', 'subject_isPregnant', 'subject_isBreastFeeding', 'subject_country', 'subject_county', 'subject_city', 'subject_line', 'subject_postalCode', 'subject_phone', 'subject_email', 'requester_pmi', 'requester_pmiDeputy', 'requester_qualification', 'requester_qualification_nhif', 'requester_role', 'requester_practiceNumber', 'requester_rhifAreaNumber', 'requester_nhifNumber', 'requester_phone', 'requester_email')
    def compute_P001(self):
        for record in self:
            current_datetime_utc = datetime.datetime.now(timezone.utc)
            bulgaria_tz = timezone(timedelta(hours=2))
            current_datetime_local = current_datetime_utc.astimezone(bulgaria_tz)
            timestamp_iso = current_datetime_local.isoformat(timespec='seconds')

            uuid_value = str(uuid.uuid4())

            P001 = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-P001.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.requester_pmi.doctor_id if self.requester_pmi and self.requester_pmi.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="P001"/>
                    <nhis:createdOn value="{timestamp_iso}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:prescription>
                        <nhis:lrn value="{self.prescription_lrn if self.prescription_lrn else ''}"/>
                        <nhis:authoredOn value="{self.prescription_authoredOn.strftime('%Y-%m-%d') if self.prescription_authoredOn else ''}"/>
                        <nhis:category value="{self.prescription_category.key if self.prescription_category else ''}"/>"""

            if record.prescription_category and record.prescription_category.key in ['T2', 'T3']:
                P001 += f"""
                        <nhis:isProtocolBased value="{str(self.prescription_isProtocolBased).lower()}"/>"""
                if record.prescription_isProtocolBased:
                    P001 += f"""
                        <nhis:protocolNumber value="{self.prescription_protocolNumber if self.prescription_protocolNumber else ''}"/>
                        <nhis:protocolDate value="{self.prescription_protocolDate.strftime('%Y-%m-%d') if self.prescription_protocolDate else ''}"/>"""
            else:
                if record.prescription_isProtocolBased:
                    P001 += f"""
                        <nhis:isProtocolBased value="true"/>
                        <nhis:protocolNumber value="{self.prescription_protocolNumber if self.prescription_protocolNumber else ''}"/>
                        <nhis:protocolDate value="{self.prescription_protocolDate.strftime('%Y-%m-%d') if self.prescription_protocolDate else ''}"/>"""

            if record.prescription_financingSource and record.prescription_financingSource.key == '2':
                P001 += f"""
                        <nhis:rhifNumber value="{self.prescription_rhifNumber.key if self.prescription_rhifNumber else '2201'}"/>"""

            if record.prescription_basedOn_nrn:
                P001 += f"""
                        <nhis:basedOn value="{self.prescription_basedOn_nrn}"/>"""

            P001 += f"""
                        <nhis:financingSource value="{self.prescription_financingSource.key if self.prescription_financingSource else ''}"/>"""

            if record.prescription_category and record.prescription_category.key == 'T1':
                P001 += f"""
                        <nhis:dispensationType value="{self.prescription_dispensationType.key if self.prescription_dispensationType else ''}"/>"""

                if record.prescription_dispensationType and record.prescription_dispensationType.key == '2':
                    P001 += f"""
                        <nhis:allowedRepeatsNumber value="{self.prescription_allowedRepeatsNumber if self.prescription_allowedRepeatsNumber else '0'}"/>"""

            if record.prescription_supplements:
                P001 += f"""
                        <nhis:supplements value="{self.prescription_supplements}"/>"""

            if record.prescription_nrnPreValidation:
                P001 += f"""
                        <nhis:nrnPreValidation value="{self.prescription_nrnPreValidation}"/>"""

            P001 += f"""
                        <nhis:group>"""

            if record.prescription_category and record.prescription_category.key == 'T3':
                P001 += f"""
                            <nhis:groupIdentifier value="{self.group_groupIdentifier.key if self.group_groupIdentifier else ''}"/>"""

            P001 += f"""
                            <nhis:medication>
                                <nhis:sequenceId value="{self.medication_sequenceId if self.medication_sequenceId else ''}"/>
                                <nhis:medicationCode value="{self.medication_medicationCode if self.medication_medicationCode else ''}" name="{self.medication_medicationCode_DisplayValue if self.medication_medicationCode_DisplayValue else ''}"/>
                                <nhis:form value="{self.medication_form if self.medication_form else ''}"/>"""

            if record.medication_priority:
                P001 += f"""
                                <nhis:priority value="{self.medication_priority.key}"/>"""

            if record.medication_note:
                P001 += f"""
                                <nhis:note value="{self.medication_note}"/>"""

            if record.prescription_category and record.prescription_category.key in ['T2', 'T3', 'T6', 'T7']:
                P001 += f"""
                                <nhis:mkb value="{self.medication_icd_code.key if self.medication_icd_code else ''}"/>"""
            elif record.medication_icd_code:
                P001 += f"""
                                <nhis:mkb value="{self.medication_icd_code.key}"/>"""

            if record.prescription_financingSource and record.prescription_financingSource.key == '2':
                P001 += f"""
                                <nhis:nhifCode value="{self.medication_nhifCode if self.medication_nhifCode else ''}"/>"""

            P001 += f"""
                                <nhis:quantityValue value="{self.medication_quantityValue if self.medication_quantityValue else ''}"/>
                                <nhis:isQuantityByForm value="{str(self.medication_isQuantityByForm).lower() if self.medication_isQuantityByForm else 'false'}"/>"""

            if record.medication_isSubstitutionAllowed is not None:
                P001 += f"""
                                <nhis:isSubstitutionAllowed value="{str(self.medication_isSubstitutionAllowed).lower()}"/>"""

            if record.prescription_category and record.prescription_category.key in ['T2', 'T3']:
                P001 += f"""
                                <nhis:intakeDuration value="{self.medication_intakeDuration if self.medication_intakeDuration else ''}"/>"""
            elif record.medication_intakeDuration:
                P001 += f"""
                                <nhis:intakeDuration value="{self.medication_intakeDuration}"/>"""

            if record.effectiveDosePeriod_start or record.effectiveDosePeriod_end:
                P001 += f"""
                                <nhis:effectiveDosePeriod>"""
                if record.effectiveDosePeriod_start:
                    P001 += f"""
                                    <nhis:start value="{self.effectiveDosePeriod_start.strftime('%Y-%m-%d')}"/>"""
                if record.effectiveDosePeriod_end:
                    P001 += f"""
                                    <nhis:end value="{self.effectiveDosePeriod_end.strftime('%Y-%m-%d')}"/>"""
                P001 += f"""
                                </nhis:effectiveDosePeriod>"""

            P001 += f"""
                                <nhis:dosageInstruction>"""

            if record.dosageInstruction_sequence:
                P001 += f"""
                                    <nhis:sequence value="{self.dosageInstruction_sequence}"/>"""

            P001 += f"""
                                    <nhis:asNeeded value="{str(self.dosageInstruction_asNeeded).lower() if self.dosageInstruction_asNeeded else 'false'}"/>"""

            if record.dosageInstruction_route:
                P001 += f"""
                                    <nhis:route value="{self.dosageInstruction_route}"/>"""

            P001 += f"""
                                    <nhis:doseQuantityValue value="{self.dosageInstruction_doseQuantityValue if self.dosageInstruction_doseQuantityValue else ''}"/>
                                    <nhis:doseQuantityCode value="{self.dosageInstruction_doseQuantityCode if self.dosageInstruction_doseQuantityCode else ''}"/>
                                    <nhis:frequency value="{self.dosageInstruction_frequency if self.dosageInstruction_frequency else ''}"/>
                                    <nhis:period value="{self.dosageInstruction_period if self.dosageInstruction_period else ''}"/>
                                    <nhis:periodUnit value="{self.dosageInstruction_periodUnit if self.dosageInstruction_periodUnit else ''}"/>"""

            if record.prescription_category and record.prescription_category.key in ['T2', 'T3', 'T6', 'T7']:
                P001 += f"""
                                    <nhis:boundsDuration value="{self.dosageInstruction_boundsDuration if self.dosageInstruction_boundsDuration else ''}"/>
                                    <nhis:boundsDurationUnit value="{self.dosageInstruction_boundsDurationUnit if self.dosageInstruction_boundsDurationUnit else ''}"/>"""
            elif record.dosageInstruction_boundsDuration:
                P001 += f"""
                                    <nhis:boundsDuration value="{self.dosageInstruction_boundsDuration}"/>
                                    <nhis:boundsDurationUnit value="{self.dosageInstruction_boundsDurationUnit if self.dosageInstruction_boundsDurationUnit else ''}"/>"""

            for dosage_when in record.dosageInstructions_id:
                if dosage_when.dosageInstruction_when:
                    P001 += f"""
                                    <nhis:when value="{dosage_when.dosageInstruction_when.key}"/>"""
                    if dosage_when.dosageInstruction_offset:
                        P001 += f"""
                                    <nhis:offset value="{int(dosage_when.dosageInstruction_offset)}"/>"""

            if record.dosageInstruction_text:
                P001 += f"""
                                    <nhis:text value="{self.dosageInstruction_text}"/>"""

            P001 += f"""
                                    <nhis:interpretation value="{self.dosageInstruction_interpretation if self.dosageInstruction_interpretation else ''}"/>
                                </nhis:dosageInstruction>
                            </nhis:medication>
                        </nhis:group>
                    </nhis:prescription>
                    <nhis:subject>
                        <nhis:identifierType value="{self.subject_identifierType.key if self.subject_identifierType else ''}"/>
                        <nhis:identifier value="{self.subject_identifier.identifier if self.subject_identifier and self.subject_identifier.identifier else ''}"/>"""

            if record.subject_nhifInsuranceNumber:
                P001 += f"""
                        <nhis:nhifInsuranceNumber value="{self.subject_nhifInsuranceNumber}"/>"""

            P001 += f"""
                        <nhis:birthDate value="{self.subject_birthDate.strftime('%Y-%m-%d') if self.subject_birthDate else ''}"/>
                        <nhis:gender value="{self.subject_gender.key if self.subject_gender else ''}"/>"""

            if record.subject_prBookNumber:
                P001 += f"""
                        <nhis:prBookNumber value="{self.subject_prBookNumber}"/>"""

            P001 += f"""
                        <nhis:name>
                            <nhis:given value="{self.subject_given if self.subject_given else ''}"/>"""

            if record.subject_middle:
                P001 += f"""
                            <nhis:middle value="{self.subject_middle}"/>"""

            P001 += f"""
                            <nhis:family value="{self.subject_family if self.subject_family else ''}"/>
                        </nhis:name>
                        <nhis:address>
                            <nhis:country value="{self.subject_country.key if self.subject_country else ''}"/>"""

            if record.subject_county:
                P001 += f"""
                            <nhis:county value="{self.subject_county.key}"/>"""

            P001 += f"""
                            <nhis:city value="{self.subject_city if self.subject_city else ''}"/>"""

            if record.subject_line:
                P001 += f"""
                            <nhis:line value="{self.subject_line}"/>"""

            if record.subject_postalCode:
                P001 += f"""
                            <nhis:postalCode value="{self.subject_postalCode}"/>"""

            P001 += f"""
                        </nhis:address>"""

            if record.subject_phone:
                P001 += f"""
                        <nhis:phone value="{self.subject_phone}"/>"""

            if record.subject_email:
                P001 += f"""
                        <nhis:email value="{self.subject_email}"/>"""

            P001 += f"""
                        <nhis:various>
                            <nhis:age value="{int(self.subject_age) if self.subject_age else '0'}"/>"""

            if record.subject_weight:
                P001 += f"""
                            <nhis:weight value="{self.subject_weight}"/>"""

            if record.subject_gender and record.subject_gender.key == '2':
                if record.subject_isPregnant is not None:
                    P001 += f"""
                            <nhis:isPregnant value="{str(self.subject_isPregnant).lower()}"/>"""

            if record.subject_gender and record.subject_gender.key == '2':
                if record.subject_isBreastFeeding is not None:
                    P001 += f"""
                            <nhis:isBreastFeeding value="{str(self.subject_isBreastFeeding).lower()}"/>"""

            P001 += f"""
                        </nhis:various>
                    </nhis:subject>
                    <nhis:requester>
                        <nhis:pmi value="{self.requester_pmi.doctor_id if self.requester_pmi else ''}"/>"""

            if record.requester_role and record.requester_role.key:
                try:
                    if int(record.requester_role.key) > 1:
                        P001 += f"""
                        <nhis:pmiDeputy value="{self.requester_pmiDeputy.doctor_id if self.requester_pmiDeputy else ''}"/>"""
                except (ValueError, TypeError):
                    pass

            if record.prescription_financingSource and record.prescription_financingSource.key == '2':
                P001 += f"""
                        <nhis:qualification value="{self.requester_qualification.key if self.requester_qualification else ''}" nhifCode="{self.requester_qualification_nhif if self.requester_qualification_nhif else ''}"/>"""
            else:
                P001 += f"""
                        <nhis:qualification value="{self.requester_qualification.key if self.requester_qualification else ''}"/>"""

            P001 += f"""
                        <nhis:role value="{self.requester_role.key if self.requester_role else ''}"/>
                        <nhis:practiceNumber value="{self.requester_practiceNumber if self.requester_practiceNumber else ''}"/>"""

            if record.prescription_financingSource and record.prescription_financingSource.key == '2':
                P001 += f"""
                        <nhis:rhifAreaNumber value="{self.requester_rhifAreaNumber.key if self.requester_rhifAreaNumber else ''}"/>"""
            elif record.requester_rhifAreaNumber:
                P001 += f"""
                        <nhis:rhifAreaNumber value="{self.requester_rhifAreaNumber.key}"/>"""

            if record.requester_nhifNumber:
                P001 += f"""
                        <nhis:nhifNumber value="{self.requester_nhifNumber}"/>"""

            P001 += f"""
                        <nhis:phone value="{self.requester_phone if self.requester_phone else '+35924444444'}"/>"""

            if record.requester_email:
                P001 += f"""
                        <nhis:email value="{self.requester_email}"/>"""

            P001 += f"""
                    </nhis:requester>
                </nhis:contents>
            </nhis:message>"""

        P001 = P001.replace("False", "false").replace("True", "true")

        self.P001 = P001
        self.compute_P007()
        self.sign_P001()

    @api.onchange( 'response_nrnPrescription')
    def compute_P007(self):
        for record in self:
            current_datetime = fields.Datetime.now()
            uuid_value = str(uuid.uuid4())
            P007 = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
            <nhis:message xmlns:nhis="https://www.his.bg" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-P007.xsd">
                <nhis:header>
                    <nhis:sender value="1"/>
                    <nhis:senderId value="{self.requester_pmi.doctor_id if self.requester_pmi.doctor_id else ''}"/>
                    <nhis:senderISName value="Supermed 1.0.1"/>
                    <nhis:recipient value="4"/>
                    <nhis:recipientId value="NHIS"/>
                    <nhis:messageId value="{uuid_value}"/>
                    <nhis:messageType value="P007"/>
                    <nhis:createdOn value="{current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"/>
                </nhis:header>
                <nhis:contents>
                    <nhis:nrnPrescription value="{self.response_nrnPrescription if self.response_nrnPrescription else ''}"/>
                    <nhis:revokeReason value="{self.revokeReason  if self.revokeReason  else ''}"/>
                </nhis:contents>
            </nhis:message>"""

        P007 = P007.replace("False", "false").replace("True", "true")

        self.P007 = P007
        self.sign_P007()

    def getSignatureP001(self):
        return

    def getSignatureP007(self):
        return

    def sign_P001(self, field_name='P001', signedinfo='SignedInfo_P001', is_signed='P001_signed', signedinfo_signature='SignedInfo_P001_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def sign_P007(self, field_name='P007', signedinfo='SignedInfo_P007', is_signed='P007_signed', signedinfo_signature='SignedInfo_P007_signature'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    def action_download_P001(self):
        return self.download_file('P001')

    def action_download_P007(self):
        return self.download_file('P007')

    def P001_api_request(self):

        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'P001_api_request')], limit=1)

        if communicator_record:
            field_origin = communicator_record.field_origin
            field_response = communicator_record.field_response
            url = communicator_record.url_value
            lrn_origin_field = communicator_record.lrn_origin_field

            self.make_api_post_request(field_origin, url, field_response, lrn_origin_field)

    def P007_api_request(self):
        communicator_record = self.env['trinity.communicator'].search([('action_name', '=', 'P007_api_request')], limit=1)

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
        nrnPrescription = xml_root.find('.//nhis:nrnPrescription', ns)
        lrnPrescription = xml_root.find('.//nhis:lrn', ns)
        status = xml_root.find('.//nhis:status', ns)
        error_reason = xml_root.find('.//nhis:reason', ns)

        if nrnPrescription is not None and 'value' in nrnPrescription.attrib:
            self.response_nrnPrescription = nrnPrescription.attrib['value']

        if lrnPrescription is not None and 'value' in lrnPrescription.attrib:
            self.response_lrnPrescription = lrnPrescription.attrib['value']

        if status is not None and 'value' in status.attrib:
            status_value = status.attrib['value']
            status_record = self.env['trinity.nomenclature.cl002'].search([('key', '=', status_value)], limit=1)
            if status_record:
                self.response_status = status_record.id
            else:
                _logger.warning(f"Status value '{status_value}' not found in trinity.nomenclature.cl002")

        self.compute_P007()

        if error_reason is not None and 'value' in error_reason.attrib:
            error_message = error_reason.attrib['value']
            raise UserError(error_message)

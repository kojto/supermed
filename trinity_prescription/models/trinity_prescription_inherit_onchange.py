from odoo import api, models
import logging

_logger = logging.getLogger(__name__)

class TrinityPrescriptionInheritOnChange(models.Model):
    _inherit = "trinity.prescription"

    @api.onchange('medication_medicationCode_name')
    def _onchange_medication_medicationCode_name(self):
        if self.medication_medicationCode_name:
            self.medication_form_name = self.env['trinity.nomenclature.cl010'].search([('key', '=', self.medication_medicationCode_name.meta_form_id)], limit=1)
            self.prescription_category = self.medication_medicationCode_name.meta_required_prescription_category if self.medication_medicationCode_name.meta_required_prescription_category else self.env['trinity.nomenclature.cl007'].search([('key', '=', 'T1')], limit=1)

    @api.onchange('prescription_template_name')
    def onchange_prescription_template(self):
        if self.prescription_template_name:
            # Store the template reference before copying
            template = self.prescription_template_name

            # Prescription fields
            self.prescription_category = template.prescription_category if template.prescription_category else self.env['trinity.nomenclature.cl007'].search([('key', '=', 'T1')], limit=1)
            self.prescription_financingSource = template.prescription_financingSource if template.prescription_financingSource else self.env['trinity.nomenclature.cl069'].search([('key', '=', '4')], limit=1)
            self.prescription_dispensationType = template.prescription_dispensationType
            self.prescription_allowedRepeatsNumber = template.prescription_allowedRepeatsNumber
            self.prescription_supplements = template.prescription_supplements

            # Group fields
            self.group_groupIdentifier = template.group_groupIdentifier

            # Medication fields
            self.medication_sequenceId = template.medication_sequenceId
            self.medication_medicationCode_name = template.medication_medicationCode_name
            self.medication_form_name = template.medication_form_name
            self.medication_priority = template.medication_priority
            self.medication_note = template.medication_note
            self.medication_icd_code = template.medication_icd_code
            self.medication_nhifCode_name = template.medication_nhifCode_name
            self.medication_quantityValue = template.medication_quantityValue
            self.medication_isQuantityByForm = template.medication_isQuantityByForm
            self.medication_isSubstitutionAllowed = template.medication_isSubstitutionAllowed
            self.dosageInstruction_boundsDuration = template.dosageInstruction_boundsDuration

            # Dosage instruction fields
            self.dosageInstruction_asNeeded = template.dosageInstruction_asNeeded
            self.dosageInstruction_route_name = template.dosageInstruction_route_name
            self.dosageInstruction_doseQuantityValue = template.dosageInstruction_doseQuantityValue
            self.dosageInstruction_doseQuantityCode_UCUM = template.dosageInstruction_doseQuantityCode_UCUM
            self.dosageInstruction_doseQuantityCode_name = template.dosageInstruction_doseQuantityCode_name
            self.dosageInstruction_frequency = template.dosageInstruction_frequency
            self.dosageInstruction_period = template.dosageInstruction_period
            self.dosageInstruction_periodUnit_name = template.dosageInstruction_periodUnit_name
            self.dosageInstruction_boundsDuration = template.dosageInstruction_boundsDuration
            self.dosageInstruction_boundsDurationUnit_name = template.dosageInstruction_boundsDurationUnit_name
            self.dosageInstruction_text = template.dosageInstruction_text

            # One2many field - copy the related records
            dosage_instructions = []
            for instruction in template.dosageInstructions_id:
                dosage_instructions.append((0, 0, {
                    'dosageInstruction_when': instruction.dosageInstruction_when.id if instruction.dosageInstruction_when else False,
                    'dosageInstruction_offset': instruction.dosageInstruction_offset,
                }))
            self.dosageInstructions_id = dosage_instructions

    @api.onchange('prescription_isProtocolBased')
    def _onchange_isProtocolBased(self):
        if not self.prescription_isProtocolBased:
            self.prescription_protocolNumber = False
            self.prescription_protocolDate = False

    @api.onchange('prescription_financingSource')
    def _onchange_financingSource(self):
        if self.prescription_financingSource and self.prescription_financingSource.key != '2':
            self.prescription_rhifNumber = False
            self.medication_nhifCode_name = False

    @api.onchange('prescription_category')
    def _onchange_prescription_category(self):
        if self.prescription_category:
            if self.prescription_category.key != 'T3':
                if self.prescription_category.key not in ['T2']:
                    self.group_groupIdentifier = False
            if self.prescription_category.key != 'T1':
                self.prescription_dispensationType = False
            if self.prescription_category.key in ['T2', 'T3']:
                nhif_source = self.env['trinity.nomenclature.cl069'].search([('key', '=', '2')], limit=1)
                if nhif_source:
                    self.prescription_financingSource = nhif_source
            if self.prescription_category.key in ['T2', 'T3']:
                day_unit = self.env['trinity.nomenclature.cl020'].search([('key', '=', 'd')], limit=1)
                if day_unit:
                    self.dosageInstruction_periodUnit_name = day_unit
            if self.prescription_category.key in ['T2', 'T3']:
                self.medication_isQuantityByForm = True
            if self.prescription_category.key in ['T2', 'T3', 'T6', 'T7']:
                day_unit = self.env['trinity.nomenclature.cl020'].search([('key', '=', 'd')], limit=1)
                if day_unit:
                    self.dosageInstruction_boundsDurationUnit_name = day_unit

    @api.onchange('requester_role')
    def _onchange_requester_role(self):
        if self.requester_role and self.requester_role.key:
            try:
                if int(self.requester_role.key) <= 1:
                    self.requester_pmiDeputy = False
            except (ValueError, TypeError):
                pass

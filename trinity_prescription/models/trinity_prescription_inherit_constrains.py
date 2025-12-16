from odoo import api, models, _
from odoo.exceptions import ValidationError

class TrinityPrescriptionInheritConstrains(models.Model):
    _inherit = "trinity.prescription"

    def _check_protocol_based_fields(self):
        for record in self:
            if record.prescription_isProtocolBased:
                if not record.prescription_protocolNumber:
                    raise ValidationError(_('CDP02: Номер на протокол е задължителен когато рецептата е базирана на протокол.'))
                if not record.prescription_protocolDate:
                    raise ValidationError(_('CDP03: Дата на протокола е задължителна когато рецептата е базирана на протокол.'))

    def _check_rhif_number(self):
        for record in self:
            if record.prescription_financingSource and record.prescription_financingSource.key == '2':
                if not record.prescription_rhifNumber:
                    raise ValidationError(_('CDP04: РЗОК Номер е задължителен когато източникът на финансиране е НЗОК (код 2).'))

    def _check_country_requirement(self):
        for record in self:
            if record.subject_identifierType and record.subject_identifierType.key in ['2', '3', '4', '5']:
                if not record.subject_country:
                    raise ValidationError(_('CDP06: Държава е задължителна за чуждестранни идентификатори (тип 2, 3, 4 или 5).'))

    def _check_group_identifier(self):
        for record in self:
            if record.prescription_category and record.prescription_category.key == 'T3':
                if not record.group_groupIdentifier:
                    category_desc = record.prescription_category.description or 'T3'
                    raise ValidationError(_('CDP08: Идентификатор на група е задължителен за %s.') % category_desc)

    def _check_icd_code(self):
        for record in self:
            if record.prescription_category and record.prescription_category.key in ['T2', 'T3', 'T6', 'T7']:
                if not record.medication_icd_code:
                    category_keys = ['T2', 'T3', 'T6', 'T7']
                    categories = self.env['trinity.nomenclature.cl007'].search([('key', 'in', category_keys)])
                    category_descriptions = ', '.join([cat.description or cat.key for cat in categories])
                    raise ValidationError(_('CDP11: МКБ код е задължителен за категории %s.') % category_descriptions)

    def _check_dispensation_type(self):
        for record in self:
            if record.prescription_category and record.prescription_category.key == 'T1':
                if not record.prescription_dispensationType:
                    category_desc = record.prescription_category.description or 'T1'
                    raise ValidationError(_('CDP12: Tип на отпускане е задължителен за %s.') % category_desc)

    def _check_nhif_code(self):
        for record in self:
            if record.prescription_financingSource and record.prescription_financingSource.key == '2':
                if not record.medication_nhifCode_name:
                    raise ValidationError(_('CDP16: НЗОК код е задължителен когато източникът на финансиране е НЗОК.'))

    @api.onchange('prescription_dispensationType')
    def _onchange_dispensationType(self):
        if self.prescription_dispensationType and self.prescription_dispensationType.key != '2':
            self.prescription_allowedRepeatsNumber = 0

    def _check_allowed_repeats(self):
        for record in self:
            if (record.prescription_dispensationType and record.prescription_dispensationType.key == '2'
                and record.prescription_category and record.prescription_category.key == 'T1'):
                if not record.prescription_allowedRepeatsNumber:
                    category_desc = record.prescription_category.description or 'T1'
                    raise ValidationError(_('CDP21: Брой разрешени повторения е задължителен за тип отпускане 2 и %s.') % category_desc)

    def _check_bounds_duration(self):
        for record in self:
            if record.prescription_category and record.prescription_category.key in ['T2', 'T3', 'T6', 'T7']:
                if not record.dosageInstruction_boundsDuration:
                    category_keys = ['T2', 'T3', 'T6', 'T7']
                    categories = self.env['trinity.nomenclature.cl007'].search([('key', 'in', category_keys)])
                    category_descriptions = ', '.join([cat.description or cat.key for cat in categories])
                    raise ValidationError(_('CDP24: Продължителност на приема е задължителна за категории %s.') % category_descriptions)
                if not record.dosageInstruction_boundsDurationUnit or record.dosageInstruction_boundsDurationUnit != 'd':
                    category_keys = ['T2', 'T3', 'T6', 'T7']
                    categories = self.env['trinity.nomenclature.cl007'].search([('key', 'in', category_keys)])
                    category_descriptions = ', '.join([cat.description or cat.key for cat in categories])
                    raise ValidationError(_('CDP23: Единица на продължителност трябва да бъде "d" (дни) за категории %s.') % category_descriptions)

    def _check_deputy_practitioner(self):
        for record in self:
            if record.requester_role and record.requester_role.key:
                try:
                    if int(record.requester_role.key) > 1:
                        if not record.requester_pmiDeputy:
                            raise ValidationError(_('CDP26: Заместник лекар е задължителен когато ролята е по-голяма от 1.'))
                except (ValueError, TypeError):
                    pass

    def _check_gender_icd_restrictions(self):
        for record in self:
            if record.subject_gender and record.medication_icd_code:
                icd_code = record.medication_icd_code.key
                if record.subject_gender.key == '1':
                    if icd_code and (icd_code.startswith('E89.4') or icd_code.startswith('N80.')):
                        raise ValidationError(_('CDP30: МКБ кодове E89.4x и N80.xx не са приложими за мъже.'))
                if record.subject_gender.key == '2':
                    if icd_code and icd_code.startswith('N40.'):
                        raise ValidationError(_('CDP31: МКБ код N40.xx не е приложим за жени.'))

    def _check_financing_source_t2_t3(self):
        for record in self:
            if record.prescription_category and record.prescription_category.key in ['T2', 'T3']:
                if not record.prescription_financingSource or record.prescription_financingSource.key != '2':
                    category_keys = ['T2', 'T3']
                    categories = self.env['trinity.nomenclature.cl007'].search([('key', 'in', category_keys)])
                    category_descriptions = ' и '.join([cat.description or cat.key for cat in categories])
                    raise ValidationError(_('CDP32: Източник на финансиране трябва да бъде НЗОК (код 2) за категории %s.') % category_descriptions)

    def _check_rhif_area_number(self):
        for record in self:
            if record.prescription_financingSource and record.prescription_financingSource.key == '2':
                if not record.requester_rhifAreaNumber:
                    raise ValidationError(_('CDP33: РЗОК регион е задължителен когато източникът на финансиране е НЗОК.'))

    def _check_period_unit(self):
        for record in self:
            if record.prescription_category and record.prescription_category.key in ['T2', 'T3']:
                if record.dosageInstruction_periodUnit and record.dosageInstruction_periodUnit != 'd':
                    category_keys = ['T2', 'T3']
                    categories = self.env['trinity.nomenclature.cl007'].search([('key', 'in', category_keys)])
                    category_descriptions = ' и '.join([cat.description or cat.key for cat in categories])
                    raise ValidationError(_('CDP37: Единица на период трябва да бъде "d" (дни) за категории %s.') % category_descriptions)

    def _check_quantity_by_form(self):
        for record in self:
            if record.prescription_category and record.prescription_category.key in ['T2', 'T3']:
                if not record.medication_isQuantityByForm:
                    category_keys = ['T2', 'T3']
                    categories = self.env['trinity.nomenclature.cl007'].search([('key', 'in', category_keys)])
                    category_descriptions = ' и '.join([cat.description or cat.key for cat in categories])
                    raise ValidationError(_('CDP38: Количеството трябва да бъде по лекарствена форма за категории %s.') % category_descriptions)

    def _check_cl115_prescription_type(self):
        for record in self:
            if record.medication_medicationCode_name and record.medication_medicationCode_name.meta_inn_code:
                cl115_match = self.env['trinity.nomenclature.cl115'].search([
                    ('description', '=', record.medication_medicationCode_name.meta_inn_code)
                ], limit=1)
                if cl115_match:
                    if not record.prescription_category or record.prescription_category.key != 'T6':
                        raise ValidationError(_('CDP39: Лекарството се изписва на зелена рецепта!'))

    def _check_cl114_prescription_type(self):
        for record in self:
            if record.medication_medicationCode_name and record.medication_medicationCode_name.meta_inn_code:
                cl114_match = self.env['trinity.nomenclature.cl114'].search([
                    ('description', '=', record.medication_medicationCode_name.meta_inn_code)
                ], limit=1)
                if cl114_match:
                    if not record.prescription_category or record.prescription_category.key != 'T7':
                        raise ValidationError(_('CDP40: Лекарството се изписва на жълта рецепта!'))

    def _collect_validation_errors(self):
        errors = []

        validation_methods = [
            ('_check_protocol_based_fields', 'CDP02/CDP03'),
            ('_check_rhif_number', 'CDP04'),
            ('_check_country_requirement', 'CDP06'),
            ('_check_group_identifier', 'CDP08'),
            ('_check_icd_code', 'CDP11'),
            ('_check_dispensation_type', 'CDP12'),
            ('_check_nhif_code', 'CDP16'),
            ('_check_allowed_repeats', 'CDP21'),
            ('_check_bounds_duration', 'CDP23/CDP24'),
            ('_check_deputy_practitioner', 'CDP26'),
            ('_check_gender_icd_restrictions', 'CDP30/CDP31'),
            ('_check_financing_source_t2_t3', 'CDP32'),
            ('_check_rhif_area_number', 'CDP33'),
            ('_check_period_unit', 'CDP37'),
            ('_check_quantity_by_form', 'CDP38'),
            ('_check_cl115_prescription_type', 'CDP39'),
            ('_check_cl114_prescription_type', 'CDP40'),
        ]

        for method_name, error_code in validation_methods:
            try:
                method = getattr(self, method_name)
                method()
            except ValidationError as e:
                if e.args and isinstance(e.args[0], list):
                    for msg in e.args[0]:
                        errors.append(str(msg))
                else:
                    error_msg = str(e.args[0]) if e.args else str(e)
                    errors.append(error_msg)

        return errors

    def validate_all_prescription_constraints(self):
        errors = self._collect_validation_errors()

        if errors:
            error_html = '<div>'
            error_html += '<h3 class="text-dark mb-3 fw-normal">Намерени са грешки при валидацията:</h3>'
            error_html += '<ul class="list-unstyled">'
            for i, error in enumerate(errors, 1):
                error_html += f'<li class="mb-2 p-2 border-start border-danger rounded" style="border-width: 5px !important;">'
                error_html += f'<span class="text-dark small">{error}</span>'
                error_html += '</li>'
            error_html += '</ul>'
            error_html += '<p class="mt-3 text-dark small">Моля, поправете грешките и опитайте отново.</p>'
            error_html += '</div>'

            wizard = self.env['trinity.prescription.validation.wizard'].create({
                'prescription_id': self.id,
                'error_messages': error_html,
                'error_count': len(errors),
                'is_success': False,
            })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Валидация на рецепта',
                'res_model': 'trinity.prescription.validation.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
                'view_id': self.env.ref('trinity_prescription.view_trinity_prescription_validation_wizard_form').id,
            }
        else:
            success_html = '<div>'
            success_html += '<p class="p-2 border-start border-success rounded text-dark small" style="border-width: 5px !important;">Няма валидационни грешки.</p>'
            success_html += '</div>'

            wizard = self.env['trinity.prescription.validation.wizard'].create({
                'prescription_id': self.id,
                'error_messages': success_html,
                'error_count': 0,
                'is_success': True,
            })

            return {
                'type': 'ir.actions.act_window',
                'name': 'Валидация на рецепта',
                'res_model': 'trinity.prescription.validation.wizard',
                'res_id': wizard.id,
                'view_mode': 'form',
                'target': 'new',
                'view_id': self.env.ref('trinity_prescription.view_trinity_prescription_validation_wizard_form').id,
            }

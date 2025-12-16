
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime
import re

class TrinityPatient(models.Model):
    _name = 'trinity.patient'
    _description = 'Пациенти'
    _rec_name = 'identifier'

    identifier = fields.Char(required=True, string='ЕГН/ЛНЧ/друг №')
    patient_irn = fields.Char(compute='compute_patient_lrn', readonly=True)

    @api.model
    def compute_patient_lrn(self):
        lrn_value = f'PAT-{self.company_vat}-{self.identifier}'
        return lrn_value

    first_name = fields.Char(string='Име', required=True)
    middle_name = fields.Char(string='Презиме')
    last_name = fields.Char(string='Фамилия', required=True)
    patient_full_name = fields.Char(string='Пациент', compute='compute_patient_full_name', store=True)
    mrzString = fields.Char(string='MRZ')
    email = fields.Char(string='Имейл')
    phone = fields.Char(string='Телефон')
    identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип ИД', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    birth_date = fields.Date(string='Дата на раждане', required=True)
    gender = fields.Many2one('trinity.nomenclature.cl001', string='Пол', required=True)
    nationality = fields.Many2one('trinity.nomenclature.cl005', string='Държава', default=lambda self: self.env['trinity.nomenclature.cl005'].search([('key', '=', 'BG')], limit=1), required=True)
    nationality_code = fields.Char(related='nationality.key', string='Код на националност')
    zip_code = fields.Char(string='Пощенски код', default="1000")
    blood_type = fields.Many2one('trinity.nomenclature.cl070', string='Кръвна група')

    address_line = fields.Char(string='Адрес')
    city = fields.Char(string='Град', default="София", required=True)

    country_bulgarian = fields.Many2one('trinity.nomenclature.cl005', string='Държава', default=lambda self: self.env['trinity.nomenclature.cl005'].search([('key', '=', 'BG')], limit=1), required=True)
    county_bulgarian = fields.Many2one('trinity.nomenclature.cl041', string='Област', default=lambda self: self.env['trinity.nomenclature.cl041'].search([('key', '=', 'SOF')], limit=1), required=True)

    ekatte_key = fields.Many2one('trinity.nomenclature.cl044', string='ЕКАТТЕ ключ', default=lambda self: self.env['trinity.nomenclature.cl044'].search([('key', '=', '68134')], limit=1))
    rhifareanumber_key = fields.Many2one('trinity.nomenclature.cl029', string='РЗОК номер', default=lambda self: self.env['trinity.nomenclature.cl029'].search([('key', '=', '2201')], limit=1))
    nhifInsuranceNumber = fields.Char(string='Личен осигурителен №')

    maritalStatus = fields.Many2one('trinity.nomenclature.cl064', string='Семейно положение')
    education = fields.Many2one('trinity.nomenclature.cl065', string='Ниво на образование')
    workplace = fields.Char(string='Работно място')
    profession = fields.Char(string='Професия')

    identificationDocument_number = fields.Char(string='Номер на документ')
    identificationDocument_issueDate = fields.Date(string='Дата на издаване')
    identificationDocument_issuer = fields.Char(string='Издател')
    identificationDocument_nationality = fields.Char(string='Националност')
    identificationDocument_phone = fields.Char(string='Телефон')
    identificationDocument_email = fields.Char(string='Имейл')

    cost_bearer_ids = fields.One2many('trinity.patient.costbearer', 'patient_id', string='Застраховки')
    examination_type_ids = fields.Many2many('trinity.examination.type', string='Разрешени услуги', compute='compute_examination_types')

    general_practitioner_id = fields.Many2one('trinity.medical.facility.doctors.external', string='Личен лекар', ondelete='set null')

    related_contact_id = fields.Many2one('kojto.contacts', string='Свързан контакт', compute='_compute_related_contact_id', store=False)

    def _compute_related_contact_id(self):
        for patient in self:
            patient.related_contact_id = self.env['kojto.contacts'].search([('registration_number', '=', patient.identifier)], limit=1)

    def open_related_contact(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kojto.contacts',
            'view_mode': 'form',
            'res_id': self.related_contact_id.id,
            'target': 'new',
        }

    def create_related_contact(self):
        for patient in self:
            if not patient.identifier:
                raise ValidationError(_('Пациентът трябва да има идентификационен номер'))

            existing_contact = self.env['kojto.contacts'].search([
                ('registration_number', '=', patient.identifier)
            ], limit=1)

            if existing_contact:

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'kojto.contacts',
                    'view_mode': 'form',
                    'res_id': existing_contact.id,
                    'target': 'new',
                }

            contact_data = {
                'registration_number': patient.identifier,
                'name': patient.patient_full_name or f"{patient.first_name} {patient.last_name}",
                'contact_type': 'person',
                'active': True,
            }

            if patient.phone:
                contact_data['phones'] = [(0, 0, {'name': patient.phone})]

            new_contact = self.env['kojto.contacts'].create(contact_data)

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'kojto.contacts',
                'view_mode': 'form',
                'res_id': new_contact.id,
                'target': 'new',
            }

    def compute_examination_types(self):
        for patient in self:
            costbearer_ids = patient.cost_bearer_ids.mapped('cost_bearer_id').ids
            if costbearer_ids:
                domain = [
                    ('active', '=', True),
                    '|',
                    ('cost_bearer_id.financingSource.key', 'in', ['4', '5','6','7','8','9']),
                    ('cost_bearer_id', 'in', costbearer_ids)
                ]
                exam_type_ids = self.env['trinity.examination.type'].search(domain).ids
                patient.examination_type_ids = [(6, 0, exam_type_ids)]
            else:
                domain = [
                    ('active', '=', True),
                    ('cost_bearer_id.financingSource.key', 'in', ['4', '5','6','7','8','9'])
                ]
                exam_type_ids = self.env['trinity.examination.type'].search(domain).ids
                patient.examination_type_ids = [(6, 0, exam_type_ids)]


    def create_nzok_insurance_record(self):
        for patient in self:
            nzok_insurance = self.env['trinity.costbearer'].search([('name', '=', 'НЗОК')], limit=1)

            if nzok_insurance:
                existing_nzok = self.env['trinity.patient.costbearer'].search([
                    ('patient_id', '=', patient.id),
                    ('cost_bearer_id', '=', nzok_insurance.id)
                ], limit=1)

                if not existing_nzok:
                    self.env['trinity.patient.costbearer'].create({
                        'active': True,
                        'active_until': False,
                        'active_from': False,
                        'patient_insurance_no': False,
                        'cost_bearer_id': nzok_insurance.id,
                        'patient_id': patient.id,
                        'patient_insurance_contract_no': False,
                    })

    @api.constrains('identifier')
    def restrict_duplicates(self):
        for rec in self:
            duplicates = self.env['trinity.patient'].search(
                [('identifier', '=', rec.identifier),
                 ('identifier_type', '=', rec.identifier_type),
                 ('id', '!=', rec.id)])
            if duplicates:
                raise ValidationError(
                    _(f'Пациент с {rec.identifier_type.description}: {rec.identifier} вече е регистриран'))

    @api.onchange('first_name', 'middle_name', 'last_name', 'address_line')
    def check_forbidden_characters(self):
        forbidden_fields = {
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'address_line': self.address_line,
        }

        for field, value in forbidden_fields.items():
            if re.search(r'[<>&]', value or ''):
                return {
                    'warning': {
                        'title': _("ГРЕШКА!"),
                        'message': _("Символи <, >, и & не са разрешени в полето %s") % field,
                    }
                }

    @api.depends('first_name', 'middle_name', 'last_name')
    def compute_patient_full_name(self):
        for record in self:
            if record.middle_name:
                full_name = f"{record.first_name} {record.middle_name} {record.last_name}"
            else:
                full_name = f"{record.first_name} {record.last_name}"

            record.patient_full_name = full_name

    def create_report(self):
        report_vals = {
            'patient_identifier_id': self.id,
        }
        report = self.env['trinity.examination'].create(report_vals)

        report.clear_signPen_X_message_fields()
        report.compute_is_patient_signer_default()
        report.compute_previous_e_examination()
        report._compute_hospital_id()

        action = {
            'name': 'Преглед',
            'type': 'ir.actions.act_window',
            'res_model': 'trinity.examination',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'res_id': report.id,
        }
        return action

    def create_kojto_contact_record(self):
        if not self:
            return

        contact_model = self.env['kojto.contacts']
        try:
            language_id = self.env.ref('base.lang_bg').id
        except ValueError:
            language_id = self.env.ref('base.lang_en').id

        created_contacts = self.env['kojto.contacts']
        success_count = 0
        error_count = 0
        total_count = len(self)

        for record in self:
            if not record.identifier or not record.patient_full_name:
                raise ValidationError(f"Missing required fields (identifier or patient_full_name) for record {record.id}")

            kojto_contact = contact_model.search([('registration_number', '=', record.identifier)], limit=1)

            valid_email = None
            if record.email and '@' in record.email and '.' in record.email.split('@')[-1]:
                valid_email = record.email

            contact_data = {
                'registration_number': record.identifier,
                'name': record.patient_full_name,
                'contact_type': 'person',
                'is_non_EU': False,
                'active': True,
                'addresses': [(0, 0, {
                    'address': record.address_line or '',
                    'city': record.city or '',
                    'country_id': self.env.ref('base.bg').id,
                    'language_id': language_id,
                })],
                'emails': [(0, 0, {
                    'name': valid_email,
                })] if valid_email else [],
                'phones': [(0, 0, {
                    'name': record.phone or '',
                })] if record.phone else [],
            }

            try:
                if kojto_contact:
                    existing_addresses = kojto_contact.addresses
                    existing_emails = kojto_contact.emails
                    existing_phones = kojto_contact.phones

                    kojto_contact.write({
                        'registration_number': contact_data['registration_number'],
                        'name': contact_data['name'],
                        'contact_type': contact_data['contact_type'],
                        'is_non_EU': contact_data['is_non_EU'],
                        'active': contact_data['active'],
                    })

                    if existing_addresses:
                        existing_addresses[0].write(contact_data['addresses'][0][2])
                    else:
                        kojto_contact.write({'addresses': contact_data['addresses']})

                    if existing_emails and contact_data['emails']:
                        existing_emails[0].write(contact_data['emails'][0][2])
                    elif contact_data['emails']:
                        kojto_contact.write({'emails': contact_data['emails']})

                    if existing_phones and contact_data['phones']:
                        existing_phones[0].write(contact_data['phones'][0][2])
                    elif contact_data['phones']:
                        kojto_contact.write({'phones': contact_data['phones']})
                else:
                    kojto_contact = contact_model.create(contact_data)

                created_contacts |= kojto_contact
                success_count += 1

            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to create/update contact for {record.patient_full_name}: {str(e)}")
                error_count += 1
                continue

        if success_count > 0 or error_count > 0:
            message = f"Batch processing completed: {success_count} contacts created/updated successfully"
            if error_count > 0:
                message += f", {error_count} failed"
            message += f" out of {total_count} total records."

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Contact Creation Summary',
                    'message': message,
                    'type': 'success' if error_count == 0 else 'warning',
                    'sticky': True,
                }
            }

        return

    def current_hospitalization_fetch(self):
        for patient in self:
            if not patient.identifier:
                continue

            fetch_record = self.env['trinity.hospitalisation.fetch'].search(
                [('user_id', '=', self.env.user.id)],
                limit=1,
                order='id desc'
            )

            if not fetch_record:
                fetch_record = self.env['trinity.hospitalisation.fetch'].create({
                    'user_id': self.env.user.id,
                })
            else:
                fetch_record.fetch_new_hospitalisation()

            update_vals = {
                'fetch_identifier': patient.identifier,
            }

            if patient.identifier_type:
                update_vals['fetch_identifier_type'] = patient.identifier_type.id

            fetch_record.write(update_vals)

            action_id = self.env.ref('trinity_hospitalization.action_trinity_hospitalisation_fetch_form').id
            url = f"/web#id={fetch_record.id}&view_type=form&model=trinity.hospitalisation.fetch&action={action_id}"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'self',
            }


class TrinityPatientCostbearer(models.Model):
    _name = 'trinity.patient.costbearer'
    _description = 'Застраховки'
    _rec_name = 'id'
    _order = 'active_from desc'

    cost_bearer_id = fields.Many2one('trinity.costbearer', string='Контрагент', required=True)
    patient_insurance_no = fields.Char(string='Клиентски №')
    patient_insurance_contract_no = fields.Char(string='Полица №')
    active = fields.Boolean(string='Активна', default=True)
    active_from = fields.Date(string='Активна от')
    active_until = fields.Date(string='Активна до')
    patient_id = fields.Many2one('trinity.patient', string='Пациент', required=True, ondelete='cascade')

    @api.depends('active_from', 'active_until')
    def _compute_is_active(self):
        today = fields.Date.today()
        for record in self:
            is_active = True
            if record.active_from and today < record.active_from:
                is_active = False
            if record.active_until and today > record.active_until:
                is_active = False
            record.active = is_active

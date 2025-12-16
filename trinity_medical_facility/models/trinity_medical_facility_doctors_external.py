
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrinityMedicalFacilityDoctorsExternal(models.Model):
    _name = 'trinity.medical.facility.doctors.external'
    _description = 'Trinity Medical Facility Doctors External'
    _rec_name = 'name'

    name = fields.Char(string='Пълно име', compute='_compute_name', store=True)

    active = fields.Boolean(string='Активен', default=True)
    doctor_id = fields.Char(string='УИН', required=True)

    title = fields.Selection([('г-н', 'г-н'),('г-жа', 'г-жа'),('д-р', 'д-р'),('доц. д-р', 'доц. д-р'),('проф. д-р', 'проф. д-р')], string='Титла', default='д-р', required=True)
    first_name = fields.Char(string='Име', required=True)
    middle_name = fields.Char(string='Бащино име')
    last_name = fields.Char(string='Фамилия', required=True)
    email = fields.Char(string='Имейл')
    phone = fields.Char(string='Телефон')
    identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    identifier = fields.Char(string='Идентификатор')
    hospital_no = fields.Char(string='Номер на болница')
    birth_date = fields.Date(string='Дата на раждане')
    gender = fields.Many2one('trinity.nomenclature.cl001', string='Пол')

    address_line = fields.Char(string='Адрес')
    city = fields.Char(string='Град')
    county_bulgarian = fields.Many2one('trinity.nomenclature.cl041', string='Област')
    county_key = fields.Char(related='county_bulgarian.key', string='Ключ на област')
    country_bulgarian = fields.Many2one('trinity.nomenclature.cl005', string='Държава')
    country_key = fields.Char(related='country_bulgarian.key', string='Ключ на държава')
    ekatte_key = fields.Many2one('trinity.nomenclature.cl044', string='ЕКАТТЕ код')
    ekatte_bulgarian = fields.Char(related='ekatte_key.description', string='ЕКАТТЕ описание')
    zip_code = fields.Char(string='Пощенски код')
    rhifAreaNumber = fields.Char(string='Номер на РЗОК област')
    nhifNumber = fields.Char(string='Номер на НЗОК')

    qualification_code = fields.Many2one('trinity.nomenclature.cl006', string='Код на специалност')
    qualification_code_nhif = fields.Char(related='qualification_code.meta_nhif_code', string='НЗОК код на специалност')
    qualification_name = fields.Char(related='qualification_code.meta_nhif_name', string='Име на специалност')
    description_bg_agent = fields.Text(related='qualification_code.meta_description_bg_agent', string='Описание (Bg_agent)')
    attach = fields.Binary(string='Диплома за лекар')
    attach_char = fields.Char(string="Диплома за лекар")
    attach1 = fields.Binary(string='Диплома за специализация')
    attach_char1 = fields.Char(string="Диплома за специализация")
    attach2 = fields.Binary(string='Свидетелство за членство в лекарски съюз')
    attach_char2 = fields.Char(string="Свидетелство за членство в лекарската колегия")
    attach3 = fields.Binary(string='Договор с МЦ Св. Троица')
    attach_char3 = fields.Char(string="Договор с МЦ Св. Троица")

    @api.constrains('doctor_id')
    def _restrict_duplicates(self):
        for rec in self:
            duplicates = self.env['trinity.medical.facility.doctors.external'].search(
                [('doctor_id', '=', rec.doctor_id), ('id', '!=', rec.id)])
            if duplicates:
                raise ValidationError(
                    _(f'УИН {rec.doctor_id} вече e регистриран. Моля, въведете уникален УИН.'))

    @api.depends('title', 'first_name', 'last_name', 'description_bg_agent', 'doctor_id')
    def _compute_name(self):
        for record in self:
            name_parts = [f"{record.title or ''} {record.first_name or ''} {record.last_name or ''}".strip()]
            if record.description_bg_agent:
                name_parts.append(f"{record.description_bg_agent}")
            if record.doctor_id:
                name_parts.append(f"УИН {record.doctor_id}")
            record.name = ", ".join(part for part in name_parts if part)

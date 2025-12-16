from odoo import models, fields

class TrinityFormPatientIntake(models.Model):
    _name = 'trinity.form.patient.intake'
    _description = 'Trinity Patient Intake Form'
    _rec_name = 'first_name'

    timestamp = fields.Datetime(string='Клеймо за време', default=fields.Datetime.now, readonly=True)
    consent = fields.Boolean(string='Съгласявам се с политиката за поверителност', default=True, help='Съгласявам се с политиката за поверителност на МЦ "Св. Троица" и приемам електронния пренос на лични данни')

    first_name = fields.Char(string='Име')
    last_name = fields.Char(string='Фамилия')
    identifier_type = fields.Many2one('trinity.nomenclature.cl004', string='Тип идентификатор', default=lambda self: self.env['trinity.nomenclature.cl004'].search([('key', '=', 1)], limit=1))
    identifier = fields.Char(string='ЕГН/ЛНЧ/друг')
    birth_date = fields.Date(string='Дата на раждане')

    phone = fields.Char(string='Телефон за контакт')
    email = fields.Char(string='Имейл')
    appointment_date = fields.Date(string='На коя дата имате преглед?')
    main_dr_performing = fields.Char(string='При кой лекар имате преглед?')
    visit_type = fields.Selection([('primary', 'Първичен'), ('secondary', 'Вторичен')], string='Прегледът е')

    complaints = fields.Text(string='Моля, опишете Вашите оплаквания!')
    tests_performed = fields.Text(string='Моля, опишете изследванията, които сте правили и от коя дата са!')
    medications = fields.Text(string='Моля, опишете всички лекарства, които приемате!')
    allergy_details = fields.Text(string='Моля, опишете Вашите алергии!')
    oncological_disease_details = fields.Text(string='Имате/имали ли сте онкологично заболяване?')
    autoimmune_disease_details = fields.Text(string='Имате/имали ли сте автоимунно заболяване?')
    implants_details = fields.Text(string='Поставяни ли са Ви импланти (напр. пейсмейкър, изкуствена става, стент)?')

    medical_history = fields.Text(string='Анамнеза')
    objective_condition = fields.Text(string='Обективно състояние')
    assessment_notes = fields.Text(string='Изследвания')
    therapy_note = fields.Text(string='Терапия')

    attached_pdf_ids = fields.Many2many('ir.attachment', 'intake_attachment_rel', 'intake_id', 'attachment_id', string='Прикачени PDF документи')

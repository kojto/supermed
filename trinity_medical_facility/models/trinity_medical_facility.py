from odoo import models, fields, api, _
import base64

class TrinityMedicalFacility(models.Model):
    _name = 'trinity.medical.facility'
    _description = 'Trinity Medical Facility'
    _rec_name = 'hospital_no'

    hospital_id = fields.Many2one('res.company', string='ЛЗ')

    active = fields.Boolean(default=True)

    hospital_no = fields.Char('№ на ЛЗ')
    managing_director = fields.Char('МОЛ')

    nhif_contract_no = fields.Char('№ на дог. НЗОК')
    nhif_contract_date = fields.Date('Дата на дог. НЗОК')
    nhif_Number = fields.Char(string='Номер в НЗОК')

    nhif_area_code = fields.Many2one('trinity.nomenclature.cl015', string='РЗОК номер на област', default=lambda self: self.env['trinity.nomenclature.cl015'].search([('key', '=', '22')], limit=1), help='Код на получателя на фактурата (CL015)')

    legal_form = fields.Selection([
        ('ЕООД', 'ЕООД - Еднолично дружество с ограничена отговорност'),
        ('ООД', 'ООД - Дружество с ограничена отговорност'),
        ('АД', 'АД - Акционерно дружество'),
        ('АДС', 'АДС - Акционерно дружество с един акционер'),
        ('ЕТ', 'ЕТ - Едноличен търговец'),
        ('СД', 'СД - Събирателно дружество'),
        ('КД', 'КД - Командитно дружество'),
        ('КДА', 'КДА - Командитно дружество с акции')
    ], string='Правна форма', default='ЕООД', help='Правна форма на фирмата')

    IBAN_no = fields.Many2one('kojto.base.bank.accounts', string='Основна банкова сметка', domain="[('contact_id', '=', related_contact_id)]")
    bic_code = fields.Char(related='IBAN_no.BIC', string='BIC код', store=True)
    bank_name = fields.Char(related='IBAN_no.bank_id.name', string='Банка', store=True)

    related_contact_id = fields.Many2one('kojto.contacts', string='Свързан контакт')

    logo = fields.Binary('Лого')
    logo_filename = fields.Char('Име на лого')

    inpatient_hospital_type_cl084 = fields.Many2one('trinity.nomenclature.cl084', string='Тип ЛЗ за болнична помощ')
    inpatient_hospital_subtype_cl085 = fields.Many2one('trinity.nomenclature.cl085', string='Вид ЛЗ за болнична помощ')
    outpatient_hospital_type_cl086 = fields.Many2one('trinity.nomenclature.cl086', string='Тип ЛЗ за извънболнична помощ')
    outpatient_hospital_subtype_cl087 = fields.Many2one('trinity.nomenclature.cl087', string='Вид ЛЗ за извънболнична помощ')

    ai_external_provider = fields.Selection([
        ('xai', 'XAI'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google'),
        ('azure', 'Azure'),
        ('other', 'Other')
    ], string='AI Provider', default='openai')

    ai_external_model = fields.Char(string='AI Model', default='grok-4-latest')
    ai_external_api_key = fields.Char(string='AI API Key', default='xai-8KFmsSlBLQG9Ge9IokX56fiXBB8aWa8BiwH1AMRJ12cDadGqGYluZOJVaIzYd97ZHI83VdVGpaEw0G0L')
    ai_external_api_url = fields.Char(string='AI API URL', default='https://api.x.ai/v1/chat/completions')
    ai_external_temperature = fields.Float(string='AI Temperature', default=0.3)
    ai_external_top_p = fields.Float(string='AI Top P', default=0.9)
    ai_external_max_tokens = fields.Integer(string='AI Max Tokens', default=1000)
    ai_external_api_timeout = fields.Integer(string='AI API Timeout', default=60)
    ai_external_api_retries = fields.Integer(string='AI API Retries', default=3)

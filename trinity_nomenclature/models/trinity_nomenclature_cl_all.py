from odoo import models, fields, api, _
from odoo.fields import Date
from datetime import timedelta, date

import pandas as pd
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TrinityNomenclatureCl001(models.Model):
    _name = 'trinity.nomenclature.cl001'
    _description = 'CL001 - Пол'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')

class TrinityNomenclatureCl002(models.Model):
    _name = 'trinity.nomenclature.cl002'
    _description = 'CL002 - Статус на рецепта'
    _rec_name = 'description'
    _order = 'key'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl003(models.Model):
    _name = 'trinity.nomenclature.cl003'
    _description = 'CL003 - Статус на Е-направление'
    _rec_name = 'description'
    _order = 'key'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl004(models.Model):
    _name = 'trinity.nomenclature.cl004'
    _description = 'CL004 - Тип на идентификатор'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl005(models.Model):
    _name = 'trinity.nomenclature.cl005'
    _description = 'CL005 - Код на държава - ISO 3166 alpha-2'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl006(models.Model):
    _name = 'trinity.nomenclature.cl006'
    _description = 'CL006 - Код на специалност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_description_bg_agent = fields.Text(string='Описание (bg_agent)')
    meta_role = fields.Char(string='Role in Healthcare')
    meta_nhif_code = fields.Char(string='НЗОК код')
    meta_nhif_name = fields.Char(string='НЗОК специалност')
    meta_clinical_speciality = fields.Char(string='Clinical Speciality')

class TrinityNomenclatureCl007(models.Model):
    _name = 'trinity.nomenclature.cl007'
    _description = 'CL007 - Тип на рецепта'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_nhif_document = fields.Char(string='NHIF Document')
    meta_description = fields.Char(string='Description')

class TrinityNomenclatureCl008(models.Model):
    _name = 'trinity.nomenclature.cl008'
    _description = 'CL008 - Начин на отпускане на рецепта (бяла)'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl009(models.Model):
    _name = 'trinity.nomenclature.cl009'
    _description = 'CL009 - Код на медикамент от регистрите на НСЦРЛП'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_inn_code = fields.Char(string='Активна субстанция')
    meta_inn = fields.Char(string='INN код')
    meta_atc = fields.Char(string='ATC')
    meta_form = fields.Char(string='Форма')
    meta_form_bg = fields.Char(string='Форма BG')
    meta_form_id = fields.Char(string='Код на лекарствената форма')
    meta_package = fields.Char(string='Пакет')
    meta_permit_owner = fields.Char(string='Собственик на разрешение')
    meta_permit_number = fields.Char(string='Номер на разрешение')
    meta_is_narcotic = fields.Boolean(string='Е наркотик')
    meta_required_prescription_category = fields.Many2one('trinity.nomenclature.cl007', string='Вид на рецепта', compute='_compute_required_prescription_category', store=True)
    meta_units = fields.Char(string='Мерни единици')
    meta_quantity = fields.Char(string='Количество')
    meta_full_title = fields.Char(string='Пълно заглавие')
    meta_updated_on = fields.Char(string='Обновено на')
    meta_status = fields.Char(string='Статус')

    @api.depends('meta_inn_code')
    def _compute_required_prescription_category(self):
        for record in self:
            cl115_match = self.env['trinity.nomenclature.cl115'].search([('description', '=', record.meta_inn_code)], limit=1)
            cl114_match = self.env['trinity.nomenclature.cl114'].search([('description', '=', record.meta_inn_code)], limit=1)

            if cl115_match:
                record.meta_required_prescription_category = self.env['trinity.nomenclature.cl007'].search([('description', '=', 'Рецепта - зелена')], limit=1)
            elif cl114_match:
                record.meta_required_prescription_category = self.env['trinity.nomenclature.cl007'].search([('description', '=', 'Рецепта - жълта')], limit=1)
            else:
                record.meta_required_prescription_category = False

class TrinityNomenclatureCl010(models.Model):
    _name = 'trinity.nomenclature.cl010'
    _description = 'CL010 - Лекарствена форма'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclaturecl011(models.Model):
    _name = 'trinity.nomenclature.cl011'
    _description = 'CL011 - МКБ код на заболяване'
    _rec_name = 'name'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_reportable = fields.Boolean(string='Reportable', default=False)
    meta_rare = fields.Boolean(string='Rare', default=False)
    meta_cancer = fields.Boolean(string='Cancer', default=False)
    meta_diabetes = fields.Boolean(string='Diabetes', default=False)
    meta_mental = fields.Boolean(string='Mental', default=False)
    meta_contagious = fields.Many2one('trinity.nomenclature.cl148', string='Contagious', ondelete='set null')

class TrinityNomenclatureCl012(models.Model):
    _name = 'trinity.nomenclature.cl012'
    _description = 'CL012 - Видове наблюдения при оценка на резултат от дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_note = fields.Text(string='Note')

class TrinityNomenclatureCl013(models.Model):
    _name = 'trinity.nomenclature.cl013'
    _description = 'CL013 - Път на въвеждане на медикамент'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl014(models.Model):
    _name = 'trinity.nomenclature.cl014'
    _description = 'CL014 - Тип на Е-направление'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_nhif_document = fields.Char(string='NHIF Document')
    meta_usage_instructions = fields.Text(string='Usage Instructions')

class TrinityNomenclatureCl015(models.Model):
    _name = 'trinity.nomenclature.cl015'
    _description = 'CL015 - РЗОК номер на област'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl016(models.Model):
    _name = 'trinity.nomenclature.cl016'
    _description = 'CL016 - Код на заместване на медикамент'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_usage_instructions = fields.Text(string='Usage Instructions')

class TrinityNomenclatureCl017(models.Model):
    _name = 'trinity.nomenclature.cl017'
    _description = 'CL017 - Код на районна фармацевтична колегия'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl018(models.Model):
    _name = 'trinity.nomenclature.cl018'
    _description = 'CL018 - Тип на изпращач или получател на НЗИС съобщение'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_organization_bg = fields.Char(string='Organization BG')
    meta_organization_en = fields.Char(string='Organization EN')

class TrinityNomenclatureCl019(models.Model):
    _name = 'trinity.nomenclature.cl019'
    _description = 'CL019 - Отрязък на рецептурна бланка'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl020(models.Model):
    _name = 'trinity.nomenclature.cl020'
    _description = 'CL020 - Мерна единица за времеви период'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_plural_descriptionbg = fields.Char(string='Множествена форма')

class TrinityNomenclatureCl021(models.Model):
    _name = 'trinity.nomenclature.cl021'
    _description = 'CL021 - Повод за издаване на направление по НЗОК'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_nhif_mapping = fields.Char(string='NHIF Mapping')

class TrinityNomenclatureCl022(models.Model):
    _name = 'trinity.nomenclature.cl022'
    _description = 'CL022 - Mедико-диагностична дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_achi_chapter = fields.Char(string='ACHI Chapter')
    meta_achi_block = fields.Char(string='ACHI Block')
    meta_achi_code = fields.Char(string='ACHI Code')
    meta_nhif_code = fields.Char(string='НЗОК код')
    meta_nhif_package = fields.Char(string='NHIF Package')

    prices_ids = fields.Many2many('trinity.nomenclature.cl022.prices', 'cl022_prices_rel', string='Цени', compute='_compute_prices', store=True)
    price = fields.Float(string='Цена', compute='_compute_highest_price', store=True)

    @api.depends('meta_nhif_code')
    def _compute_prices(self):
        for record in self:
            if record.meta_nhif_code:
                record.prices_ids = self.env['trinity.nomenclature.cl022.prices'].search([
                    ('code', '=', record.meta_nhif_code)
                ])
            else:
                record.prices_ids = self.env['trinity.nomenclature.cl022.prices'].browse()

    @api.depends('prices_ids.price')
    def _compute_highest_price(self):
        for record in self:
            record.price = max(record.prices_ids.mapped('price')) if record.prices_ids else 0

class TrinityNomenclatureCl022prices(models.Model):
    _name = 'trinity.nomenclature.cl022.prices'
    _description = 'CL022 - цени'
    _rec_name = 'code'
    _order = 'code asc'

    code = fields.Char(string='Код', required=True)
    description = fields.Char(string='Описание')
    volume = fields.Integer(string='Обем')
    price = fields.Float(string='Цена', required=True)
    active_from = fields.Date(string='Активна от', required=True)
    currency_id = fields.Many2one('res.currency', string='Валута', required=True, default=lambda self: self.env.company.currency_id if self.env.company else None)

    active = fields.Boolean(string='Активна', compute='_compute_active', store=True)

    @api.depends('active_from', 'code')
    def _compute_active(self):
        today = date.today()
        for record in self:
            if not record.active_from:
                record.active = False
                continue
            later_record_exists = self.search([
                ('code', '=', record.code),
                ('active_from', '>', record.active_from)
            ], limit=1)
            record.active = today >= record.active_from and not later_record_exists.exists()

    @api.model
    def create(self, vals):
        record = super().create(vals)
        cl022_records = self.env['trinity.nomenclature.cl022'].search([
            ('meta_nhif_code', '=', record.code)
        ])
        if cl022_records:
            cl022_records._compute_prices()
        return record

class TrinityNomenclatureCl023(models.Model):
    _name = 'trinity.nomenclature.cl023'
    _description = 'CL023 - Роля на медицински специалист'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl024(models.Model):
    _name = 'trinity.nomenclature.cl024'
    _description = 'CL024 - Резултат от медико-диагностична дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_cl022_mapping = fields.Char(string='CL022 Mapping')
    meta_loinc = fields.Char(string='LOINC***')
    meta_cl028_mapping = fields.Char(string='CL028 Mapping**')
    meta_cl032_mapping = fields.Char(string='CL032 Mapping**')
    meta_ucum = fields.Char(string='UCUM*')
    meta_old_key = fields.Char(string='Old Key')

class TrinityNomenclatureCl025(models.Model):
    _name = 'trinity.nomenclature.cl025'
    _description = 'CL025 - Метод на получаване на резултат от медико-диагностична дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')

class TrinityNomenclatureCl026(models.Model):
    _name = 'trinity.nomenclature.cl026'
    _description = 'CL026 - Лекарствен продукт по НЗОК'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Описание (EN)')
    meta_way_of_prescribing_code = fields.Char(string='Код на начина на предписване')
    meta_quantity = fields.Char(string='Количество')
    meta_divisible = fields.Char(string='Делимо')
    meta_narcotic = fields.Char(string='Наркотик')
    meta_medical_supply_list_type = fields.Char(string='Тип списък медицински материали')
    meta_flag_to_stop = fields.Char(string='Флаг за спиране')
    meta_prescription_type = fields.Char(string='Тип рецепта')
    meta_target_disease = fields.Char(string='Целева болест')
    meta_completely_paid = fields.Char(string='Напълно платено')
    meta_cl009 = fields.Char(string='CL009')
    meta_mkbage = fields.Char(string='МКБ възраст')
    meta_target_disease_all = fields.Char(string='Всички целеви болести')

class TrinityNomenclatureCl027(models.Model):
    _name = 'trinity.nomenclature.cl027'
    _description = 'CL027 - Приоритет за изпълнение'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_latin = fields.Char(string='Latin')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')

class TrinityNomenclatureCl028(models.Model):
    _name = 'trinity.nomenclature.cl028'
    _description = 'CL028 - Скала на стойност на резултат'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_note = fields.Text(string='Note')

class TrinityNomenclatureCl029(models.Model):
    _name = 'trinity.nomenclature.cl029'
    _description = 'CL029 - РЗОК номер на област и здравен район'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl030(models.Model):
    _name = 'trinity.nomenclature.cl030'
    _description = 'CL030 - Стойност в номенклатура на резултат от наблюдение'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_cl032_mapping = fields.Char(string='CL032 Mapping')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_snomed = fields.Char(string='SNOMED')

class TrinityNomenclatureCl031(models.Model):
    _name = 'trinity.nomenclature.cl031'
    _description = 'CL031 - Код на лекарство от регистрите на НСЦРЛП'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

class TrinityNomenclatureCl032(models.Model):
    _name = 'trinity.nomenclature.cl032'
    _description = 'CL032 - Тип номенклатура на резултат от наблюдение'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl033(models.Model):
    _name = 'trinity.nomenclature.cl033'
    _description = 'CL033 - Статус на медико-диагностична дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')

class TrinityNomenclatureCl034(models.Model):
    _name = 'trinity.nomenclature.cl034'
    _description = 'CL034 - Време за приемане на медикамент'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_offset_allowed = fields.Boolean(string='Offset Allowed')
    meta_instructions = fields.Text(string='Instructions')

class TrinityNomenclatureCl035(models.Model):
    _name = 'trinity.nomenclature.cl035'
    _description = 'CL035 - Форма на дозировка'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl036(models.Model):
    _name = 'trinity.nomenclature.cl036'
    _description = 'CL036 - Код на лекарство от регистрите на НСЦРЛП'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

class TrinityNomenclatureCl037(models.Model):
    _name = 'trinity.nomenclature.cl037'
    _description = 'CL037 - Код на ваксина'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_medicament_details = fields.Text(string='Medicament Details')
    meta_atc = fields.Char(string='ATC')
    meta_inn = fields.Char(string='INN')
    meta_target_disease = fields.Char(string='Target Disease')
    meta_vaccine_group = fields.Char(string='Vaccine Group')
    meta_dose_quantity_ml = fields.Char(string='Dose Quantity (ml)')
    meta_number_of_doses = fields.Char(string='Number of Doses')
    meta_days_to_next_dose = fields.Char(string='Days to Next Dose')
    meta_permit_number = fields.Char(string='Permit Number')
    meta_permit_owner_id = fields.Char(string='Permit Owner ID')
    meta_permit_owner_name = fields.Char(string='Permit Owner Name')
    meta_mh_code = fields.Char(string='MH code')

class TrinityNomenclatureCl038(models.Model):
    _name = 'trinity.nomenclature.cl038'
    _description = 'CL038 - Планова имунизация или реимунизация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display value BG')
    meta_display_value_en = fields.Char(string='Display value EN')
    meta_display_transfered_data_bg = fields.Char(string='Display transfered data BG')
    meta_display_transfered_data_en = fields.Char(string='Display transfered data EN')
    meta_program_group = fields.Char(string='Program Group')
    meta_dose_number = fields.Char(string='Dose Number')
    meta_cl082_mapping = fields.Char(string='CL082 Mapping')
    meta_min_age = fields.Char(string='Min age')
    meta_max_age = fields.Char(string='Max age**')
    meta_rules = fields.Text(string='Rules')
    meta_vaccine_additional_info = fields.Text(string='Vaccine additional info')
    meta_cl037_mapping_2023 = fields.Char(string='CL037 Mapping (2023)')
    meta_cl037_mapping_2024 = fields.Char(string='CL037 Mapping (2024)')

class TrinityNomenclatureCl039(models.Model):
    _name = 'trinity.nomenclature.cl039'
    _description = 'CL039 - Статус на Е-имунизация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl040(models.Model):
    _name = 'trinity.nomenclature.cl040'
    _description = 'CL040 - Предприети действия относно подозиран лекарствен продукт'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl041(models.Model):
    _name = 'trinity.nomenclature.cl041'
    _description = 'CL041 - Код на област'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl042(models.Model):
    _name = 'trinity.nomenclature.cl042'
    _description = 'CL042 - Социална група'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl043(models.Model):
    _name = 'trinity.nomenclature.cl043'
    _description = 'CL043 - Статус на лице за имунизация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl044(models.Model):
    _name = 'trinity.nomenclature.cl044'
    _description = 'CL044 - ЕКАТТЕ'
    _rec_name = 'description'
    _order = 'key'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl045(models.Model):
    _name = 'trinity.nomenclature.cl045'
    _description = 'CL045 - Част от тялото за администриране на лекарство'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl046(models.Model):
    _name = 'trinity.nomenclature.cl046'
    _description = 'CL046 - Път на навлизане на лекарство в тялото'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl047(models.Model):
    _name = 'trinity.nomenclature.cl047'
    _description = 'CL047 - Причина за посещение при лекар'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_nhif_mapping = fields.Char(string='NHIF Mapping')

class TrinityNomenclatureCl049(models.Model):
    _name = 'trinity.nomenclature.cl049'
    _description = 'CL049 - Класификация на преглед'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl050(models.Model):
    _name = 'trinity.nomenclature.cl050'
    _description = 'CL050 - Код на високо-специализирана дейност по НЗОК'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_type = fields.Char(string='Type')
    meta_achi_chapter = fields.Char(string='ACHI Chapter')
    meta_achi_block = fields.Char(string='ACHI Block')
    meta_achi_code = fields.Char(string='ACHI Code')
    meta_nhif_code = fields.Char(string='НЗОК код')
    meta_cl006 = fields.Char(string='CL006')
    meta_cl048 = fields.Char(string='CL048')
    meta_fhir = fields.Char(string='FHIR')

    prices_ids = fields.Many2many('trinity.nomenclature.cl050.prices', 'cl050_prices_rel', string='Цени', compute='_compute_prices', store=True)
    price = fields.Float(string='Цена', compute='_compute_highest_price', store=True)

    @api.depends('key', 'name')
    def _compute_prices(self):
        for record in self:
            if record.key or record.name:
                record.prices_ids = self.env['trinity.nomenclature.cl050.prices'].search([
                    ('code', '=', record.key)
                ])
            else:
                record.prices_ids = self.env['trinity.nomenclature.cl050.prices'].browse()

    @api.depends('prices_ids.price')
    def _compute_highest_price(self):
        for record in self:
            record.price = max(record.prices_ids.mapped('price')) if record.prices_ids else 0

class TrinityNomenclatureCl050prices(models.Model):
    _name = 'trinity.nomenclature.cl050.prices'
    _description = 'CL050 - цени'
    _rec_name = 'code'
    _order = 'code asc'

    code = fields.Char(string='Код', required=True)
    description = fields.Char(string='Описание')
    volume = fields.Integer(string='Обем')
    price = fields.Float(string='Цена', required=True)
    active_from = fields.Date(string='Активна от', required=True)
    currency_id = fields.Many2one('res.currency', string='Валута', required=True, default=lambda self: self.env.company.currency_id if self.env.company else None)

    active = fields.Boolean(string='Активна', compute='_compute_active', store=True)

    @api.depends('active_from', 'code')
    def _compute_active(self):
        today = date.today()
        for record in self:
            if not record.active_from:
                record.active = False
                continue
            later_record_exists = self.search([
                ('code', '=', record.code),
                ('active_from', '>', record.active_from)
            ], limit=1)
            record.active = today >= record.active_from and not later_record_exists.exists()

    @api.model
    def create(self, vals):
        record = super().create(vals)
        cl050_records = self.env['trinity.nomenclature.cl050'].search([
            '|', ('key', '=', record.code), ('name', 'ilike', record.code)
        ])
        if cl050_records:
            cl050_records._compute_prices()
        return record

class TrinityNomenclatureCl051(models.Model):
    _name = 'trinity.nomenclature.cl051'
    _description = 'CL051 - Вид на преглед за медицинска експертиза по НЗОК'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']


class TrinityNomenclatureCl052(models.Model):
    _name = 'trinity.nomenclature.cl052'
    _description = 'CL052 - Причина за издаване на направление за ТЕЛК'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_instructions = fields.Text(string='Instructions')

class TrinityNomenclatureCl053(models.Model):
    _name = 'trinity.nomenclature.cl053'
    _description = 'CL053 - Тип адрес'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl054(models.Model):
    _name = 'trinity.nomenclature.cl054'
    _description = 'CL054 - Специални медицински дейности - МКБ 9'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl055(models.Model):
    _name = 'trinity.nomenclature.cl055'
    _description = 'CL055 - Статус на преглед'
    _rec_name = 'description'
    _order = 'key'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl056(models.Model):
    _name = 'trinity.nomenclature.cl056'
    _description = 'CL056 - Медицински инструмент'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_type = fields.Char(string='Тип')
    meta_test_type = fields.Char(string='Тип тест')
    meta_manifacturer = fields.Char(string='Производител')
    meta_cl058 = fields.Char(string='CL058')

class TrinityNomenclatureCl057(models.Model):
    _name = 'trinity.nomenclature.cl057'
    _description = 'CL057 - Тип на медицински инструмент'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl058(models.Model):
    _name = 'trinity.nomenclature.cl058'
    _description = 'CL058 - Производител на медицински инструмент'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_country = fields.Char(string='Country')
    meta_website = fields.Char(string='Website')
    meta_dgc_approved = fields.Char(string='DGC Approved')
    meta_bg_approved = fields.Char(string='BG Approved')

class TrinityNomenclatureCl059(models.Model):
    _name = 'trinity.nomenclature.cl059'
    _description = 'CL059 - Тип на прием за хоспитализация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl060(models.Model):
    _name = 'trinity.nomenclature.cl060'
    _description = 'CL060 - Насочваща институция'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl061(models.Model):
    _name = 'trinity.nomenclature.cl061'
    _description = 'CL061 - Причина за хоспитализация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl062(models.Model):
    _name = 'trinity.nomenclature.cl062'
    _description = 'CL062 - Клинични пътеки'
    _rec_name = 'name'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

    prices_ids = fields.Many2many('trinity.nomenclature.cl062.prices', 'cl062_prices_rel', string='Цени', compute='_compute_prices', store=True)
    price = fields.Float(string='Цена', compute='_compute_highest_price', store=True)

    @api.depends('key')
    def _compute_prices(self):
        for record in self:
            if record.key:
                record.prices_ids = self.env['trinity.nomenclature.cl062.prices'].search([
                    ('code', '=', record.key)
                ])
            else:
                record.prices_ids = self.env['trinity.nomenclature.cl062.prices'].browse()

    @api.depends('prices_ids.price')
    def _compute_highest_price(self):
        for record in self:
            record.price = max(record.prices_ids.mapped('price')) if record.prices_ids else 0

class TrinityNomenclatureCl062prices(models.Model):
    _name = 'trinity.nomenclature.cl062.prices'
    _description = 'CL062 - цени'
    _rec_name = 'code'
    _order = 'code asc'

    code = fields.Char(string='Код', required=True)
    description = fields.Char(string='Описание')
    volume = fields.Integer(string='Обем')
    price = fields.Float(string='Цена', required=True)
    active_from = fields.Date(string='Активна от', required=True)
    currency_id = fields.Many2one('res.currency', string='Валута', required=True, default=lambda self: self.env.company.currency_id if self.env.company else None)

    active = fields.Boolean(string='Активна', compute='_compute_active', store=True)

    @api.depends('active_from', 'code')
    def _compute_active(self):
        today = date.today()
        for record in self:
            if not record.active_from:
                record.active = False
                continue
            later_record_exists = self.search([
                ('code', '=', record.code),
                ('active_from', '>', record.active_from)
            ], limit=1)
            record.active = today >= record.active_from and not later_record_exists.exists()

    @api.model
    def create(self, vals):
        record = super().create(vals)
        cl062_records = self.env['trinity.nomenclature.cl062'].search([
            ('key', '=', record.code)
        ])
        if cl062_records:
            cl062_records._compute_prices()
        return record

class TrinityNomenclatureCl063(models.Model):
    _name = 'trinity.nomenclature.cl063'
    _description = 'CL063 - Амбулаторна или клинична процедура'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl064(models.Model):
    _name = 'trinity.nomenclature.cl064'
    _description = 'CL064 - Семейно положение'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl065(models.Model):
    _name = 'trinity.nomenclature.cl065'
    _description = 'CL065 - Образование'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl066(models.Model):
    _name = 'trinity.nomenclature.cl066'
    _description = 'CL066 - Степен на тежест на състоянието'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl067(models.Model):
    _name = 'trinity.nomenclature.cl067'
    _description = 'CL067 - Времеви интервал от медицинско събитие'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_applicable = fields.Char(string='Applicable')

class TrinityNomenclatureCl068(models.Model):
    _name = 'trinity.nomenclature.cl068'
    _description = 'CL068'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl069(models.Model):
    _name = 'trinity.nomenclature.cl069'
    _description = 'CL069 - Източник на финансиране'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl070(models.Model):
    _name = 'trinity.nomenclature.cl070'
    _description = 'CL070 - Кръвна група'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl071(models.Model):
    _name = 'trinity.nomenclature.cl071'
    _description = 'CL071 - Тип на алергична реакция'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl072(models.Model):
    _name = 'trinity.nomenclature.cl072'
    _description = 'CL072 - Категория на алергична реакция'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl073(models.Model):
    _name = 'trinity.nomenclature.cl073'
    _description = 'CL073 - Критичност на алергична реакция'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl074(models.Model):
    _name = 'trinity.nomenclature.cl074'
    _description = 'CL074 - Статус на Е-Хоспитализация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl075(models.Model):
    _name = 'trinity.nomenclature.cl075'
    _description = 'CL075 - Резултат от хоспитализация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl076(models.Model):
    _name = 'trinity.nomenclature.cl076'
    _description = 'CL076 - Роля на диагноза'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')

class TrinityNomenclatureCl077(models.Model):
    _name = 'trinity.nomenclature.cl077'
    _description = 'CL077 - Клиничен статус'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl078(models.Model):
    _name = 'trinity.nomenclature.cl078'
    _description = 'CL078 - Верификационен статус'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')
    meta_orpha_diseases_label_bg = fields.Char(string='Orpha diseases label BG')
    meta_orpha_diseases_label_en = fields.Char(string='Orpha diseases label EN')

class TrinityNomenclatureCl079(models.Model):
    _name = 'trinity.nomenclature.cl079'
    _description = 'CL079 - Режим на хранене'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl080(models.Model):
    _name = 'trinity.nomenclature.cl080'
    _description = 'CL080 - Разпореждане след изписване'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl081(models.Model):
    _name = 'trinity.nomenclature.cl081'
    _description = 'CL081 - Статус на работоспособност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl082(models.Model):
    _name = 'trinity.nomenclature.cl082'
    _description = 'CL082 - Имунизационна програма'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl083(models.Model):
    _name = 'trinity.nomenclature.cl083'
    _description = 'CL083 - Статус на доклад за медико-диагностична дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl084(models.Model):
    _name = 'trinity.nomenclature.cl084'
    _description = 'CL084 - Тип лечебно заведение за извънболнична помощ'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl085(models.Model):
    _name = 'trinity.nomenclature.cl085'
    _description = 'CL085 - Вид лечебно заведение за болнична помощ'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl086(models.Model):
    _name = 'trinity.nomenclature.cl086'
    _description = 'CL086 - Тип лечебно заведение за болнична помощ (коригирано наименование)'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl087(models.Model):
    _name = 'trinity.nomenclature.cl087'
    _description = 'CL087 - Вид лечебно заведение за извънболнична помощ'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl088(models.Model):
    _name = 'trinity.nomenclature.cl088'
    _description = 'CL088 - Резултат от дейност по профилактика'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_units = fields.Char(string='Units')
    meta_cl050_mapping = fields.Char(string='CL50 Mapping')
    meta_cl142_mapping = fields.Char(string='CL142 Mapping')
    meta_cl012_mapping = fields.Char(string='CL012 Mapping')
    meta_cl028_mapping = fields.Char(string='CL028 Mapping')
    meta_cl032_mapping = fields.Char(string='CL032 Mapping')
    meta_cl138_mapping = fields.Char(string='CL138 Mapping')
    meta_requires_text_conclusion = fields.Boolean(string='Requires text conclusion')
    meta_note = fields.Text(string='Note')

class TrinityNomenclatureCl089(models.Model):
    _name = 'trinity.nomenclature.cl089'
    _description = 'CL089 - Етап на хоспитализация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl090(models.Model):
    _name = 'trinity.nomenclature.cl090'
    _description = 'CL090 - Ефект от нежелана лекарствена реакция'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl091(models.Model):
    _name = 'trinity.nomenclature.cl091'
    _description = 'CL091 - Изход от нежелана лекарствена реакция'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl092(models.Model):
    _name = 'trinity.nomenclature.cl092'
    _description = 'CL092 - Зависимост или състояние'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl093(models.Model):
    _name = 'trinity.nomenclature.cl093'
    _description = 'CL093 - Връзка с нежелана лекарствена реакция'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl094(models.Model):
    _name = 'trinity.nomenclature.cl094'
    _description = 'CL094'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl095(models.Model):
    _name = 'trinity.nomenclature.cl095'
    _description = 'CL095 - ACHI Chapter'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl096(models.Model):
    _name = 'trinity.nomenclature.cl096'
    _description = 'CL096 - ACHI Block'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl097(models.Model):
    _name = 'trinity.nomenclature.cl097'
    _description = 'CL097 - Интерпретация на резултати'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl098(models.Model):
    _name = 'trinity.nomenclature.cl098'
    _description = 'CL098 - Тип място на раждане'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl099(models.Model):
    _name = 'trinity.nomenclature.cl099'
    _description = 'CL099 - Начин на раждане'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl100(models.Model):
    _name = 'trinity.nomenclature.cl100'
    _description = 'CL100 - Заключение след преглед за продължаване на лечението'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl101(models.Model):
    _name = 'trinity.nomenclature.cl101'
    _description = 'CL101 - Статус на настаняване в лечебно заведение'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl102(models.Model):
    _name = 'trinity.nomenclature.cl102'
    _description = 'CL102 - Тип е-документ'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl103(models.Model):
    _name = 'trinity.nomenclature.cl103'
    _description = 'CL103 - Родствена връзка'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl104(models.Model):
    _name = 'trinity.nomenclature.cl104'
    _description = 'CL104 - Употреба на тютюн'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_risk_factor = fields.Char(string='Risk factor')

class TrinityNomenclatureCl105(models.Model):
    _name = 'trinity.nomenclature.cl105'
    _description = 'CL105 - Статус на семейна здравна история'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl106(models.Model):
    _name = 'trinity.nomenclature.cl106'
    _description = 'CL106 - Зъбен код'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_tooth_group = fields.Char(string='Tooth Group')
    meta_tooth_type = fields.Char(string='Tooth Type')

class TrinityNomenclatureCl107(models.Model):
    _name = 'trinity.nomenclature.cl107'
    _description = 'CL107 - Код на състояние на зъб'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_nhif_mapping = fields.Char(string='NHIF Mapping')
    meta_nhif_text = fields.Char(string='NHIF Text')
    meta_incompatible_other_codes = fields.Text(string='Incompatible other codes from CL107')
    meta_required_other_codes = fields.Text(string='Required other codes from CL107')

class TrinityNomenclatureCl108(models.Model):
    _name = 'trinity.nomenclature.cl108'
    _description = 'CL108 - Зъбна повърхност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl109(models.Model):
    _name = 'trinity.nomenclature.cl109'
    _description = 'CL109 - Степен на подвижност на зъб'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl110(models.Model):
    _name = 'trinity.nomenclature.cl110'
    _description = 'CL110 - Код на дентална дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_notes = fields.Text(string='Notes')
    meta_cl112_mapping = fields.Char(string='CL112 Mapping')
    meta_nhif_code = fields.Char(string='НЗОК код')

class TrinityNomenclatureCl111(models.Model):
    _name = 'trinity.nomenclature.cl111'
    _description = 'CL111 - Код на дентална диагноза'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_cl011_mapping = fields.Char(string='CL011 Mapping')

class TrinityNomenclatureCl112(models.Model):
    _name = 'trinity.nomenclature.cl112'
    _description = 'CL112 - Тип на дентална дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl113(models.Model):
    _name = 'trinity.nomenclature.cl113'
    _description = 'CL113 - Статус на Е-дентално лечение'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl114(models.Model):
    _name = 'trinity.nomenclature.cl114'
    _description = 'CL114 - Лекарства съдържащи наркотични вещества по жълта рецепта (T7)'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

class TrinityNomenclatureCl115(models.Model):
    _name = 'trinity.nomenclature.cl115'
    _description = 'CL115 - Лекарства съдържащи наркотични вещества по зелена рецепта (T6)'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

class TrinityNomenclatureCl116(models.Model):
    _name = 'trinity.nomenclature.cl116'
    _description = 'CL116 - Причина за издаване на медицинска бележка'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl117(models.Model):
    _name = 'trinity.nomenclature.cl117'
    _description = 'CL117 - Място за провеждане на лечение и възстановяване'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl118(models.Model):
    _name = 'trinity.nomenclature.cl118'
    _description = 'CL118 - Статус за медицинска бележка'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl119(models.Model):
    _name = 'trinity.nomenclature.cl119'
    _description = 'CL119'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl120(models.Model):
    _name = 'trinity.nomenclature.cl120'
    _description = 'CL120 - Производител на устройството, използвано за полагане на подпис на пациента'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl121(models.Model):
    _name = 'trinity.nomenclature.cl121'
    _description = 'CL121 - Модел на устройството, използвано за полагане на подпис на пациента'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')
    meta_cl120_mapping = fields.Char(string='CL120 Mapping')

class TrinityNomenclatureCl122(models.Model):
    _name = 'trinity.nomenclature.cl122'
    _description = 'CL122 - Заболявания за проследяване и диспансеризация'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_cl011_mapping = fields.Char(string='CL011 Mapping')
    meta_main = fields.Boolean(string='Main')
    meta_additional = fields.Boolean(string='Additional')
    meta_min_patient_age = fields.Char(string='Min Patient Age')
    meta_max_patient_age = fields.Char(string='Max Patient Age')
    meta_cl069_mapping = fields.Char(string='CL069 Mapping')

class TrinityNomenclatureCl123(models.Model):
    _name = 'trinity.nomenclature.cl123'
    _description = 'CL123 - Категория за управление на МСП'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl124(models.Model):
    _name = 'trinity.nomenclature.cl124'
    _description = 'CL124 - Статус на удостоверение за здравословно състояние'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl125(models.Model):
    _name = 'trinity.nomenclature.cl125'
    _description = 'CL125 - Тип на удостоверение за здравословно състояние'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl126(models.Model):
    _name = 'trinity.nomenclature.cl126'
    _description = 'CL126 - Групи рискови фактори за развитие на заболяване'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl127(models.Model):
    _name = 'trinity.nomenclature.cl127'
    _description = 'CL127 - Рискови фактори за развитие на заболяване'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_risk_group_definition = fields.Text(string='Risk Group definition')
    meta_cl126 = fields.Char(string='CL126')
    meta_cl011 = fields.Char(string='CL011')
    meta_data_from = fields.Char(string='Data from')

class TrinityNomenclatureCl128(models.Model):
    _name = 'trinity.nomenclature.cl128'
    _description = 'CL128 - Обективен статус с резултат от физикален преглед'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_min_age = fields.Char(string='Min Age')
    meta_max_age = fields.Char(string='Max Age')

class TrinityNomenclatureCl129(models.Model):
    _name = 'trinity.nomenclature.cl129'
    _description = 'CL129 - Пациенски характеристики за личен картон'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_cl088_mapping = fields.Char(string='CL088 Mapping')

class TrinityNomenclatureCl130(models.Model):
    _name = 'trinity.nomenclature.cl130'
    _description = 'CL130 - Видове дейности и поддейности по НЗОК'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_type = fields.Char(string='Type')
    meta_type_short = fields.Char(string='Type short')

class TrinityNomenclatureCl131(models.Model):
    _name = 'trinity.nomenclature.cl131'
    _description = 'CL131 - Статус на попълване на анамнеза'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_fhir_mapping = fields.Char(string='FHIR Mapping')
    meta_notes = fields.Text(string='Notes')

class TrinityNomenclatureCl132(models.Model):
    _name = 'trinity.nomenclature.cl132'
    _description = 'CL132 - График на профилактичните прегледи и дейности'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_cl047_mapping = fields.Char(string='CL047 Mapping')
    meta_cl136_mapping = fields.Char(string='CL136 Mapping')
    meta_cl011_mapping = fields.Char(string='CL011 Mapping')
    meta_event_trigger = fields.Char(string='Event Trigger')
    meta_common_index = fields.Char(string='Common index')
    meta_min_interval_from_common_index = fields.Char(string='Min interval from common index')
    meta_max_interval_from_common_index = fields.Char(string='Max interval from common index')
    meta_age = fields.Char(string='Age')
    meta_max_age = fields.Char(string='Max Age')
    meta_recurring = fields.Boolean(string='Recurring')
    meta_repeat_every_x_years = fields.Char(string='Repeat Every x Years')
    meta_gender = fields.Char(string='Gender')

class TrinityNomenclatureCl133(models.Model):
    _name = 'trinity.nomenclature.cl133'
    _description = 'CL133 - Групи въпроси към прегледи при снемане на анамнеза'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl134(models.Model):
    _name = 'trinity.nomenclature.cl134'
    _description = 'CL134 - Въпроси към прегледи при снемане на анамнеза'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_note = fields.Text(string='Note')
    meta_cl133 = fields.Char(string='CL133')
    meta_multiple_choice = fields.Boolean(string='Multiple Choice')
    meta_cl028 = fields.Char(string='CL028')
    meta_answer_nomenclature = fields.Char(string='Answer Nomenclature')
    meta_ask_once = fields.Boolean(string='Ask once')

class TrinityNomenclatureCl135(models.Model):
    _name = 'trinity.nomenclature.cl135'
    _description = 'CL135 - Код на успешна операция получен от системата на БОВЛ'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl136(models.Model):
    _name = 'trinity.nomenclature.cl136'
    _description = 'CL136 - Видове дейности при профилактични прегледи'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl137(models.Model):
    _name = 'trinity.nomenclature.cl137'
    _description = 'CL137 - Статус на профилактичен преглед или дейност'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl138(models.Model):
    _name = 'trinity.nomenclature.cl138'
    _description = 'CL138 - Групи от допустими отговори при профилактика'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl139(models.Model):
    _name = 'trinity.nomenclature.cl139'
    _description = 'CL139 - Допустими отговори при профилактика'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_cl138_mapping = fields.Char(string='CL138 Mapping')

class TrinityNomenclatureCl140(models.Model):
    _name = 'trinity.nomenclature.cl140'
    _description = 'CL140 - Допустими връзки при контакти в личен картон'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl141(models.Model):
    _name = 'trinity.nomenclature.cl141'
    _description = 'CL141 - Статус на дейност по профилактика'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl142(models.Model):
    _name = 'trinity.nomenclature.cl142'
    _description = 'CL142 - Код на дейност по профилактика'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_description = fields.Char(string='Описание')
    meta_descriptionen = fields.Char(string='Описание (en)')
    meta_achi_chapter = fields.Char(string='ACHI Chapter')
    meta_achi_block = fields.Char(string='ACHI Block')
    meta_achi_code = fields.Char(string='ACHI Code')
    meta_nhif_code = fields.Char(string='НЗОК код')
    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl143(models.Model):
    _name = 'trinity.nomenclature.cl143'
    _description = 'CL143 - Скринингови програми'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_cl022 = fields.Char(string='CL022')
    meta_gender = fields.Char(string='Gender (CL001)')
    meta_cl006 = fields.Char(string='CL006')
    meta_min_age = fields.Char(string='Min age')
    meta_max_age = fields.Char(string='Max age')
    meta_min_interval = fields.Char(string='Min interval')
    meta_start_date = fields.Date(string='Start date')
    meta_end_date = fields.Date(string='End date')
    meta_cl021 = fields.Char(string='CL021')
    meta_cl047 = fields.Char(string='CL047')
    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl144(models.Model):
    _name = 'trinity.nomenclature.cl144'
    _description = 'CL144 - Резултат от дейност по профилактика'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')
    meta_units = fields.Char(string='Units')
    meta_cl142_mapping = fields.Char(string='CL142 Mapping')
    meta_cl012_mapping = fields.Char(string='CL012 Mapping')
    meta_cl028_mapping = fields.Char(string='CL028 Mapping')
    meta_cl138_mapping = fields.Char(string='CL138 Mapping')
    meta_requires_text_conclusion = fields.Boolean(string='Requires text conclusion')
    meta_note = fields.Text(string='Note')

class TrinityNomenclatureCl145(models.Model):
    _name = 'trinity.nomenclature.cl145'
    _description = 'CL145 - Източник на информацията при отговор по въпросник в профилактика'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_bg = fields.Char(string='Display Value BG')
    meta_display_value_en = fields.Char(string='Display Value EN')

class TrinityNomenclatureCl146(models.Model):
    _name = 'trinity.nomenclature.cl146'
    _description = 'CL146 - Статус на отпускане по рецепта'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl147(models.Model):
    _name = 'trinity.nomenclature.cl147'
    _description = 'CL147 - Вид на предписана терапия'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl148(models.Model):
    _name = 'trinity.nomenclature.cl148'
    _description = 'CL148 - Регистър на Заразните болести'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl149(models.Model):
    _name = 'trinity.nomenclature.cl149'
    _description = 'CL149 - Категоризация на случаите на заразни заболявания'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl150(models.Model):
    _name = 'trinity.nomenclature.cl150'
    _description = 'CL150 - Редки заболявания по Orphanet'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Language EN')

class TrinityNomenclatureCl997(models.Model):
    _name = 'trinity.nomenclature.cl997'
    _description = 'CL997 - Статус на специализирана заявка към НЗИС'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_descriptionen = fields.Char(string='Описание (en)')

class TrinityNomenclatureCl998(models.Model):
    _name = 'trinity.nomenclature.cl998'
    _description = 'CL998 - Предупреждение към издадени е-документи'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_source = fields.Char(string='Source')

class TrinityNomenclatureCl999(models.Model):
    _name = 'trinity.nomenclature.cl999'
    _description = 'CL999 - Код за грешка'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

    meta_display_value_en = fields.Char(string='Display Value (English)')
    meta_display_value_bg = fields.Char(string='Display Value (Bulgarian)')

class TrinityNomenclatureCls01(models.Model):
    _name = 'trinity.nomenclature.cls01'
    _description = 'CLS01'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

class TrinityNomenclatureCls02(models.Model):
    _name = 'trinity.nomenclature.cls02'
    _description = 'CLS02'
    _rec_name = 'description'
    _inherit = ['trinity.nomenclature.common.fields']

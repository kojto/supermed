# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from io import BytesIO
from datetime import datetime
import base64
import xlsxwriter
import logging

_logger = logging.getLogger(__name__)

class TrinityFinancialReportsInheritXlsxExport(models.Model):
    _inherit = 'trinity.financial.reports'

        ############################################################################
        #                              EXPORT TO EXCEL                             #
        ############################################################################

    def _get_patient_insurance_no(self, examination_record):
        if not examination_record.patient_identifier_id or not examination_record.cost_bearer_id:
            return ''

        cost_bearer_record = examination_record.patient_identifier_id.cost_bearer_ids.filtered(
            lambda cb: cb.cost_bearer_id.id == examination_record.cost_bearer_id.id and cb.active
        )

        if cost_bearer_record:
            return cost_bearer_record[0].patient_insurance_no or ''
        return ''

    def _get_patient_insurance_contract_no(self, examination_record):
        if not examination_record.patient_identifier_id or not examination_record.cost_bearer_id:
            return ''

        cost_bearer_record = examination_record.patient_identifier_id.cost_bearer_ids.filtered(
            lambda cb: cb.cost_bearer_id.id == examination_record.cost_bearer_id.id and cb.active
        )

        if cost_bearer_record:
            return cost_bearer_record[0].patient_insurance_contract_no or ''
        return ''

    def export_xlsx_xlm_file(self):
        self.check_report_overlap()
        self.calculate_services_and_prices()
        xlsx_export_methods = {
            'ДОВЕРИЕ': self.export_doverie_xlsx,
            'УНИКА': self.export_uniqa_xlsx,
            'ДЗИ': self.export_dzi_xlsx,
            'ДЖЕНЕРАЛИ': self.export_generali_xlsx,
            'БУЛСТРАД': self.export_bulstrad_xlsx,
            'СЪГЛАСИЕ': self.export_saglasie_xlsx,
            'ЗК БЪЛГАРИЯ': self.export_zk_bulgaria_xlsx,
            'АЛИАНЦ': self.export_allianz_xlsx,
            'ЖЗИ': self.export_zhzi_xlsx
        }

        export_method = xlsx_export_methods.get(self.cost_bearer_id_name)
        if export_method:
            export_method()
        else:

            pass

    # ---- ДОВЕРИЕ ------ #
    def export_doverie_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')

        # Create the filename
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-ДОВЕРИЕ.xlsx"

        # Logic for creating Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet2 = workbook.add_worksheet('Данни')
        sheet1 = workbook.add_worksheet('Услуги')
        sheet3 = workbook.add_worksheet('Указания за попълване')

        # currency format
        currency_format = workbook.add_format({'num_format': '#,##0.00'})

        # Add formats for the header and record rows
        header_format = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 10})
        record_format = workbook.add_format({'font_name': 'Arial', 'font_size': 10})
        header_border_format = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Arial', 'font_size': 11})

        # Write headers to the sheet with the specified format
        headers = ["ЕГН /ЛНЧ/", "Имена на застрахованото лице", "Дата", "Край", "МКБ10", "Код Спец.", "Код", "Описание", "Услуга име", "Цена ед."]

        for i, header in enumerate(headers):
            sheet1.write(0, i, header, header_format)

        for row_num, record in enumerate(records, start=1):
            sheet1.write(row_num, 0, record.patient_identifier_id.identifier if record.patient_identifier_id.identifier else '', record_format)
            sheet1.write(row_num, 1, record.patient_full_name if record.patient_full_name else '', record_format)
            sheet1.write(row_num, 2, record.examination_open_dtm.strftime('%d.%m.%Y') if record.examination_open_dtm else '', record_format)
            sheet1.write(row_num, 3, '')
            sheet1.write(row_num, 4, record.icd_code.key if record.icd_code.key else '', record_format)
            sheet1.write(row_num, 5, record.main_dr_performing_qualification_code_nhif if record.main_dr_performing_qualification_code_nhif else '', record_format)
            sheet1.write(row_num, 6, record.examination_type_id.nhif_procedure_code if record.examination_type_id.nhif_procedure_code else '', record_format)
            sheet1.write(row_num, 7, '')
            sheet1.write(row_num, 8, record.examination_type if record.examination_type else '', record_format)
            sheet1.write(row_num, 9, record.examination_type_id_price.price if record.examination_type_id_price else '', currency_format)

        last_row = len(records) + 2
        sheet1.write_formula(last_row, 9, f"SUM(J2:J{last_row})", currency_format)

        # Set the width of all columns to be twice the regular width
        for col_num in range(len(headers)):
            sheet1.set_column(col_num, col_num, 2 * 10)

        # ---- данни sheet2 ----#

        # Write specific text in the second row, second column
        sheet2.write(2, 0, "Булстат", header_border_format)
        sheet2.write(2, 1, "Наименование на ЛЗ", header_border_format)
        sheet2.write(2, 2, "Банка код", header_border_format)
        sheet2.write(2, 3, "IBAN", header_border_format)
        sheet2.write(2, 4, "Период на отчитане: от", header_border_format)
        sheet2.write(2, 5, "Период на отчитане: до", header_border_format)
        sheet2.write(2, 6, "Фактура", header_border_format)
        sheet2.write(2, 7, "Дата", header_border_format)
        sheet2.write(2, 8, "Начин плащане", header_border_format)
        sheet2.write(2, 9, "Обща сума", header_border_format)

        sheet2.write(3, 0, self.company_vat if self.company_vat else '', record_format)
        sheet2.write(3, 1, self.company_name if self.company_name else '', record_format)
        sheet2.write(3, 2, self.company_bic if self.company_bic else '', record_format)
        sheet2.write(3, 3, self.company_iban if self.company_iban else '', record_format)
        sheet2.write(3, 4, self.date_start.strftime('%d.%m.%Y'), record_format)
        sheet2.write(3, 5, self.date_end.strftime('%d.%m.%Y'), record_format)
        sheet2.write(3, 6, "", record_format)
        sheet2.write(3, 7, "", record_format)
        sheet2.write(3, 8, "По банков път", record_format)

        sheet2.write_formula(3, 9, f"={sheet1.name}!J{last_row + 1}", currency_format)

        # Set the width of all columns to be twice the regular width for sheet2
        for col_num in range(len(headers)):
            sheet2.set_column(col_num, col_num, 2 * 10)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

    # ---- УНИКА ------ #
    def export_uniqa_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')

        # Create the filename
        today_date = datetime.now().date().strftime("%d_%m_%Y")
        filename = f"RZI-2203131524-{today_date}.xlsx"

        # Logic for creating Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        # Add a text format for cells that should keep leading zeros
        text_format = workbook.add_format({'num_format': '@'})

        # currency format
        currency_format = workbook.add_format({'num_format': '#,##0.00" лв."'})

        # Add formats for the header and record rows
        header_format = workbook.add_format({'bold': True, 'font_name': 'Tahoma', 'font_size': 9, 'font_color': '#ff0000'})
        record_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 10, 'border': 1, 'border_color': 'black'})

        # Write headers to the sheet with the specified format
        headers = ["Date", "Name", "EGN", "Polica", "Action", "Note", "MKB", "Price"]

        for i, header in enumerate(headers):
            sheet.write(0, i, header, header_format)

        for row_num, record in enumerate(records, start=1):
            sheet.write(row_num, 0, record.examination_open_dtm.strftime('%d.%m.%Y') if record.examination_open_dtm else '', record_format)
            sheet.write(row_num, 1, record.patient_identifier_id.patient_full_name if record.patient_identifier_id.patient_full_name else '', record_format)
            sheet.write(row_num, 2, record.patient_identifier_id.identifier if record.patient_identifier_id.identifier else '', record_format)
            sheet.write(row_num, 3, self._get_patient_insurance_contract_no(record), record_format)
            sheet.write(row_num, 4, record.examination_type if record.examination_type else '', record_format)
            sheet.write(row_num, 5, record.main_dr_performing_doctor_id.description_bg if record.main_dr_performing_doctor_id.description_bg else '', record_format)
            sheet.write(row_num, 6, record.icd_code.key if record.icd_code.key else '', record_format)
            sheet.write(row_num, 7, record.examination_type_id_price.price if record.examination_type_id_price else '', record_format)

        last_row = len(records) + 2
        sheet.write_formula(last_row, 7, f"SUM(H2:H{last_row})")

        # Set the width of all columns to be twice the regular width
        for col_num in range(len(headers)):
            sheet.set_column(col_num, col_num, 2 * 10)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

    # ---- ДЗИ ------ #

    def export_dzi_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")


        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-ДЗИ.xlsx"

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet1 = workbook.add_worksheet('Услуги')
        sheet2 = workbook.add_worksheet('Данни')
        sheet3 = workbook.add_worksheet('Указания за попълване')

        currency_format = workbook.add_format({'num_format': '#,##0.00" лв."'})
        header_format = workbook.add_format({'bold': True, 'font_name': 'Calibri', 'font_size': 11})
        header_border_format = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Calibri', 'font_size': 11})
        title_format = workbook.add_format({'bold': True, 'font_name': 'Calibri', 'font_size': 14})
        record_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 10})
        footer_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 11})

        report_title = 'МЕСЕЧЕН ОТЧЕТ ЗА ДЕЙНОСТ ПО ДОГОВОР С "ДЗИ-ЖИВОТОЗАСТРАХОВАНЕ" ЕАД'
        headers = [
            "ЕГН/ЛНЧ", "Имена на осигуреното лице", "№ на здравна карта", "Амбулаторен лист", "Дата", "МКБ10", "Код Спец.", "Специалност име", "Код услуга", "Услуга име","Брой услуги","Цена ед."
        ]

        sheet1.merge_range('A1:M1', report_title, title_format)

        for i, header in enumerate(headers):
            sheet1.write(2, i, header, header_format)

        for row_num, record in enumerate(records, start=3):
            sheet1.write(row_num, 0, record.patient_identifier_id.identifier if record.patient_identifier_id.identifier else '', record_format)
            sheet1.write(row_num, 1, record.patient_full_name if record.patient_full_name else '', record_format)
            sheet1.write(row_num, 2, self._get_patient_insurance_no(record), record_format)
            sheet1.write(row_num, 3, record.e_examination_lrn if record.e_examination_lrn else '', record_format)
            sheet1.write(row_num, 4, record.examination_open_dtm.strftime('%d.%m.%Y') if record.examination_open_dtm else '', record_format)
            sheet1.write(row_num, 5, record.icd_code.key if record.icd_code.key else '', record_format)
            sheet1.write(row_num, 6, record.main_dr_performing_qualification_code_nhif if record.main_dr_performing_qualification_code_nhif else '', record_format)
            sheet1.write(row_num, 7, record.main_dr_performing_qualification_name if record.main_dr_performing_qualification_name else '', record_format)
            sheet1.write(row_num, 8, record.examination_type_id.nhif_procedure_code if record.examination_type_id.nhif_procedure_code else '', record_format)
            sheet1.write(row_num, 9, record.examination_type_id.examination_type if record.examination_type_id.examination_type else '', record_format)
            sheet1.write(row_num, 10, '1')
            sheet1.write(row_num, 11, record.examination_type_id_price.price if record.examination_type_id_price else '')

        last_row = len(records) + 3
        sheet1.write_formula(last_row, 11, f"SUM(L4:L{last_row})")

        for col in range(0, 8):
            sheet1.write(last_row, col, None, footer_format)

            sheet1.write(last_row + 3, 9, "Управител: ", footer_format)
            sheet1.write(last_row + 4, 10, "/Д-р Марин Генчев/", footer_format)

        for col_num in range(len(headers)):
            sheet1.set_column(col_num, col_num, 20)

        # ---- данни ----#

        sheet2.write(1, 1, 'МЕСЕЧЕН ОТЧЕТ ЗА ДЕЙНОСТ ПО ДОГОВОР С"ДЗИ-ЗО" АД', header_format)

        sheet2.write(2, 0, "Код на ИМП", header_border_format)
        sheet2.write(2, 1, "Регистрационен номер на ЛЗ", header_border_format)
        sheet2.write(2, 2, "Булстат", header_border_format)
        sheet2.write(2, 3, "Наименование на ЛЗ", header_border_format)
        sheet2.write(2, 4, "Банка код", header_border_format)
        sheet2.write(2, 5, "IBAN", header_border_format)
        sheet2.write(2, 6, "Период на отчитане: от", header_border_format)
        sheet2.write(2, 7, "Период на отчитане: до", header_border_format)
        sheet2.write(2, 8, "Фактура", header_border_format)
        sheet2.write(2, 9, "Дата", header_border_format)
        sheet2.write(2, 10, "Начин плащане", header_border_format)
        sheet2.write(2, 11, "Обща сума", header_border_format)

        sheet2.write(3, 0, "", record_format)
        sheet2.write(3, 1, self.company_hospital_no if self.company_hospital_no else '', record_format)
        sheet2.write(3, 2, self.company_vat if self.company_vat else '', record_format)
        sheet2.write(3, 3, self.company_name if self.company_name else '', record_format)
        sheet2.write(3, 4, self.company_bic if self.company_bic else '', record_format)
        sheet2.write(3, 5, self.company_iban if self.company_iban else '', record_format)
        sheet2.write(3, 6, self.date_start.strftime('%d.%m.%Y'), record_format)
        sheet2.write(3, 7, self.date_end.strftime('%d.%m.%Y'), record_format)
        sheet2.write(3, 8, "", record_format)
        sheet2.write(3, 9, "", record_format)
        sheet2.write(3, 10, "По банков път", record_format)
        sheet2.write_formula(3, 11, f"={sheet1.name}!L{last_row + 1}", record_format)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

    # ---- ДЖЕНЕРАЛИ ------ #

    def export_generali_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')

        # Create the filename
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-ДЖЕНЕРАЛИ.xlsx"

        # Logic for creating Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('ИЗВЪНБОЛНИЧНА ПОМОЩ')

        # currency format
        currency_format = workbook.add_format({'num_format': '#,##0.00" лв."'})

        # Add formats for the header and record rows
        main_header_format = workbook.add_format({'bold': True, 'font_name': 'Times New Roman', 'font_size': 10, 'align': 'center'})
        header_format = workbook.add_format({'bold': True, 'font_name': 'Times New Roman', 'font_size': 10, 'align': 'center'})
        header_format_regular = workbook.add_format({'border': 1, 'border_color': 'black', 'font_name': 'Times New Roman', 'font_size': 10, 'align': 'center'})
        header_format_grey = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Times New Roman', 'font_size': 10, 'bg_color': '#d8d8d8'})
        header_format_white = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Times New Roman', 'font_size': 10, 'bg_color': 'white'})
        header_format_ccffff = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Times New Roman', 'font_size': 10, 'bg_color': '#ccffff'})
        header_format_33cccc = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Times New Roman', 'font_size': 10, 'bg_color': '#33cccc'})
        record_format = workbook.add_format({'border': 1, 'border_color': 'black', 'font_name': 'Times New Roman', 'font_size': 10, 'bg_color': '#ccffff'})
        header_border_format = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Times New Roman', 'font_size': 11})

        # Write additional cells starting from the second row
        sheet.write(1, 1, "Име на ЛЗ", header_format_grey)
        sheet.write(1, 2, "Населено място", header_format_grey)
        sheet.write(1, 3, "Адрес", header_format_grey)
        sheet.write(2, 1, self.company_name if self.company_name else '', header_format_white)
        sheet.write(2, 2, self.company_city if self.company_city else '', header_format_white)
        sheet.write(2, 3, self.company_street if self.company_street else '', header_format_white)

        sheet.write(4, 1, "Банкова Сметка", header_format_grey)
        sheet.write(4, 2, "Банка", header_format_grey)
        sheet.write(4, 3, "ЕИК", header_format_grey)
        sheet.write(5, 1, self.company_iban if self.company_iban else '', header_format_white)
        sheet.write(5, 2, "", header_format_white)
        sheet.write(5, 3, self.company_vat if self.company_vat else '', header_format_white)

        sheet.merge_range('A8:J8', "СПЕЦИФИКАЦИЯ ЗА ИЗВЪРШЕНА МЕДИЦИНСКА ДЕЙНОСТ ПО ДОГОВОР С 'ДЖЕНЕРАЛИ ЗАСТРАХОВАНЕ' АД", main_header_format)
        sheet.write(9, 1, "за месец, година", header_format)
        sheet.write(9, 2, "12.2023", header_format_ccffff)

        # Write headers to the sheet with the specified format
        headers = ["№ по ред", "Име, презиме, фамилия на застраховано лице", "ЕГН", "Индивидуален здравен номер", "Медицинска специалност", "№ на амбулаторен лист", "Дата на събитие", "Код по МКБ", "Наименование на услуга", "Цена на услугата"]
        headers_2nd_row = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']

        for i, (header1, header2) in enumerate(zip(headers, headers_2nd_row)):
            sheet.write(11, i, header1, header_format_regular)
            sheet.write(12, i, header2, header_format_regular)

        sheet.write_formula(13, 9, f"SUM(J15:J{len(records) + 14})", header_format_33cccc)

        # Write the records
        for row_num, record in enumerate(records, start=0):
            sheet.write(row_num+14, 0, row_num + 1, record_format) # № ред
            sheet.write(row_num+14, 1, record.patient_full_name if record.patient_full_name else '', record_format)
            sheet.write(row_num+14, 2, record.patient_identifier_id.identifier if record.patient_identifier_id.identifier else '', record_format)
            sheet.write(row_num+14, 3, self._get_patient_insurance_no(record), record_format) # Осигурителен номер
            sheet.write(row_num+14, 4, record.main_dr_performing_qualification_code_nhif_and_name if record.main_dr_performing_qualification_code_nhif_and_name else '', record_format)
            sheet.write(row_num+14, 5, record.e_examination_lrn if record.e_examination_lrn else '', record_format)
            sheet.write(row_num+14, 6, record.examination_open_dtm.strftime('%d.%m.%Y') if record.examination_open_dtm else '', record_format)
            sheet.write(row_num+14, 7, record.icd_code.key if record.icd_code.key else '', record_format)
            sheet.write(row_num+14, 8, record.examination_type if record.examination_type else '', record_format)
            sheet.write(row_num+14, 9, record.examination_type_id_price.price if record.examination_type_id_price else '', record_format)

        # Write additional fields below the last record
        last_row_num = len(records) + 14
        sheet.write(last_row_num + 1, 8, "ОБЩА СТОЙНОСТ:", header_format)
        sheet.write_formula(last_row_num + 1, 9, f"SUM(J15:J{last_row_num})", header_format)
        sheet.write(last_row_num + 2, 1, "ПРОВЕРИЛ:", header_format)
        sheet.write(last_row_num + 3, 1, "/подпис на Дженерали Застраховане АД", header_format)
        sheet.write(last_row_num + 4, 8, "УПРАВИТЕЛ:", header_format)
        sheet.write(last_row_num + 5, 8, "/подпис и печат/", header_format)

        # Define column widths
        column_widths = {
            'A': 10,
            'B': 40,
            'C': 20,
            'D': 20,
            'E': 10,
            'F': 10,
            'G': 10,
            'H': 20,
            'I': 20,
            'J': 10,
            'K': 15,
            'L': 20,
            'M': 15
        }

        # Set column widths
        for col, width in column_widths.items():
            sheet.set_column(f'{col}:{col}', width)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

    # ---- БУЛСТРАД ------ #

    def export_bulstrad_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')

        # Create the filename
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-БУЛСТРАД.xlsx"

        # Logic for creating Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('месечен отчет за ИМП')
        sheet1 = workbook.add_worksheet('ИМП-дейности и специалности')
        sheet1 = workbook.add_worksheet('МКБ10')
        sheet1 = workbook.add_worksheet('Указания за попълване')

        # Add formats for the header and record rows
        header_format = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 10})
        record_format = workbook.add_format({'font_name': 'Arial', 'font_size': 10})

        # Write the top cells
        sheet.write(0, 5, "ПРИЛОЖЕНИЕ № 2", header_format)
        sheet.merge_range('C3:G3', "Отчет за извършени дейности по ИМП към ЗАД 'БУЛСТРАД ЖИВОТ В.И.Г.'", header_format)
        sheet.write(3, 3, "месец", header_format)

        month_names_bg = {'01': 'януари', '02': 'февруари','03': 'март', '04': 'април','05': 'май', '06': 'юни','07': 'юли', '08': 'август','09': 'септември', '10': 'октомври','11': 'ноември', '12': 'декември'}
        month_number = self.date_start.strftime('%m') if self.date_start else ''
        bulgarian_month_name = month_names_bg.get(month_number, '')

        # Write to the Excel sheet
        sheet.write(3, 4, bulgarian_month_name, header_format)
        sheet.write(3, 5, self.date_start.strftime('%Y') if self.date_start else '', header_format)
        sheet.write(4, 2, "Лечебно заведение:", header_format)
        sheet.merge_range('D5:G5', self.company_name if self.company_name else '', header_format)

        # Write headers to the sheet with the specified format
        headers = ["№", "Име, презиме, фамилия", "Идентификационен номер", "Дата", "Дейност код", "МКБ 10 Код", "Специалност код", "Цени"]

        for i, header in enumerate(headers):
            sheet.write(6, i, header, header_format)

        # Write the records
        for row_num, record in enumerate(records, start=0):
            sheet.write(row_num+7, 0, row_num + 1, record_format)
            sheet.write(row_num+7, 1, record.patient_full_name or '', record_format)
            sheet.write(row_num+7, 2, self._get_patient_insurance_no(record), record_format)
            sheet.write(row_num+7, 3, record.examination_open_dtm.strftime('%d.%m.%Y') if record.examination_open_dtm else '', record_format)
            sheet.write(row_num+7, 4, record.examination_type_id.nhif_procedure_code or '', record_format) # Код услуга
            sheet.write(row_num+7, 5, record.icd_code.key or '', record_format)
            sheet.write(row_num+7, 6, record.main_dr_performing_qualification_code_nhif or '', record_format)
            sheet.write(row_num+7, 7, record.examination_type_id_price.price if record.examination_type_id_price else '')

        # Calculate the sum of all prices in the last column
        sheet.write_formula(len(records) + 7, 7, f"=SUM(H7:H{len(records) + 7})")

        # Define column widths
        column_widths = {
            'A': 10,
            'B': 40,
            'C': 40,
            'D': 20,
            'E': 10,
            'F': 10,
            'G': 10,
            'H': 20
        }

        # Set column widths
        for col, width in column_widths.items():
            sheet.set_column(f'{col}:{col}', width)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

    # ---- ЗК БЪЛГАРИЯ ------ #

    def export_zk_bulgaria_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')

        # Create the filename
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-ЗК БЪЛГАРИЯ.xlsx"

        today_date = datetime.now().date().strftime("%d_%m_%Y")

        # Logic for creating Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet1 = workbook.add_worksheet('Услуги')
        sheet2 = workbook.add_worksheet('Данни')
        sheet3 = workbook.add_worksheet('Указания за попълване')

        currency_format = workbook.add_format({'num_format': '#,##0.00" лв."'})
        header_format = workbook.add_format({'bold': True, 'font_name': 'Calibri', 'font_size': 11})
        header_border_format = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Calibri', 'font_size': 11})
        title_format = workbook.add_format({'bold': True, 'font_name': 'Calibri', 'font_size': 14})
        record_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 10})
        footer_format = workbook.add_format({'font_name': 'Calibri', 'font_size': 11})

        # Write headers to the sheet with the specified format
        headers = ["ЕГН/ЛНЧ", "Имена", "Застрах.No", "Номер договор", "Код Риск", "Риск име", "Амбулаторен лист", "Дата", "Край", "МКБ10", "Лекар УИН", "Код Спец.", "Специалност име", "Описание", "Код услуга", "Услуга име", "Брой изп.", "Цена ед."]

        for i, header in enumerate(headers):
            sheet1.write(2, i, header, header_format)

        for row_num, record in enumerate(records, start=1):
            # You would replace the attributes of the record with the actual attributes of your model
            sheet1.write(row_num+3, 0, record.patient_identifier_id.identifier if record.patient_identifier_id.identifier else '', record_format)
            sheet1.write(row_num+3, 1, record.patient_full_name if record.patient_full_name else '', record_format)
            sheet1.write(row_num+3, 2, self._get_patient_insurance_no(record), record_format)
            sheet1.write(row_num+3, 3, '', record_format)
            sheet1.write(row_num+3, 4, '', record_format)
            sheet1.write(row_num+3, 5, '', record_format)
            sheet1.write(row_num+3, 6, record.e_examination_lrn if record.e_examination_lrn else '', record_format)
            sheet1.write(row_num+3, 7, record.examination_open_dtm.strftime('%d.%m.%Y') if record.examination_open_dtm else '', record_format)
            sheet1.write(row_num+3, 8, '', record_format)
            sheet1.write(row_num+3, 9, record.icd_code.key if record.icd_code.key else '', record_format)
            sheet1.write(row_num+3, 10, record.main_dr_performing_doctor_id.doctor_id if record.main_dr_performing_doctor_id.doctor_id else '', record_format)
            sheet1.write(row_num+3, 11, record.main_dr_performing_qualification_code_nhif if record.main_dr_performing_qualification_code_nhif else '', record_format)
            sheet1.write(row_num+3, 12, record.main_dr_performing_qualification_name if record.main_dr_performing_qualification_name else '', record_format)
            sheet1.write(row_num+3, 13, '', record_format)
            sheet1.write(row_num+3, 14, record.examination_type_id.nhif_procedure_code if record.examination_type_id.nhif_procedure_code else '', record_format)
            sheet1.write(row_num+3, 15, record.examination_type if record.examination_type else '', record_format)
            sheet1.write(row_num+3, 16, '1', record_format)
            sheet1.write(row_num+3, 17, record.examination_type_id_price.price if record.examination_type_id_price else '')

        # Calculate the sum of all prices in column R (index 17 in Python)
        last_row = len(records) + 4
        sheet1.write_formula(last_row, 17, f"SUM(R4:R{last_row})")

        # Define column widths
        column_widths = {
            'A': 10,
            'B': 40,
            'C': 40,
            'D': 20,
            'E': 20,
            'F': 20,
            'G': 20,
            'H': 20,
            'I': 20,
            'J': 20,
            'K': 20,
            'L': 20,
            'M': 20,
            'N': 20,
            'O': 20,
            'P': 20,
            'Q': 20,
            'R': 20
        }

        # Set column widths
        for col, width in column_widths.items():
            sheet1.set_column(f'{col}:{col}', width)

        # ---- данни ----#

        sheet2.write(1, 1, 'МЕСЕЧЕН ОТЧЕТ ЗА ДЕЙНОСТ ПО ДОГОВОР С"ДЗИ-ЗО" АД', header_format)

        sheet2.write(2, 0, "Код на ИМП", header_border_format)
        sheet2.write(2, 1, "Регистрационен номер на ЛЗ", header_border_format)
        sheet2.write(2, 2, "Булстат", header_border_format)
        sheet2.write(2, 3, "Наименование на ЛЗ", header_border_format)
        sheet2.write(2, 4, "Банка код", header_border_format)
        sheet2.write(2, 5, "IBAN", header_border_format)
        sheet2.write(2, 6, "Период на отчитане: от", header_border_format)
        sheet2.write(2, 7, "Период на отчитане: до", header_border_format)
        sheet2.write(2, 8, "Фактура", header_border_format)
        sheet2.write(2, 9, "Дата", header_border_format)
        sheet2.write(2, 10, "Начин плащане", header_border_format)
        sheet2.write(2, 11, "Обща сума", header_border_format)

        sheet2.write(3, 0, "", record_format)
        sheet2.write(3, 1, self.company_hospital_no if self.company_hospital_no else '', record_format)
        sheet2.write(3, 2, self.company_vat if self.company_vat else '', record_format)
        sheet2.write(3, 3, self.company_name if self.company_name else '', record_format)
        sheet2.write(3, 4, self.company_bic if self.company_bic else '', record_format)
        sheet2.write(3, 5, self.company_iban if self.company_iban else '', record_format)
        sheet2.write(3, 6, self.date_start.strftime('%d.%m.%Y'), record_format)
        sheet2.write(3, 7, self.date_end.strftime('%d.%m.%Y'), record_format)
        sheet2.write(3, 8, "", record_format)
        sheet2.write(3, 9, "", record_format)
        sheet2.write(3, 10, "По банков път", record_format)
        sheet2.write_formula(3, 11, f"={sheet1.name}!L{last_row + 1}", record_format)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

    # ---- АЛИАНЦ ------ #

    def export_allianz_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')

        # Create the filename
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-АЛИАНЦ.xlsx"

        # Logic for creating Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet1 = workbook.add_worksheet('import')
        sheet2 = workbook.add_worksheet('Указание попълване')
        sheet3 = workbook.add_worksheet('Zlopoluka')
        sheet4 = workbook.add_worksheet('type_service')
        sheet5 = workbook.add_worksheet('HI_SPECIALITY')
        sheet6 = workbook.add_worksheet('HIMKB10Diagnose')
        sheet7 = workbook.add_worksheet('Operativno lechenie')

        # currency format
        currency_format = workbook.add_format({'num_format': '#,##0.00" лв."'})

        # Add formats for the header and record rows
        header_format = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 12, 'bg_color': '#bdd6ee', 'font_color': '#00b0f0', 'text_wrap': True, 'border': 1})
        record_format = workbook.add_format({'font_name': 'Arial', 'font_size': 10})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})

        headers = ["Щета номер", "ЕГН/ЛНЧ", "Имена", "Дата начало", "Дата край", "МКБ10", "Лекар УИН", "Име Специалист",
          "Код специалност", "Име на специалност", "Код услуга", "Услуга име", "Брой услуги",
          "Предявена цена от ИМП/ДМС", "Злополука", "Тип услуга"]

        for idx, header in enumerate(headers):
            sheet1.write(0, idx, header, header_format)

        for row_num, record in enumerate(records, start=1):
            sheet1.write(row_num, 0, '')
            sheet1.write(row_num, 1, record.patient_identifier_id.identifier or '', record_format)
            sheet1.write(row_num, 2, record.patient_full_name or '', record_format)
            sheet1.write(row_num, 3, record.examination_open_dtm.strftime('%d.%m.%Y') if record.examination_open_dtm else '', record_format)
            sheet1.write(row_num, 4, record.examination_close_dtm.strftime('%d.%m.%Y') if record.examination_close_dtm else '', record_format)
            sheet1.write(row_num, 5, record.icd_code.key or '', record_format)
            sheet1.write(row_num, 6, record.main_dr_performing_doctor_id.doctor_id or '', record_format)
            sheet1.write(row_num, 7, record.main_dr_performing_full_name or '', record_format)
            sheet1.write(row_num, 8, record.main_dr_performing_qualification_code_nhif or '', record_format)
            sheet1.write(row_num, 9, record.main_dr_performing_qualification_name or '', record_format)
            sheet1.write(row_num, 10, record.examination_type_id.nhif_procedure_code or '', record_format)
            sheet1.write(row_num, 11, record.examination_type or '', record_format)
            sheet1.write(row_num, 12, '1', record_format)
            sheet1.write(row_num, 13, record.examination_type_id_price.price if record.examination_type_id_price else '', currency_format)
            sheet1.write(row_num, 14, 'не', record_format)
            sheet1.write(row_num, 15, '1', record_format)

            sheet1.write_formula(len(records) + 2, 13, f"SUM(N2:N{len(records) + 1})", currency_format)
        for col_num in range(len(headers)):
            sheet1.set_column(col_num, col_num, 2 * 10)

        workbook.close()
        output.seek(0)
        file_data = output.read()
        file_b64 = base64.b64encode(file_data)
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})
        try:
            self.generate_allinaz_annex_attachment()
        except Exception as e:
            _logger.error(f"Failed to generate Allianz annex during export: {e}")
        try:
            self.generate_report_pdf_attachment()
        except Exception as e:
            _logger.error(f"Failed to generate main report PDF during export: {e}")

        return

    # ---- СЪГЛАСИЕ ------ #

    def export_saglasie_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')

        # Create the filename
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-СЪГЛАСИЕ.xlsx"

        # Logic for creating Excel file
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('DKC')

        # currency format
        currency_format = workbook.add_format({'num_format': '#,##0.00" лв."'})
        currency_format_bold = workbook.add_format({'bold': True, 'num_format': '#,##0.00" лв."'})
        currency_format_border = workbook.add_format({'border': 1, 'border_color': 'black', 'num_format': '#,##0.00" лв."'})

        # Add formats for the header and record rows
        main_header_format = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'center', 'top': 2})
        header_format = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'center'})
        header_format_underlined = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'underline': True, 'font_size': 10})
        header_format_italic = workbook.add_format({'bold': False, 'italic': True, 'underline': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'right'})
        header_format_italic2 = workbook.add_format({'bold': False, 'italic': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'right'})
        record_format = workbook.add_format({'border': 1, 'border_color': 'black', 'font_name': 'Century Gothic', 'font_size': 10})
        header_border_format = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Century Gothic', 'font_size': 11})
        header_format_blue = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Century Gothic', 'text_wrap': True, 'font_size': 8, 'bg_color': '#99ccff'})
        header_format_bold_right = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'text_wrap': True, 'font_size': 10, 'align': 'right'})

        # Write the data to the specified cells
        sheet.merge_range('A1:D1', 'Регистрационен номер на ЛЗ:', header_format_italic)
        sheet.write(0, 4, self.company_hospital_no if self.company_hospital_no else '', header_format_underlined)  # Added missing quotation mark
        sheet.write(0, 11, "Банка", header_format_italic)
        sheet.write(0, 12, "ОББ", header_format_underlined)
        sheet.merge_range('A2:D2', "Наименование на ЛЗ:", header_format_italic)
        sheet.write(1, 4, self.company_name if self.company_name else '', header_format_underlined)
        sheet.write(1, 11, "BIC", header_format_italic)
        sheet.write(1, 12, self.company_bic if self.company_bic else '', header_format_underlined)
        sheet.merge_range('A3:D3', "Област:", header_format_italic)
        sheet.write(2, 4, '', header_format_underlined)
        sheet.write(2, 11, "IBAN", header_format_italic)
        sheet.write(2, 12, self.company_iban if self.company_iban else '', header_format_underlined)
        sheet.merge_range('A4:D4', "Град:", header_format_italic)
        sheet.write(3, 4, self.company_city if self.company_city else '', header_format_underlined)
        sheet.write(3, 11, "ИН", header_format_italic)
        sheet.merge_range('A5:D5', "Улица", header_format_italic)
        sheet.write(4, 4, self.company_street if self.company_street else '', header_format_underlined)
        sheet.write(4, 11, "", header_format_underlined)
        sheet.merge_range('A6:O6', 'СПЕЦИФИКАЦИЯ', main_header_format)
        sheet.merge_range('A7:C7', "ЗА ИЗВЪРШЕНА ДЕЙНОСТ В", header_format)
        sheet.merge_range('D7:G7', self.company_name if self.company_name else '', header_format)
        sheet.write(6, 7, "ПО ДОГОВОР С /СЪС", header_format)
        sheet.merge_range('I7:M7', "ЗД Съгласие АД", header_format)
        sheet.write(6, 13, "от дата:", header_format)
        sheet.write(6, 14, datetime.now().strftime('%d.%m.%Y'), header_format)
        sheet.write(8, 3, "КЪМ ФАКТУРА №", header_format)
        sheet.write(8, 9, "ЗА ПЕРИОД ОТ", header_format)
        sheet.write(8, 11, self.date_start.strftime('%d.%m.%Y'), header_format)
        sheet.write(8, 12, self.date_end.strftime('%d.%m.%Y'), header_format)

        # Write headers to the sheet with the specified format
        headers = ["№ ред", "Дата на изпълнение", "Име пациент", "Пациент ЕГН", "Осигурителен номер", "Шифър", "Специалност", "Име лекар", "Лекар изпълнител", "Амб. лист No", "Д-за код", "Наименование на диагнозата по МКБ10", "Услуга", "Код услуга", "Цена"]

        for i, header in enumerate(headers):
            sheet.write(11, i, header, header_format_blue)

        for row_num, record in enumerate(records, start=0):
            sheet.write(row_num+12, 0, row_num, record_format) # № ред
            sheet.write(row_num+12, 1, record.examination_open_dtm.strftime('%Y-%m-%d') if record.examination_open_dtm else '', record_format) # Дата на изпълнение
            sheet.write(row_num+12, 2, record.patient_full_name if record.patient_full_name else '', record_format) # Име пациент
            sheet.write(row_num+12, 3, record.patient_identifier_id.identifier if record.patient_identifier_id.identifier else '', record_format) # Пациент ЕГН
            sheet.write(row_num+12, 4, self._get_patient_insurance_no(record), record_format) # Осигурителен номер
            sheet.write(row_num+12, 5, record.main_dr_performing_qualification_code_nhif if record.main_dr_performing_qualification_code_nhif else '', record_format) # Шифър
            sheet.write(row_num+12, 6, record.main_dr_performing_qualification_name if record.main_dr_performing_qualification_name else '', record_format) # Специалност
            sheet.write(row_num+12, 7, record.main_dr_performing_full_name if record.main_dr_performing_full_name else '', record_format) # Име лекар
            sheet.write(row_num+12, 8, record.main_dr_performing_full_name if record.main_dr_performing_full_name else '', record_format) # Лекар изпълнител
            sheet.write(row_num+12, 9, record.e_examination_lrn if record.e_examination_lrn else '', record_format) # Амб. лист No
            sheet.write(row_num+12, 10, record.icd_code.key if record.icd_code.key else '', record_format) # Д-за код
            sheet.write(row_num+12, 11, record.additional_description if record.additional_description else '', record_format) # Наименование на диагнозата по МКБ10
            sheet.write(row_num+12, 12, record.examination_type if record.examination_type else '', record_format) # Услуга
            sheet.write(row_num+12, 13, record.examination_type_id.nhif_procedure_code if record.examination_type_id.nhif_procedure_code else '', record_format) # Код услуга
            sheet.write(row_num+12, 14, record.examination_type_id_price.price if record.examination_type_id_price else '', currency_format_border) # Цена

        # Calculate the sum of all prices in column 15 (indexed from 0, so it is 14 in code)
        sheet.write(row_num+14, 1, 'ВСИЧКО', header_format_bold_right)
        sheet.write_formula(len(records) + 13, 14, f"=SUM(O13:O{len(records) + 13})", currency_format_bold)

        sheet.merge_range('A' + str(len(records) + 17) + ':C' + str(len(records) + 17), 'ОБЩА СТОЙНОСТ:', header_format_bold_right)
        sheet.merge_range('D' + str(len(records) + 17) + ':F' + str(len(records) + 17), f"=SUM(O12:O{len(records) + 14})", currency_format)

        sheet.merge_range('B' + str(len(records) + 19) + ':G' + str(len(records) + 19), 'ЗА ЗД Съгласие АД', header_format)
        sheet.merge_range('K' + str(len(records) + 19) + ':O' + str(len(records) + 19), f"""ЗА {self.company_name if self.company_name else ''}""", header_format)

        sheet.write(len(records) + 20, 11, "ИЗПЪЛНИТЕЛЕН ДИРЕКТОР:", header_format_italic2)
        sheet.merge_range('A' + str(len(records) + 21) + ':F' + str(len(records) + 21), "ПРОВЕРИЛ: __________", header_format_italic2)
        sheet.merge_range('A' + str(len(records) + 24) + ':F' + str(len(records) + 24), "РАЗРЕШИЛ ПЛАЩАНЕТО: ___________", header_format_italic2)
        sheet.write(len(records) + 23, 11, "ПРОКУРИСТ:", header_format_italic2)
        sheet.write(len(records) + 25, 11, "СЪГЛАСУВАЛИ:", header_format_italic2)
        sheet.write(len(records) + 27, 5, "/подписи и печат/", header_format_italic2)
        sheet.write(len(records) + 27, 11, "Изготвил:", header_format_italic2)

        # Define a dictionary with column widths
        column_widths = {
            'A': 5,
            'B': 10,
            'C': 10,
            'D': 20,
            'E': 10,
            'F': 10,
            'G': 10,
            'H': 20,
            'I': 20,
            'J': 10,
            'K': 15,
            'L': 20,
            'M': 15,
            'N': 10,
            'O': 10
        }

        # Set the width of each column using a loop
        for col, width in column_widths.items():
            sheet.set_column(col + ':' + col, width)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

    # ---- ЖЗИ ------ #

    def export_zhzi_xlsx(self):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        if not records:
            raise UserError("Не са намерени записи по зададените критерии.")

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-ЖЗИ.xlsx"
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('спецификация')

        # currency format
        currency_format = workbook.add_format({'num_format': '#,##0.00" лв."'})
        currency_format_bold = workbook.add_format({'bold': True, 'num_format': '#,##0.00" лв."'})
        currency_format_border = workbook.add_format({'border': 1, 'border_color': 'black', 'num_format': '#,##0.00" лв."'})

        # Add formats for the header and record rows
        main_header_format = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'center', 'top': 2})
        header_format = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'center'})
        header_format_underlined = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'underline': True, 'font_size': 10})
        header_format_italic = workbook.add_format({'bold': False, 'italic': True, 'underline': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'right'})
        header_format_italic2 = workbook.add_format({'bold': False, 'italic': True, 'font_name': 'Century Gothic', 'font_size': 10, 'align': 'right'})
        record_format = workbook.add_format({'border': 1, 'border_color': 'black', 'font_name': 'Century Gothic', 'font_size': 10})
        header_border_format = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Century Gothic', 'font_size': 11})
        header_format_blue = workbook.add_format({'border': 1, 'border_color': 'black', 'bold': True, 'font_name': 'Century Gothic', 'text_wrap': True, 'font_size': 8, 'bg_color': '#99ccff'})
        header_format_bold_right = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'text_wrap': True, 'font_size': 10, 'align': 'right'})

        # Write the data to the specified cells
        sheet.merge_range('A1:D1', 'Регистрационен номер на ЛЗ:', header_format_italic)
        sheet.write(0, 4, self.company_hospital_no if self.company_hospital_no else '', header_format_underlined)  # Added missing quotation mark
        sheet.write(0, 9, "Банка", header_format_italic)
        sheet.write(0, 10, "ОББ", header_format_underlined)
        sheet.merge_range('A2:D2', "Наименование на ЛЗ:", header_format_italic)
        sheet.write(1, 4, self.company_name if self.company_name else '', header_format_underlined)
        sheet.write(1, 9, "BIC", header_format_italic)
        sheet.write(1, 10, self.company_bic if self.company_bic else '', header_format_underlined)
        sheet.merge_range('A3:D3', "Област:", header_format_italic)
        sheet.write(2, 4, '', header_format_underlined)
        sheet.write(2, 9, "IBAN", header_format_italic)
        sheet.write(2, 10, self.company_iban if self.company_iban else '', header_format_underlined)
        sheet.merge_range('A4:D4', "Град:", header_format_italic)
        sheet.write(3, 4, self.company_city if self.company_city else '', header_format_underlined)
        sheet.write(3, 9, "ИН", header_format_italic)
        sheet.merge_range('A5:D5', "Улица", header_format_italic)
        sheet.write(4, 4, self.company_street if self.company_street else '', header_format_underlined)
        sheet.write(4, 9, "", header_format_underlined)
        sheet.merge_range('A6:M6', 'СПЕЦИФИКАЦИЯ', main_header_format)
        sheet.merge_range('A7:C7', "ЗА ИЗВЪРШЕНА ДЕЙНОСТ В", header_format)
        sheet.merge_range('D7:G7', self.company_name if self.company_name else '', header_format)
        sheet.write(6, 7, "ПО ДОГОВОР С /СЪС", header_format)
        sheet.write(6, 9, "от дата:", header_format)
        sheet.write(6, 10, datetime.now().strftime('%d.%m.%Y'), header_format)
        sheet.write(8, 3, "КЪМ ФАКТУРА №", header_format)
        sheet.write(8, 8, "ЗА ПЕРИОД ОТ", header_format)
        sheet.write(8, 9, self.date_start.strftime('%d.%m.%Y'), header_format)
        sheet.write(8, 10, self.date_end.strftime('%d.%m.%Y'), header_format)

        headers = ["№ ред", "Име на пациент", "Пациент ЕГН", "Застрахователен номер", "Дата", "Амбулаторен лист №", "Услуга име", "Дейност код", "МКБ Код", "Име на лекаря", "УИН на лекаря", "Специалност код", "Единична цена в лв."]
        for i, header in enumerate(headers):
            sheet.write(11, i, header, header_format_blue)

        for row_num, record in enumerate(records, start=1):
            sheet.write(row_num + 12, 0, row_num, record_format)
            sheet.write(row_num + 12, 1, record.patient_full_name or '', record_format)
            sheet.write(row_num + 12, 2, record.patient_identifier_id.identifier or '', record_format)
            sheet.write(row_num + 12, 3, self._get_patient_insurance_no(record), record_format)
            sheet.write(row_num + 12, 4, record.examination_open_dtm.strftime('%Y-%m-%d') if record.examination_open_dtm else '', record_format)
            sheet.write(row_num + 12, 5, record.e_examination_lrn or '', record_format)
            sheet.write(row_num + 12, 6, record.examination_type or '', record_format)
            sheet.write(row_num + 12, 7, record.examination_type_id.nhif_procedure_code or '', record_format)
            sheet.write(row_num + 12, 8, record.icd_code.key or '', record_format)
            sheet.write(row_num + 12, 9, record.main_dr_performing_full_name or '', record_format)
            sheet.write(row_num + 12, 10, record.main_dr_performing_doctor_id.doctor_id or '', record_format)
            sheet.write(row_num + 12, 11, record.main_dr_performing_qualification_code_nhif or '', record_format)
            sheet.write(row_num + 12, 12, record.examination_type_id_price.price if record.examination_type_id_price else 0, record_format)

        sheet.write_formula(len(records) + 14, 12, f"=SUM(M13:M{len(records) + 14})")

        sheet.merge_range('A' + str(len(records) + 17) + ':C' + str(len(records) + 17), 'ОБЩА СТОЙНОСТ:', header_format_bold_right)
        sheet.merge_range('D' + str(len(records) + 17) + ':F' + str(len(records) + 17), f"=SUM(M13:O{len(records) + 14})", currency_format)

        sheet.merge_range('B' + str(len(records) + 19) + ':G' + str(len(records) + 19), 'ЗА ЖИВОТОЗАСТРАХОВАТЕЛЕН ИНСТИТУТ АД:', header_format_italic2)
        sheet.merge_range('K' + str(len(records) + 19) + ':O' + str(len(records) + 19), f"""ЗА {self.company_name if self.company_name else ''}""", header_format)

        sheet.write(len(records) + 20, 11, "ИЗПЪЛНИТЕЛЕН ДИРЕКТОР:", header_format_italic2)
        sheet.merge_range('A' + str(len(records) + 21) + ':F' + str(len(records) + 21), "ПРОВЕРИЛ: __________", header_format_italic2)
        sheet.merge_range('A' + str(len(records) + 24) + ':F' + str(len(records) + 24), "РАЗРЕШИЛ ПЛАЩАНЕТО: ___________", header_format_italic2)
        sheet.write(len(records) + 23, 11, "ПРОКУРИСТ:", header_format_italic2)
        sheet.write(len(records) + 25, 11, "СЪГЛАСУВАЛИ:", header_format_italic2)
        sheet.write(len(records) + 27, 5, "/подписи и печат/", header_format_italic2)
        sheet.write(len(records) + 27, 11, "Изготвил:", header_format_italic2)

        column_widths = {
            'A': 5,
            'B': 10,
            'C': 10,
            'D': 20,
            'E': 10,
            'F': 10,
            'G': 10,
            'H': 20,
            'I': 20,
            'J': 10,
            'K': 15,
            'L': 20,
            'M': 15,
            'N': 10,
            'O': 10
        }

        # Set the width of each column using a loop
        for col, width in column_widths.items():
            sheet.set_column(col + ':' + col, width)

        workbook.close()
        output.seek(0)
        file_data = output.read()

        # Encode data to binary
        file_b64 = base64.b64encode(file_data)

        # Create an 'ir.attachment' record with the custom filename
        attachment_data = {
            'name': filename,
            'type': 'binary',
            'datas': file_b64,
            'res_model': 'trinity.examination',
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        attachment = self.env['ir.attachment'].create(attachment_data)

        self.write({'last_xlsx_export_filename': filename})
        self.write({'last_xlsx_export': file_b64})

        self.generate_report_pdf_attachment()

        return

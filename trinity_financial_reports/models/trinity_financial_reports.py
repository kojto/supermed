from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime
from os.path import join as opj
from tempfile import TemporaryDirectory
from PyPDF2 import PdfMerger
from io import BytesIO
from weasyprint import HTML
import base64
import os
import io
import re
import zipfile
import logging

_logger = logging.getLogger(__name__)

class TrinityFinancialReports(models.Model):
    _name = 'trinity.financial.reports'
    _description = 'Trinity Financial Reports'
    _rec_name = 'financial_reports_lrn'
    _inherit = ["trinity.library.fr.qes", "trinity.library.printable"]

    financial_reports_lrn = fields.Char(string='LRN', required=True, default=lambda self: self.generate_financial_reports_lrn(), copy=False)
    name = fields.Char(string='Име на отчет', compute='_compute_name')

    @api.depends('date_start', 'date_end', 'cost_bearer_id')
    def _compute_name(self):
        for record in self:
            record.name = record.financial_reports_lrn

    contents = fields.One2many('trinity.financial.report.contents', 'financial_report_id', string='Услуги')

    cost_bearer_id = fields.Many2one('trinity.costbearer', string='Отчет към фирма:', required=True)
    cost_bearer_id_name = fields.Char(related='cost_bearer_id.name')

    main_dr_performing_doctor_id = fields.Many2one('trinity.medical.facility.doctors', string='За лекар:')
    main_dr_performing_token_certificate = fields.Text(related='main_dr_performing_doctor_id.token_certificate')
    main_dr_performing_full_name = fields.Char(related='main_dr_performing_doctor_id.full_name')
    main_dr_performing_identifier = fields.Char(related='main_dr_performing_doctor_id.identifier')
    main_dr_performing_qualification_code_nhif = fields.Char(related='main_dr_performing_doctor_id.qualification_code_nhif')
    main_dr_performing_practiceName = fields.Char(related='company_id.name')
    main_dr_performing_practiceNumber = fields.Char(related='hospital_id.hospital_no')
    main_dr_performing_nhif_ContractNo = fields.Char(related='hospital_id.nhif_contract_no')
    main_dr_performing_nhif_ContractDate = fields.Date(related='hospital_id.nhif_contract_date')

    user_token_certificate = fields.Text(string="User Token Certificate", related='main_dr_performing_doctor_id.token_certificate')
    user_token_expiresOnDatetime = fields.Datetime(string="User Token Expiry", related='main_dr_performing_doctor_id.expiresOnDatetime')
    user_token_is_expired = fields.Boolean(string="User Token is expired", default=False)

    date_start = fields.Date(string='От дата:', required=True, copy=False, default=lambda self: self.default_date_start())
    date_end = fields.Date(string='До дата:', required=True, copy=False, default=lambda self: self.default_date_end())

    fr_nhif = fields.Text(string='XML')
    fr_nhif_raw = fields.Text(string='fr_nhif_raw', copy=False)
    fr_nhif_signed = fields.Char(string='fr_nhif Signed Text', default='not signed', copy=False)
    SignedInfo_fr_nhif = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_fr_nhif_signature = fields.Char(string="SignedInfo signature", copy=False)

    last_xml_export = fields.Binary(string='.XML отчет', readonly=True)
    last_xml_export_filename = fields.Char(string="Име на файла")

    last_xlsx_export = fields.Binary(string='.XLSX отчет', readonly=True)
    last_xlsx_export_filename = fields.Char(string="Име на файла")

    last_pdf_export = fields.Binary(string='Амбулаторни листове', readonly=True)
    last_pdf_export_filename = fields.Char(string='Име на файла')

    allinaz_annex = fields.Binary(string='Приложение 7.2', readonly=True)
    allinaz_annex_filename = fields.Char(string='Име на файла')

    associated_invoice = fields.Char(string='Associated Invoice', readonly=True)
    invoice_attachment = fields.Binary(string='Фактура', readonly=True)
    invoice_attachment_filename = fields.Char(string='Име на файла')

    join_to_zip =  fields.Binary(string='Свали .zip архив', readonly=True)
    join_to_zip_filename = fields.Char(string='Име на файла')

    records_in_financial_report = fields.Many2many('trinity.examination', string='Записи включени в отчета')
    examinations_in_financial_report = fields.One2many('trinity.examination', 'financial_report_id', string='Прегледи включени в отчета')

    total_quantity = fields.Float(string='ОБЩ БРОЙ', digits=(16, 0), readonly=True)
    total_price = fields.Float(string='ОБЩО', digits=(16, 2), readonly=True)

    pre_vat_total_contents = fields.Float(string='ОБЩО без ДДС', compute='_compute_total_price_vat_contents')
    vat_amount_contents = fields.Float(string='ДДС', compute='_compute_total_price_vat_contents')
    total_price_contents = fields.Float(string='ОБЩО с ДДС', compute='_compute_total_price_vat_contents')

    @api.depends('contents.pre_vat_total', 'contents.vat_amount')
    def _compute_total_price_vat_contents(self):
        for record in self:
            record.pre_vat_total_contents = sum(record.contents.mapped('pre_vat_total')) if record.contents else 0.0
            record.vat_amount_contents = sum(record.contents.mapped('vat_amount')) if record.contents else 0.0
            record.total_price_contents = record.pre_vat_total_contents + record.vat_amount_contents

    def check_report_overlap(self):
        for record in self:
            overlapping_records = self.search([
                ('cost_bearer_id', '=', record.cost_bearer_id.id),
                ('id', '!=', record.id),
                ('date_start', '<=', record.date_end),
                ('date_end', '>=', record.date_start)
            ])
            if overlapping_records:
                raise ValidationError("Има вече създаден отчет за %s включващ дни от %s до %s" % (
                    record.cost_bearer_id.display_name,
                    record.date_start,
                    record.date_end
                ))

    def default_date_start(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        return first_day_of_current_month

    def default_date_end(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        first_day_of_next_month = first_day_of_current_month + relativedelta(months=1)
        last_day_of_current_month = first_day_of_next_month - timedelta(days=1)
        return last_day_of_current_month

    def forward_one_month(self):
        self.ensure_one()
        next_month = self.date_start + relativedelta(months=1)
        self.date_start = next_month.replace(day=1)
        self.date_end = self.date_end + relativedelta(months=1)
        next_month_end = self.date_end + relativedelta(months=1)
        self.date_end = next_month_end.replace(day=1) - relativedelta(days=1)
        self.create_financial_report()

    def backward_one_month(self):
        self.ensure_one()
        previous_month = self.date_start - relativedelta(months=1)
        self.date_start = previous_month.replace(day=1)
        next_month = self.date_start + relativedelta(months=1)
        self.date_end = next_month.replace(day=1) - relativedelta(days=1)
        self.create_financial_report()

    def forward_one_year(self):
        self.ensure_one()
        self.date_start = (self.date_start + relativedelta(years=1)).replace(day=1)
        self.date_end = self.date_end + relativedelta(years=1)
        next_year_end = (self.date_end + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        self.date_end = next_year_end
        self.create_financial_report()

    def backward_one_year(self):
        self.ensure_one()
        self.date_start = (self.date_start - relativedelta(years=1)).replace(day=1)
        self.date_end = self.date_end - relativedelta(years=1)
        previous_year_end = (self.date_end + relativedelta(months=1)).replace(day=1) - relativedelta(days=1)
        self.date_end = previous_year_end
        self.create_financial_report()

    def set_dates_to_current_month(self):
        today = date.today()
        first_day_of_current_month = today.replace(day=1)
        self.date_start = first_day_of_current_month
        first_day_of_next_month = first_day_of_current_month + relativedelta(months=1)
        last_day_of_current_month = first_day_of_next_month - timedelta(days=1)
        self.date_end = last_day_of_current_month
        self.create_financial_report()

    def set_dates_to_today(self):
        today = date.today()
        self.date_start = today
        self.date_end = today
        self.create_financial_report()

    def set_dates_to_current_week(self):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        self.date_start = start_of_week
        self.date_end = end_of_week
        self.create_financial_report()

    def set_dates_to_current_year(self):
        today = date.today()
        first_day_of_year = today.replace(month=1, day=1)
        last_day_of_year = today.replace(month=12, day=31)
        self.date_start = first_day_of_year
        self.date_end = last_day_of_year
        self.create_financial_report()


    def create_nhif_xml(self):
        domain = [
            ('cost_bearer_id', '=', self.cost_bearer_id.id or False),
            ('examination_open_dtm', '>=', self.date_start or False),
            ('examination_open_dtm', '<=', self.date_end or False),
            ('main_dr_performing_doctor_id', '=', self.main_dr_performing_doctor_id.id or False),
            ('e_examination_nrn', '!=', False),
        ]

        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        self.records_in_financial_report = [(6, 0, records.ids)]
        self.examinations_in_financial_report = [(6, 0, records.ids)]

        nhif_xml_values = []

        for record in records:
            record.compute_nhif_xml()
            nhif_xml_values.append(record.nhif_xml)

        combined_nhif_xml = '\n'.join(nhif_xml_values)

        combined_xml = (
            f'<Practice>'
            f'<PracticeCode>{self.main_dr_performing_practiceNumber if self.main_dr_performing_practiceNumber else ""}</PracticeCode>\n'
            f'<PracticeName>{self.main_dr_performing_practiceName if self.main_dr_performing_practiceName else ""}</PracticeName>\n'
            f'<ContractNo>{self.main_dr_performing_nhif_ContractNo if self.main_dr_performing_nhif_ContractNo else ""}</ContractNo>\n'
            f'<ContractDate>{self.main_dr_performing_nhif_ContractDate.strftime("%Y-%m-%d") if self.main_dr_performing_nhif_ContractDate else ""}</ContractDate>\n'
            f'<DateFrom>{self.date_start if self.date_start else ""}</DateFrom>'
            f'<DateTo>{self.date_end if self.date_end else ""}</DateTo>'
            f'<ContrHA>0</ContrHA>\n'
            f'<Doctor>\n<UIN>{self.main_dr_performing_doctor_id.doctor_id if self.main_dr_performing_doctor_id else ""}</UIN>\n'
            f'<EGN>{self.main_dr_performing_identifier if self.main_dr_performing_identifier else ""}</EGN>\n'
            f'<FullName>{self.main_dr_performing_full_name if self.main_dr_performing_full_name else ""}</FullName>\n'
            f'<SIMPCode>{self.main_dr_performing_qualification_code_nhif if self.main_dr_performing_qualification_code_nhif else ""}</SIMPCode>\n'
            f'</Doctor>\n</Practice>'
        )

        insertion_point = combined_xml.find('</Doctor>')
        if insertion_point == -1:
            _logger.warning("Could not find </Doctor> tag, appending XML at the end.")
            insertion_point = len(combined_xml)

        combined_xml = (combined_xml[:insertion_point] + combined_nhif_xml + combined_xml[insertion_point:])

        self.fr_nhif = combined_xml

        self.sign_fr_nhif()

    def sign_fr_nhif(self, field_name='fr_nhif', signedinfo='SignedInfo_fr_nhif', signedinfo_signature='SignedInfo_fr_nhif_signature', is_signed='fr_nhif_signed'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)

    @api.onchange('main_dr_performing_doctor_id', 'cost_bearer_id', 'date_start', 'date_end')
    def create_financial_report(self):
        if self.cost_bearer_id and 'НЗОК' in self.cost_bearer_id_name:
            self.create_nhif_xml()
        else:
            return

    def download_xml(self):
        if self.fr_nhif_signed == 'signed':
            filename = f'FILE_SUBM_AMB_IMP_R-{self.date_start}-{self.date_end}-{self.main_dr_performing_practiceNumber}-{self.main_dr_performing_doctor_id.doctor_id}.xml'
            file_b64 = base64.b64encode(self.fr_nhif.encode('utf-8'))
            self.last_xml_export = file_b64
            self.last_xml_export_filename = filename
        return

    def get_signature_nhif(self):
        return

    @api.model
    def generate_financial_reports_lrn(self):
        date_today = datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.financial.reports'].sudo().search(
            [('financial_reports_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='financial_reports_lrn desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.financial_reports_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1

        lrn_value = f'FiR-{date_today}-{current_company_vat}-{sequence_number:04d}'
        return lrn_value

    def get_filename_allinaz_annex(self):
        first_record_date = self.date_start.strftime('%Y-%m')
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-АЛИАНЦ"
        return filename

    def generate_allinaz_annex_attachment(self):
        try:
            html = self.generate_report_html('trinity_financial_reports.allinanz_annex')
            html = self.inject_report_css(html, None)

            pdf_data = HTML(string=html).write_pdf()

            filename = f"{self.date_start.strftime('%Y-%m')}-ЕИК_{self.company_vat}-{self.cost_bearer_id.name}.pdf"
            data_record = base64.b64encode(pdf_data)

            self.allinaz_annex = data_record
            self.allinaz_annex_filename = filename
            return data_record

        except Exception as e:
            _logger.error(f"Failed to generate Allianz annex PDF: {str(e)}")
            raise UserError(f"Failed to generate Allianz annex PDF: {str(e)}")

    def generate_report_pdf_attachment(self, report_ref=None, report_css_ref=None):
        domain = [
            ('company_id', '=', self.company_id.id),
            ('cost_bearer_id', '=', self.cost_bearer_id.id),
            ('examination_open_dtm', '>=', self.date_start),
            ('examination_open_dtm', '<=', self.date_end),
        ]
        records = self.env['trinity.examination'].search(domain, order='e_examination_lrn desc')

        if not records:
            return False

        pdf_merger = PdfMerger()
        individual_attachments = []

        for record in records:
            result = record.print_amb_list_as_pdf(report_ref=report_ref, report_css_ref=report_css_ref)
            if result.get('type') == 'ir.actions.act_url':
                attachment_id = int(result['url'].split('/web/content/')[1].split('?')[0])
                attachment = self.env['ir.attachment'].browse(attachment_id)
                if attachment.exists():
                    individual_attachments.append(attachment.id)
                    pdf_merger.append(BytesIO(base64.b64decode(attachment.datas)))

        if not individual_attachments:
            return False

        first_record_date = records[0].examination_open_dtm.strftime('%Y-%m')
        costbearer = records[0].cost_bearer_id.name
        filename = f"{first_record_date}-ЕИК_{self.company_vat}-{costbearer}-амбулаторни_листове.pdf"

        combined_pdf_data = BytesIO()
        pdf_merger.write(combined_pdf_data)
        pdf_merger.close()
        combined_pdf_data.seek(0)
        encoded_pdf = base64.b64encode(combined_pdf_data.read())

        self.last_pdf_export = encoded_pdf
        self.last_pdf_export_filename = filename

        return {
            'individual_attachments': individual_attachments,
            'combined_pdf': encoded_pdf,
            'combined_filename': filename,
        }

    def create_invoice_from_financial_report(self):
        default_subcode = self.env['kojto.commission.subcodes'].search([], limit=1)
        if not default_subcode:
            raise UserError("No subcodes found. Please create a subcode first.")

        default_vat_treatment = self.env['kojto.finance.vat.treatment'].search([], limit=1)
        company = self.env['kojto.contacts'].search([('res_company_id', '=', self.env.user.company_id.id)], limit=1)

        if company:
            bank_account = self.env['kojto.base.bank.accounts'].search([
                ('contact_id', '=', company.id),
                ('account_type', '=', 'bank'),
                ('active', '=', True)
            ], limit=1)

        current_date = fields.Date.today()

        invoice_vals = {
            'examinations_in_invoice': [(6, 0, self.records_in_financial_report.ids)],
            'document_in_out_type': 'outgoing',
            'counterparty_type': 'legal_entity',
            'counterparty_id': self.cost_bearer_id.associated_contact_id.id,
            'subcode_id': default_subcode.id,
            'invoice_vat_treatment_id': default_vat_treatment.id if default_vat_treatment else False,
            'exchange_rate_to_bgn': 1.00000,
            'exchange_rate_to_eur': 0.51129,
            'company_bank_account_id': bank_account.id if bank_account else False,
            'subject': f'Отчет към {self.cost_bearer_id.name} за период {self.date_start} - {self.date_end}',
            'language_id': self.env.ref('base.lang_bg').id,
            'currency_id': self.env.ref('base.BGN').id,
            'payment_terms_id': self.env['kojto.base.payment.terms'].search([('name', '=', 'Плащане по банков път')], limit=1).id,
            'date_issue': current_date,
            'date_due': current_date + timedelta(days=7),
            'date_tax_event': current_date,
        }

        if self.company_id:
            company = self.company_id
            for model, field in [
                ("kojto.base.names", "company_name_id"),
                ("kojto.base.addresses", "company_address_id"),
                ("kojto.base.tax.numbers", "company_tax_number_id"),
                ("kojto.base.phones", "company_phone_id"),
                ("kojto.base.emails", "company_email_id"),
            ]:
                record = self.env[model].search([("contact_id", "=", company.id)], limit=1)
                if record:
                    invoice_vals[field] = record.id

        if self.cost_bearer_id.associated_contact_id:
            counterparty = self.cost_bearer_id.associated_contact_id
            for model, field in [
                ("kojto.base.names", "counterparty_name_id"),
                ("kojto.base.addresses", "counterparty_address_id"),
                ("kojto.base.tax.numbers", "counterparty_tax_number_id"),
                ("kojto.base.phones", "counterparty_phone_id"),
                ("kojto.base.emails", "counterparty_email_id"),
            ]:
                record = self.env[model].search([("contact_id", "=", counterparty.id)], limit=1)
                if record:
                    invoice_vals[field] = record.id


        invoice = self.env['kojto.finance.invoices'].create(invoice_vals)

        for i, content in enumerate(self.contents, 1):
            self.env['kojto.finance.invoice.contents'].create({
                'invoice_id': invoice.id,
                'position': str(i),
                'name': content.unit,
                'quantity': content.unit_quantity,
                'unit_price': content.unit_price,
                'vat_rate': content.vat_rate,
                'pre_vat_total': content.unit_quantity * content.unit_price,
            })

        if invoice.consecutive_number:
            self.write({'associated_invoice': invoice.consecutive_number})

        # Generate PDF using print_document_as_pdf function
        try:
            pdf_result = invoice.print_document_as_pdf()
            if pdf_result and pdf_result.get('type') == 'ir.actions.act_url':
                # Extract attachment ID from the URL
                attachment_id = int(pdf_result['url'].split('/web/content/')[1].split('?')[0])
                attachment = self.env['ir.attachment'].browse(attachment_id)
                if attachment.exists():
                    # Store the PDF data in the associated_invoice field
                    self.write({
                        'invoice_attachment': attachment.datas,
                        'invoice_attachment_filename': f"{self.date_start.strftime('%Y-%m')}-ЕИК_{self.company_vat}-{self.cost_bearer_id.name}-Фактура_№{invoice.consecutive_number}.pdf"
                    })
        except Exception as e:
            _logger.error(f"Failed to generate invoice PDF: {str(e)}")
            # Continue execution even if PDF generation fails

        self.compute_zipped_files()

        return invoice

    def compute_zipped_files(self):
        zip_buffer = io.BytesIO()
        with TemporaryDirectory() as temp_dir:
            if self.last_xlsx_export:
                filename = self.last_xlsx_export_filename or 'last_xlsx_export.xlsx'
                with open(opj(temp_dir, filename), 'wb') as xls_file:
                    xls_file.write(base64.b64decode(self.last_xlsx_export))
            if self.last_pdf_export:
                filename = self.last_pdf_export_filename or 'last_pdf_export.pdf'
                with open(opj(temp_dir, filename), 'wb') as pdf_file:
                    pdf_file.write(base64.b64decode(self.last_pdf_export))
            if self.allinaz_annex:
                filename = self.allinaz_annex_filename or 'allinaz_annex.pdf'
                with open(opj(temp_dir, filename), 'wb') as annex_file:
                    annex_file.write(base64.b64decode(self.allinaz_annex))
            if self.invoice_attachment:
                filename = self.invoice_attachment_filename or 'invoice_attachment.pdf'
                with open(opj(temp_dir, filename), 'wb') as annex_file:
                    annex_file.write(base64.b64decode(self.invoice_attachment))
            with io.BytesIO() as stream:
                with zipfile.ZipFile(stream, 'w') as zipf:
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_dir))
                zip_data = stream.getvalue()

        self.join_to_zip = base64.b64encode(zip_data)
        self.join_to_zip_filename = f"{self.date_start.strftime('%Y-%m')}-ЕИК_{self.company_vat}-{self.cost_bearer_id.name}.zip"

    def calculate_services_and_prices(self):
        self.delete_existing_contents()

        if self.cost_bearer_id_name == 'НЗОК':
            if self.main_dr_performing_doctor_id:
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('cost_bearer_id', '=', self.cost_bearer_id.id or False),
                    ('examination_open_dtm', '>=', self.date_start or False),
                    ('examination_open_dtm', '<=', self.date_end or False),
                    ('main_dr_performing_doctor_id', '=', self.main_dr_performing_doctor_id.id),
                ]
            else:
                domain = [
                    ('company_id', '=', self.company_id.id),
                    ('cost_bearer_id', '=', self.cost_bearer_id.id or False),
                    ('examination_open_dtm', '>=', self.date_start or False),
                    ('examination_open_dtm', '<=', self.date_end or False),
                ]
        else:
            domain = [
                ('company_id', '=', self.company_id.id),
                ('cost_bearer_id', '=', self.cost_bearer_id.id),
                ('examination_open_dtm', '>=', self.date_start),
                ('examination_open_dtm', '<=', self.date_end),
            ]

        examination_types = self.env['trinity.examination'].search(domain).mapped('examination_type')
        filtered_examination_types = [etype for etype in examination_types if isinstance(etype, str)]

        for etype in examination_types:
            if not isinstance(etype, str):
                _logger.warning("Non-string type found in examination_types: %s (type: %s)", etype, type(etype))

        unique_types = sorted(set(filtered_examination_types))
        self.assign_examination_types_contents(unique_types, filtered_examination_types, domain)

    def delete_existing_contents(self):
        self.contents = [(5, 0, 0)]

    def assign_examination_types_contents(self, unique_types, filtered_examination_types, domain):
        self.contents = [(5, 0, 0)]

        for exam_type in unique_types:
            count = filtered_examination_types.count(exam_type)
            record = self.env['trinity.examination'].search(domain + [('examination_type', '=', exam_type)], limit=1)
            price = record.examination_type_id_price.price if record and record.examination_type_id_price else 0.0

            self.env['trinity.financial.report.contents'].create({
                'financial_report_id': self.id,
                'unit': exam_type,
                'unit_quantity': count,
                'unit_price': price,
                'vat_rate': 0,
            })

class TrinityRejectedPayment(models.Model):
    _name = 'trinity.rejected.payment'
    _description = 'Trinity Rejected Payment'
    _rec_name = 'rejected_payment_lrn'

    user_id = fields.Many2one('res.users', string='Current User', default=lambda self: self.env.user, copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id, copy=False)
    company_vat = fields.Char(related='company_id.vat', string='Company VAT')

    rejected_payment_lrn = fields.Char(string='LRN', required=True, default=lambda self: self.generate_rejected_payment_lrn(), copy=False)

    cost_bearer_id = fields.Many2one('trinity.costbearer', string='Носител на разходите:', required=True)
    cost_bearer_id_name = fields.Char(related='cost_bearer_id.name')

    cost_bearer_message = fields.Text(string='Съобщение')
    extracted_nrn = fields.Char(string='НРН')
    extracted_lrn = fields.Char(string='Амб. №')

    @api.model
    def generate_rejected_payment_lrn(self):
        date_today = datetime.now().date().strftime('%Y-%m-%d')
        current_company_vat = self.env.user.company_id.vat

        existing_records = self.env['trinity.rejected.payment'].sudo().search(
            [('rejected_payment_lrn', 'like', date_today), ('company_vat', '=', current_company_vat)],
            order='rejected_payment_lrn desc',
            limit=1
        )
        if existing_records:
            last_sequence = existing_records.rejected_payment_lrn[-4:]
            sequence_number = int(last_sequence) + 1
        else:
            sequence_number = 1

        lrn_value = f'FiR-{date_today}-{current_company_vat}-{sequence_number:04d}'
        return lrn_value

    @api.onchange('cost_bearer_message')
    def extract_nrn_and_lrn(self):
        if self.cost_bearer_message:
            extracted_nrn = re.findall(r'\b[A-Z0-9]{12}\b', self.cost_bearer_message)
            self.extracted_nrn = ','.join(extracted_nrn) if extracted_nrn else False

            extracted_lrn = re.findall(r'\b[\d-]{16,}\b', self.cost_bearer_message)
            self.extracted_lrn = ','.join(extracted_lrn) if extracted_lrn else False

            self.update_rejected_payments(extracted_nrn, extracted_lrn)
        else:
            self.extracted_nrn = False
            self.extracted_lrn = False

    def update_rejected_payments(self, extracted_nrn, extracted_lrn):
        if extracted_lrn:
            records = self.env['trinity.examination'].search([('e_examination_lrn', 'in', extracted_lrn)])
            records.write({'rejected_payment': 'yes'})

        if extracted_nrn:
            records = self.env['trinity.examination'].search([('e_examination_nrn', 'in', extracted_nrn)])
            records.write({'rejected_payment': 'yes'})

class TrinityExaminationInherit(models.Model):
    _inherit = 'trinity.examination'

    financial_report_id = fields.Many2one('trinity.financial.reports', string='Свързан отчет')

from odoo import api, fields, models, exceptions
from odoo.exceptions import ValidationError, UserError
from xml.etree import ElementTree as ET
from datetime import date, timedelta, datetime
from lxml import etree
import base64
import logging
_logger = logging.getLogger(__name__)

class TrinityMonthlyNotification(models.Model):
    _name = 'trinity.monthly.notification'
    _description = 'Trinity Monthly Notification'
    _rec_name = 'monthly_notification_num'
    _inherit = ["trinity.library.fr.qes"]

    contents = fields.One2many('trinity.monthly.notification.contents', 'monthly_notification_id', string='Услуги')

    monthly_notification_num = fields.Char(string='№ на месечно известие')
    practice_code = fields.Char(string='Код на практиката')
    date_from = fields.Date(string='От дата')
    date_to = fields.Date(string='До дата')
    inv_type_code = fields.Char(string='Код фактура')
    inv_type = fields.Char(string='Вид фактура')
    nhif_type_code = fields.Char(string='Код по НЗОК')
    nhif_type = fields.Char(string='Вид по НЗОК')
    inv_summ = fields.Float(string='Сума на фактурата')
    inv_fl = fields.Char(string='Статус на фактурата')
    id_inv = fields.Char(string='ИД на фактурата')
    from_inv_num = fields.Char(string='Свързана фактура')
    from_inv_date = fields.Date(string='Дата на свързаната фактура')

    last_xml_export = fields.Binary(string='Фактурата към НЗОК в XML формат', readonly=True)
    last_xml_export_filename = fields.Char(string="Име на файла")

    monthly_notification = fields.Binary(string='Зареди месечно известие на НЗОК', attachment=True)
    monthly_notification_filename = fields.Char(string='Име на файл')

    invoice_id = fields.Many2one('kojto.finance.invoices', string='Свързана фактура')
    invoice_type = fields.Selection([('invoice', 'Фактура'),('correction', 'Коригирана фактура'),('credit', 'Кредитно известие'), ('debit', 'Дебитно известие')], string='Вид фактура', default='invoice')

    fr_nhif = fields.Text(string='Фактурата на НЗОК в XML формат')
    fr_nhif_raw = fields.Text(string='fr_nhif_raw', copy=False)
    fr_nhif_signed = fields.Char(string='fr_nhif Signed Text', default='not signed', copy=False)
    SignedInfo_fr_nhif = fields.Char(string="SignedInfo", copy=False)
    SignedInfo_fr_nhif_signature = fields.Char(string="SignedInfo signature", copy=False)

    total_price = fields.Float(string='ОБЩО', digits=(16, 2))
    pre_vat_total_contents = fields.Float(string='ОБЩО без ДДС', compute='_compute_total_price_vat_contents')
    vat_amount_contents = fields.Float(string='ДДС', compute='_compute_total_price_vat_contents')
    total_price_contents = fields.Float(string='ОБЩО с ДДС', compute='_compute_total_price_vat_contents')

    def download_xml(self):
        if self.fr_nhif_signed == 'signed':
            filename = f'ELECTRONIC_INVOICE-{self.monthly_notification_num or "UNKNOWN"}-{self.date_from or ""}-{self.date_to or ""}.xml'
            file_b64 = base64.b64encode(self.fr_nhif.encode('utf-8'))
            # Store the XML export (you may need to add these fields if they don't exist)
            if hasattr(self, 'last_xml_export'):
                self.last_xml_export = file_b64
            if hasattr(self, 'last_xml_export_filename'):
                self.last_xml_export_filename = filename
        return

    def get_signature_nhif(self):
        return

    @api.depends('contents.pre_vat_total', 'contents.vat_amount')
    def _compute_total_price_vat_contents(self):
        for record in self:
            record.pre_vat_total_contents = sum(record.contents.mapped('pre_vat_total')) if record.contents else 0.0
            record.vat_amount_contents = sum(record.contents.mapped('vat_amount')) if record.contents else 0.0
            record.total_price_contents = record.pre_vat_total_contents + record.vat_amount_contents

    @api.onchange('monthly_notification')
    def extract_data_from_monthly_notification(self):
        if not self.monthly_notification:
            return
        try:
            notification_xml = base64.b64decode(self.monthly_notification).decode('utf-8')
            root = ET.fromstring(notification_xml)
            ns = {'ns': 'http://pis.technologica.com/MonthlyNotif.xsd'}

            def get_text(path):
                elem = root.find(path, namespaces=ns)
                return elem.text if elem is not None else None

            fields_map = {
                'monthly_notification_num': './/ns:monthly_notification_num',
                'practice_code': './/ns:practice_code',
                'inv_type_code': './/ns:inv_type_code',
                'inv_type': './/ns:inv_type',
                'nhif_type_code': './/ns:nhif_type_code',
                'nhif_type': './/ns:nhif_type',
                'inv_fl': './/ns:inv_fl',
                'id_inv': './/ns:id_inv',
                'from_inv_num': './/ns:from_inv_num',
            }

            for field, path in fields_map.items():
                setattr(self, field, get_text(path))

            def parse_date(path):
                val = get_text(path)
                return datetime.strptime(val, "%Y-%m-%d").date() if val else None

            self.date_from = parse_date('.//ns:date_from')
            self.date_to = parse_date('.//ns:date_to')
            self.from_inv_date = parse_date('.//ns:from_inv_date')
            self.inv_summ = float(get_text('.//ns:inv_summ') or 0) if get_text('.//ns:inv_summ') else None

            contents_vals = []
            for detail in root.findall('.//ns:Monthly_Notification_Details', namespaces=ns):
                try:
                    activity_name_elem = detail.find('ns:activity_name', namespaces=ns)
                    activity_code_elem = detail.find('ns:activity_code', namespaces=ns)
                    quantity_elem = detail.find('ns:quantity', namespaces=ns)
                    unit_price_elem = detail.find('ns:unit_price', namespaces=ns)

                    contents_vals.append((0, 0, {
                        'unit': activity_name_elem.text if activity_name_elem is not None else None,
                        'unit_code': activity_code_elem.text if activity_code_elem is not None else None,
                        'unit_quantity': float(quantity_elem.text) if quantity_elem is not None and quantity_elem.text else 0.0,
                        'unit_price': float(unit_price_elem.text) if unit_price_elem is not None and unit_price_elem.text else 0.0,
                        'vat_rate': 0.0,
                    }))
                except Exception:
                    pass

            self.contents = [(5, 0, 0)] + contents_vals
            self.update_invoice_type()

        except Exception:
            pass

    def update_invoice_type(self):
        for record in self:
            type_map = {
                'INVOICE': 'invoice',
                'DT_NOTIF': 'debit',
                'CT_NOTIF': 'credit'
            }
            record.invoice_type = type_map.get(record.inv_type_code)
            if record.inv_type_code in ('DT_NOTIF', 'CT_NOTIF') and record.from_inv_num:
                parent_invoice = self.env['kojto.finance.invoices'].search([
                    ('consecutive_number', '=', record.from_inv_num)
                ], limit=1)
                if parent_invoice:
                    record.parent_invoice = parent_invoice.id


    ############################################################################
    #                            INVOICE GENERATION                            #
    ############################################################################

    def create_invoice_from_monthly_notification(self):
        default_subcode = self.env['kojto.commission.subcodes'].search([], limit=1)
        if not default_subcode:
            raise UserError("No subcodes found. Please create a subcode first.")

        default_vat_treatment = self.env['kojto.finance.vat.treatment'].search([], limit=1)
        company = self.env['kojto.contacts'].search([('res_company_id', '=', self.env.user.company_id.id)], limit=1)

        bank_account = False
        if company:
            bank_account = self.env['kojto.base.bank.accounts'].search([
                ('contact_id', '=', company.id),
                ('account_type', '=', 'bank'),
                ('active', '=', True)
            ], limit=1)

        for report in self:
            nhif_record = self.env['kojto.contacts'].search([('name', '=', 'СЗОК')], limit=1)

            costbearer = self.env['trinity.costbearer'].search([
                ('associated_contact_id', '=', nhif_record.id)
            ], limit=1)

            examination_records = self.env['trinity.examination']
            if costbearer and report.date_from and report.date_to:

                date_from_start = datetime.combine(report.date_from, datetime.min.time())
                date_to_end = datetime.combine(report.date_to, datetime.max.time())

                examination_records = self.env['trinity.examination'].search([
                    ('cost_bearer_id', '=', costbearer.id),
                    ('examination_open_dtm', '>=', date_from_start),
                    ('examination_open_dtm', '<=', date_to_end),
                ])
            else:
                _logger.warning("Costbearer or date range not found for monthly notification %s", report.monthly_notification_num)

            parent_invoice = False
            if report.from_inv_num:
                parent_invoice = self.env['kojto.finance.invoices'].search([
                    ('consecutive_number', '=', report.from_inv_num)
                ], limit=1)

            kojto_invoice_type = report.invoice_type
            if report.invoice_type == 'debit':
                kojto_invoice_type = 'debit_note'
            elif report.invoice_type == 'credit':
                kojto_invoice_type = 'credit_note'

            invoice_vals = {
                'examinations_in_invoice': [(6, 0, examination_records.ids)],
                'document_in_out_type': 'outgoing',
                'invoice_type': kojto_invoice_type,
                'counterparty_type': 'legal_entity',
                'counterparty_id': nhif_record.id,
                'subcode_id': default_subcode.id,
                'invoice_vat_treatment_id': default_vat_treatment.id if default_vat_treatment else False,
                'parent_invoice_id': parent_invoice.id if parent_invoice else False,
                'exchange_rate_to_bgn': 1.00000,
                'exchange_rate_to_eur': 0.51129,
                'company_bank_account_id': bank_account.id if bank_account else False,
                'subject': f'Месечно известие № {report.monthly_notification_num} за период {report.date_from} - {report.date_to}',
                'language_id': self.env.ref('base.lang_bg').id,
                'currency_id': self.env.ref('base.BGN').id,
                'payment_terms_id': self.env['kojto.base.payment.terms'].search([('name', '=', 'Плащане по банков път')], limit=1).id,
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

            counterparty = nhif_record.id
            for model, field in [
                ("kojto.base.names", "counterparty_name_id"),
                ("kojto.base.addresses", "counterparty_address_id"),
                ("kojto.base.tax.numbers", "counterparty_tax_number_id"),
                ("kojto.base.phones", "counterparty_phone_id"),
                ("kojto.base.emails", "counterparty_email_id"),
            ]:
                record = self.env[model].search([("contact_id", "=", counterparty)], limit=1)
                if record:
                    invoice_vals[field] = record.id

            invoice = self.env['kojto.finance.invoices'].create(invoice_vals)
            report.invoice_id = invoice.id

            for i, content in enumerate(report.contents, 1):
                self.env['kojto.finance.invoice.contents'].create({
                    'invoice_id': invoice.id,
                    'position': str(i),
                    'name': content.unit or '',
                    'quantity': content.unit_quantity,
                    'unit_price': content.unit_price,
                    'vat_rate': content.vat_rate,
                    'pre_vat_total': content.unit_quantity * content.unit_price,
                })

            report.generate_nhis_electronic_invoice()

            return

    def generate_nhis_electronic_invoice(self):
        for record in self:
            if not record.invoice_id:
                raise UserError("No linked invoice found. Please create or link an invoice first.")

            invoice = record.invoice_id
            company = record.company_id or self.env.user.company_id
            hospital = record.hospital_id
            nhif_recipient = self.env['kojto.contacts'].search([('name', '=', 'СЗОК')], limit=1)

            # Parse monthly notification XML to extract invoice fields
            invoice_data = {}
            if record.monthly_notification:
                try:
                    notification_xml = base64.b64decode(record.monthly_notification).decode('utf-8')
                    notif_root = ET.fromstring(notification_xml)
                    notif_ns = {'ns': 'http://pis.technologica.com/MonthlyNotif.xsd'}

                    def get_notif_text(path):
                        elem = notif_root.find(path, namespaces=notif_ns)
                        return elem.text if elem is not None else None

                    # Extract invoice fields from monthly notification
                    invoice_data = {
                        'recipient_code': get_notif_text('.//ns:recipient_code'),
                        'recipient_address': get_notif_text('.//ns:recipient_address'),
                        'recipient_bulstat': get_notif_text('.//ns:recipient_bulstat'),
                        'issuer_type': get_notif_text('.//ns:issuer_type'),
                        'legal_form': get_notif_text('.//ns:legal_form'),
                        'address_by_contract': get_notif_text('.//ns:address_by_contract'),
                        'registration_by_VAT': get_notif_text('.//ns:registration_by_VAT'),
                        'grounds_for_not_charging_VAT': get_notif_text('.//ns:grounds_for_not_charging_VAT'),
                        'contract_no': get_notif_text('.//ns:contract_no'),
                        'contract_date': get_notif_text('.//ns:contract_date'),
                        'health_insurance_fund_type_code': get_notif_text('.//ns:health_insurance_fund_type_code'),
                        'measure_code': get_notif_text('.//ns:measure_code'),
                        'payment_type': get_notif_text('.//ns:payment_type'),
                        'original': get_notif_text('.//ns:original'),
                    }
                except Exception as e:
                    _logger.warning("Error parsing monthly notification XML: %s", e)

            # Get recipient information - from monthly notification or hospital/NHIF contact
            recipient_code = invoice_data.get('recipient_code')
            if not recipient_code:
                if hospital and hospital.nhif_area_code:
                    recipient_code = hospital.nhif_area_code.key
                else:
                    # Default to "22" if not found
                    default_cl015 = self.env['trinity.nomenclature.cl015'].search([('key', '=', '22')], limit=1)
                    recipient_code = default_cl015.key if default_cl015 else "22"

            recipient_address = invoice_data.get('recipient_address')
            if not recipient_address and nhif_recipient and nhif_recipient.addresses:
                address_parts = []
                addr = nhif_recipient.addresses[0]
                if addr.address:
                    address_parts.append(addr.address)
                if addr.city:
                    address_parts.append(addr.city)
                if address_parts:
                    recipient_address = ", ".join(address_parts)
            if not recipient_address:
                recipient_address = ""

            recipient_bulstat = invoice_data.get('recipient_bulstat')
            if not recipient_bulstat and nhif_recipient and nhif_recipient.registration_number:
                recipient_bulstat = nhif_recipient.registration_number
            if not recipient_bulstat:
                recipient_bulstat = ""

            # Get issuer information - from monthly notification or hospital/company
            issuer_type = invoice_data.get('issuer_type') or "0"

            legal_form = hospital.legal_form if hospital and hospital.legal_form else ""

            address_by_contract = invoice_data.get('address_by_contract')
            if not address_by_contract and company:
                address_parts = []
                if company.street:
                    address_parts.append(company.street)
                if company.city:
                    address_parts.append(company.city)
                if address_parts:
                    address_by_contract = ", ".join(address_parts)
            if not address_by_contract:
                address_by_contract = ""

            registration_by_VAT = invoice_data.get('registration_by_VAT') or "0"

            grounds_for_not_charging_VAT = invoice_data.get('grounds_for_not_charging_VAT') or "Чл.113,ал.9 от ЗДДС"

            contract_no = invoice_data.get('contract_no')
            if not contract_no:
                contract_no = hospital.nhif_contract_no if hospital and hospital.nhif_contract_no else ""

            contract_date = invoice_data.get('contract_date')
            if not contract_date:
                contract_date = hospital.nhif_contract_date.strftime("%Y-%m-%d") if hospital and hospital.nhif_contract_date else ""

            health_insurance_fund_type_code = invoice_data.get('health_insurance_fund_type_code') or "NZOK"

            measure_code = invoice_data.get('measure_code') or "BR"

            payment_type = invoice_data.get('payment_type') or "B"

            original = invoice_data.get('original') or "Y"

            ns = "http://pis.technologica.com/electronic_invoice.xsd"
            root = ET.Element("ELECTRONIC_INVOICE", xmlns=ns)

            ET.SubElement(root, "fin_document_type_code").text = record.inv_type_code or "INVOICE"
            ET.SubElement(root, "fin_document_no").text = invoice.consecutive_number or "UNKNOWN"
            ET.SubElement(root, "fin_document_month_no").text = record.monthly_notification_num or ""
            ET.SubElement(root, "fin_document_date").text = (invoice.date_issue or date.today()).strftime("%Y-%m-%d")

            recipient = ET.SubElement(root, "Invoice_Recipient")
            ET.SubElement(recipient, "recipient_code").text = recipient_code
            ET.SubElement(recipient, "recipient_name").text = nhif_recipient.name if nhif_recipient else "СЗОК"
            ET.SubElement(recipient, "recipient_address").text = recipient_address
            ET.SubElement(recipient, "recipient_bulstat").text = recipient_bulstat

            issuer = ET.SubElement(root, "Invoice_Issuer")
            ET.SubElement(issuer, "issuer_type").text = issuer_type
            ET.SubElement(issuer, "legal_form").text = legal_form
            ET.SubElement(issuer, "company_name").text = company.name or ""
            ET.SubElement(issuer, "address_by_contract").text = address_by_contract
            ET.SubElement(issuer, "registration_by_VAT").text = registration_by_VAT
            ET.SubElement(issuer, "grounds_for_not_charging_VAT").text = grounds_for_not_charging_VAT
            ET.SubElement(issuer, "issuer_bulstat").text = company.vat or company.company_registry or ""
            ET.SubElement(issuer, "contract_no").text = contract_no
            ET.SubElement(issuer, "contract_date").text = contract_date
            ET.SubElement(issuer, "rhi_nhif_no").text = record.practice_code or ""

            ET.SubElement(root, "health_insurance_fund_type_code").text = health_insurance_fund_type_code
            ET.SubElement(root, "activity_type_code").text = record.nhif_type_code or ""
            ET.SubElement(root, "date_from").text = record.date_from.strftime("%Y-%m-%d") if record.date_from else ""
            ET.SubElement(root, "date_to").text = record.date_to.strftime("%Y-%m-%d") if record.date_to else ""

            for content in record.contents:
                operation = ET.SubElement(root, "Business_operation")
                ET.SubElement(operation, "activity_code").text = content.unit_code or ""
                ET.SubElement(operation, "activity_name").text = content.unit or ""
                ET.SubElement(operation, "measure_code").text = measure_code
                ET.SubElement(operation, "quantity").text = str(content.unit_quantity)
                ET.SubElement(operation, "unit_price").text = str(content.unit_price)
                ET.SubElement(operation, "value_price").text = str(content.pre_vat_total)

            aggregated = ET.SubElement(root, "Aggregated_amounts")
            ET.SubElement(aggregated, "payment_type").text = payment_type
            ET.SubElement(aggregated, "total_amount").text = str(record.inv_summ or record.total_price_contents or 0)
            ET.SubElement(aggregated, "payment_amount").text = str(record.inv_summ or record.total_price_contents or 0)
            ET.SubElement(aggregated, "original").text = original
            ET.SubElement(aggregated, "tax_event_date").text = record.date_to.strftime("%Y-%m-%d") if record.date_to else ""

            xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml_str += ET.tostring(root, encoding="unicode", method="xml")
            record.fr_nhif = xml_str

        self.sign_fr_nhif()

    def sign_fr_nhif(self, field_name='fr_nhif', signedinfo='SignedInfo_fr_nhif', signedinfo_signature='SignedInfo_fr_nhif_signature', is_signed='fr_nhif_signed'):
        self.prepare_first_digest(field_name, signedinfo, is_signed, signedinfo_signature)


class TrinityMonthlyNotificationContents(models.Model):
    _name = 'trinity.monthly.notification.contents'
    _description = 'Trinity Monthly Notification Contents'

    monthly_notification_id = fields.Many2one('trinity.monthly.notification', string='Monthly Notification', required=True, ondelete='cascade')

    unit = fields.Char(string='Услуга')
    unit_code = fields.Char(string='Код услуга')
    unit_quantity = fields.Float(string='Брой', digits=(16, 0))
    unit_price = fields.Float(string='Ед. цена лв.', digits=(16, 2))
    pre_vat_total = fields.Float(string='Обща цена лв. без ДДС', digits=(16, 2), compute='_compute_pre_vat_total')
    vat_rate = fields.Float(string='ДДС ставка %', digits=(16, 2), default=0.0)
    vat_amount = fields.Float(string='ДДС сума лв.', digits=(16, 2), compute='_compute_vat_amount')
    total_price = fields.Float(string='Обща цена лв.', digits=(16, 2), compute='_compute_total_price')

    @api.depends('unit_price', 'unit_quantity')
    def _compute_pre_vat_total(self):
        for record in self:
            record.pre_vat_total = record.unit_price * record.unit_quantity

    @api.depends('pre_vat_total', 'vat_rate')
    def _compute_vat_amount(self):
        for record in self:
            record.vat_amount = record.pre_vat_total * record.vat_rate / 100

    @api.depends('unit_price', 'unit_quantity', 'pre_vat_total', 'vat_rate')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.pre_vat_total + record.vat_amount

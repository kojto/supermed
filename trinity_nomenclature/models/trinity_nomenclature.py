import base64
import datetime
import json
import logging
import math
import re
import uuid
import xml.etree.ElementTree as ET
import pandas as pd
import unicodedata
import requests
from io import BytesIO

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from ..static.trinity_nomenclature_field_mapping import field_mapping
from ..static.trinity_nomenclature_ignored_xlsx_sheets import IGNORED_SHEETS
from ..static.trinity_nomenclature_nhif_import import CL_MODELS

_logger = logging.getLogger(__name__)

class TrinityNomenclature(models.Model):
    _name = "trinity.nomenclature"
    _description = "Номенклатура"
    _order = "cl_value asc nulls last"

    active = fields.Boolean(default=True)
    cl_value = fields.Char(required=True, string="CL стойност")
    target_model = fields.Many2one('ir.model', string="Целеви модел", compute="_compute_target_model", store=True, ondelete='set null')
    description = fields.Char(string="Описание")
    json_data = fields.Binary(string="JSON данни")
    json_data_rows = fields.Integer(string="JSON редове данни")
    csv_data = fields.Binary(string="CSV данни")
    xml_data = fields.Binary(string="XML данни")
    is_from_nhif = fields.Boolean(string="От НЗОК")
    is_from_xlsx = fields.Boolean(string="От XLSX")

    version = fields.Char(string="Версия")

    @api.depends('cl_value')
    def _compute_target_model(self):
        for record in self:
            record.target_model = False
            if record.cl_value:
                model_name = f"trinity.nomenclature.{record.cl_value.lower()}"
                record.target_model = self.env['ir.model'].search([('model', '=', model_name)], limit=1) or False

    def get_json_data_as_string(self):
        if not self.json_data:
            return ""
        try:
            return base64.b64decode(self.json_data).decode('utf-8')
        except Exception as e:
            _logger.error(f"Грешка при декодиране на JSON данни: {e}")
            return ""

    def create_or_update_cl_record(self):
        total_duplicates_removed = 0
        for record in self:
            if record.target_model:
                duplicates_removed = self.env[record.target_model.model].delete_duplicate_records_based_on_key()
                total_duplicates_removed += duplicates_removed

        all_results = []
        for record in self:
            if not record.csv_data or not record.target_model:
                all_results.append({"cl_value": getattr(record, "cl_value", "Неизвестно"), "error": "Липсват CSV данни или целеви модел"})
                continue
            try:
                all_results.append(self.process_csv_data(record, base64.b64decode(record.csv_data)))
            except Exception as e:
                all_results.append({"cl_value": getattr(record, "cl_value", "Неизвестно"), "error": f"Неуспешно декодиране на CSV: {e}"})

        total_created = sum(r.get("created", 0) for r in all_results if "created" in r)
        total_updated = sum(r.get("updated", 0) for r in all_results if "updated" in r)
        processed = sum(1 for r in all_results if "created" in r or "updated" in r)
        all_errors = [f"{r['cl_value']}: {r['error']}" for r in all_results if "error" in r]
        message = [f"Обработени {processed} запис{'а' if processed != 1 else ''}", f"Създадени: {total_created}", f"Обновени: {total_updated}"]
        if total_duplicates_removed > 0:
            message.append(f"Премахнати дубликати: {total_duplicates_removed}")
        if all_errors:
            message.extend(["", "Грешки:"] + [f"  {e}" for e in all_errors[:10]])
            if len(all_errors) > 10:
                message.append(f"  ... и още {len(all_errors) - 10} грешки")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": f"CL Обработка",
                "message": "\n".join(message),
                "type": "success" if not all_errors else "warning",
                "sticky": False,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "reload",
                }
            }
        }


    def process_csv_data(self, record, csv_bytes, batch_size=200, chunk_size=1000):

        def normalize_key(val):
            if not val:
                return None
            return unicodedata.normalize("NFKC", str(val)).strip().lower()

        try:
            test_df = pd.read_csv(BytesIO(csv_bytes), dtype=str, nrows=1)
        except Exception as e:
            return {
                "cl_value": getattr(record, "cl_value", "Неизвестно"),
                "error": f"Неуспешно парсиране на CSV: {e}"
            }

        test_df.columns = test_df.columns.str.strip().str.lower()

        if "key" not in test_df.columns or "description" not in test_df.columns:
            return {
                "cl_value": getattr(record, "cl_value", "Неизвестно"),
                "error": "CSV липсва задължителна колона: 'Key' або 'Description'"
            }

        model = self.env[record.target_model.model]
        boolean_fields = [f for f, fo in model._fields.items()
                        if f.startswith("meta_") and fo.type == "boolean"]
        many2one_fields = {f: fo for f, fo in model._fields.items()
                          if f.startswith("meta_") and fo.type == "many2one"}

        total_created, total_updated, all_errors = 0, 0, []
        total_processed = 0
        all_keys_in_csv = set()

        _logger.info(f"Collecting all keys from CSV for {record.cl_value}...")
        try:
            for chunk_df in pd.read_csv(BytesIO(csv_bytes), dtype=str, chunksize=chunk_size):
                chunk_df.columns = chunk_df.columns.str.strip().str.lower()
                chunk_df['key'] = chunk_df['key'].apply(normalize_key)
                all_keys_in_csv.update(chunk_df['key'].dropna().unique())
        except Exception as e:
            return {
                "cl_value": getattr(record, "cl_value", "Неизвестно"),
                "error": f"Грешка при събиране на ключове: {e}"
            }

        _logger.info(f"Building cache of existing records for {record.cl_value}...")
        existing_records = model.search(['|', ('active', '=', True), ('active', '=', False)])
        existing_keys = {}
        for rec in existing_records:
            normalized_key = normalize_key(rec.key)
            if normalized_key in all_keys_in_csv:
                existing_keys[normalized_key] = rec

        _logger.info(f"Processing CSV in chunks of {chunk_size} for {record.cl_value}...")
        chunk_number = 0
        to_create, to_update = [], []

        try:
            csv_reader = pd.read_csv(BytesIO(csv_bytes), dtype=str, chunksize=chunk_size)

            for chunk_df in csv_reader:
                chunk_number += 1
                _logger.info(f"Processing chunk {chunk_number} ({len(chunk_df)} rows) for {record.cl_value}...")

                chunk_df.columns = chunk_df.columns.str.strip().str.lower()
                chunk_df['key'] = chunk_df['key'].apply(normalize_key)

                chunk_df = chunk_df.drop_duplicates(subset=['key'], keep='last')

                rows = chunk_df.to_dict("records")

                for data in rows:
                    total_processed += 1
                    key = normalize_key(data.get("key"))
                    description = data.get("description")
                    valid_since_version = data.get("valid_since_version")
                    valid_until_version = data.get("valid_until_version")

                    if not key or not description or str(description).strip() == "":
                        all_errors.append("Невалидни данни: Липсва ключ или описание")
                        continue

                    def process_value(v):
                        if v is None:
                            return None
                        if isinstance(v, float) and math.isnan(v):
                            return ""
                        if isinstance(v, str) and v.strip() in ['nan', 'NaN', 'None']:
                            return ""
                        return v

                    meta_vals = {}
                    for k, v in data.items():
                        if k.startswith("meta_"):
                            if k in many2one_fields:
                                field_info = many2one_fields[k]
                                if v and str(v).strip() and str(v).strip() not in ['nan', 'NaN', 'None', '']:
                                    try:
                                        related_model = self.env[field_info.comodel_name]
                                        related_record = related_model.search([('key', '=', str(v).strip())], limit=1)
                                        if related_record:
                                            meta_vals[k] = related_record.id
                                        else:
                                            all_errors.append(f"Не е намерен запис в {field_info.comodel_name} с ключ '{v}' за поле '{k}'")
                                    except Exception as e:
                                        all_errors.append(f"Грешка при търсене на запис за '{k}' = '{v}': {e}")
                            else:
                                processed_val = process_value(v)
                                if processed_val is not None:
                                    meta_vals[k] = processed_val

                    vals = {
                        "description": description,
                        "current_version": record.version,
                        **meta_vals
                    }

                    if valid_since_version is not None:
                        processed_version = process_value(valid_since_version)
                        if processed_version is not None:
                            vals["valid_since_version"] = processed_version
                    if valid_until_version is not None:
                        processed_version = process_value(valid_until_version)
                        if processed_version is not None:
                            vals["valid_until_version"] = processed_version

                    for k in vals:
                        if k in boolean_fields:
                            v = vals[k]
                            vals[k] = (
                                v if isinstance(v, bool)
                                else True if isinstance(v, str) and v.lower() in ("true", "1", "t", "y", "yes")
                                else False
                            )

                    if key in existing_keys:
                        to_update.append((existing_keys[key], vals))
                    else:
                        to_create.append({**vals, "key": key})

                    if len(to_create) >= batch_size:
                        try:
                            created_records = model.create(to_create)
                            total_created += len(to_create)
                            for rec in created_records:
                                existing_keys[normalize_key(rec.key)] = rec
                            to_create = []
                        except Exception as e:
                            all_errors.append(f"Неуспешно създаване на партида: {e}")
                            to_create = []

                    if len(to_update) >= batch_size:
                        try:
                            for rec, vals in to_update:
                                rec.write(vals)
                            total_updated += len(to_update)
                            to_update = []
                        except Exception as e:
                            all_errors.append(f"Неуспешно обновяване на партида: {e}")
                            to_update = []

                _logger.info(f"Completed chunk {chunk_number} for {record.cl_value}")

        except Exception as e:
            return {
                "cl_value": getattr(record, "cl_value", "Неизвестно"),
                "error": f"Грешка при четене на CSV chunks: {e}"
            }

        if to_create:
            try:
                model.create(to_create)
                total_created += len(to_create)
            except Exception as e:
                all_errors.append(f"Неуспешно създаване на оставащите записи: {e}")

        if to_update:
            try:
                for rec, vals in to_update:
                    rec.write(vals)
                total_updated += len(to_update)
            except Exception as e:
                all_errors.append(f"Неуспешно обновяване на оставащите записи: {e}")

        result = {
            "cl_value": getattr(record, "cl_value", "Неизвестно"),
            "created": total_created,
            "updated": total_updated,
            "total_processed": total_processed
        }


        if all_errors:
            result["error"] = "; ".join(all_errors)

        return result


class TrinityNomenclatureImportWizard(models.TransientModel):
    _name = "trinity.nomenclature.import.wizard"
    _description = "Импорт на CL номенклатури от Excel"

    file = fields.Binary(string=".xlsx файл", required=True)
    filename = fields.Char(string="Име на файла")

    def _extract_version_from_filename(self, filename):
        if not filename:
            return ""

        version_pattern = r'v\d+(?:\.\d+)*'
        match = re.search(version_pattern, filename, re.IGNORECASE)

        if match:
            return match.group(0)

        return ""

    def _map_column_to_field(self, column_name):
        reverse_mapping = {v: k for k, v in field_mapping.items()}
        return reverse_mapping.get(column_name, column_name)

    def action_import(self):
        if not self.file:
            raise UserError(_("Моля, качете Excel файл."))

        try:
            data = base64.b64decode(self.file)
            excel = pd.ExcelFile(BytesIO(data))
        except Exception as e:
            raise UserError(_("Неуспешно четене на Excel файл: %s") % str(e))

        created_count, updated_count, errors = 0, 0, []
        ignored_sheets = IGNORED_SHEETS

        for sheet_name in excel.sheet_names:
            if not sheet_name.upper().startswith("CL") or sheet_name in ignored_sheets:
                continue
            try:
                raw_df = pd.read_excel(excel, sheet_name=sheet_name, header=None, dtype=str)
                if raw_df.empty or len(raw_df.columns) == 0:
                    errors.append(f"Лист {sheet_name} е празен или няма колони")
                    continue

                header_row_idx = raw_df.index[raw_df.iloc[:, 0] == "Key"]
                if header_row_idx.empty:
                    errors.append(f"Не е намерен 'Key' заглавен ред в лист {sheet_name}")
                    continue

                df = pd.read_excel(excel, sheet_name=sheet_name, header=header_row_idx[0], dtype=str)

                df = df.dropna(how="all")
                if df.empty:
                    errors.append(f"Лист {sheet_name} няма данни след обработка")
                    continue

                rename_dict = {}
                if len(df.columns) > 0: rename_dict[df.columns[0]] = "key"
                if len(df.columns) > 1: rename_dict[df.columns[1]] = "description"
                for col in df.columns[2:]:
                    if col == "Since":
                        rename_dict[col] = "valid_since_version"
                    elif col == "Valid Until":
                        rename_dict[col] = "valid_until_version"
                    else:
                        field_name = self._map_column_to_field(col)
                        rename_dict[col] = field_name

                df = df.rename(columns=rename_dict)

                json_str = df.to_json(orient="records", force_ascii=False, indent=2)
                json_b64 = base64.b64encode(json_str.encode('utf-8'))

                csv_buffer = BytesIO()
                df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
                csv_b64 = base64.b64encode(csv_buffer.getvalue()).decode()

                version = self._extract_version_from_filename(self.filename)

                vals = {
                    "cl_value": sheet_name,
                    "description": f"Данни от {sheet_name}",
                    "json_data": json_b64,
                    "json_data_rows": len(json_str.split("\n")),
                    "csv_data": csv_b64,
                    "is_from_xlsx": True,
                    "version": version,
                }

                existing = self.env["trinity.nomenclature"].search([
                    ("cl_value", "=", sheet_name),
                    '|', ('active', '=', True), ('active', '=', False)
                ], limit=1)
                if existing:
                    existing.write(vals)
                    updated_count += 1
                else:
                    self.env["trinity.nomenclature"].create(vals)
                    created_count += 1

            except IndexError as e:
                errors.append(f"Лист {sheet_name} има невалидна структура (грешка в индекса): {str(e)}")
            except Exception as e:
                errors.append(f"Грешка при обработка на лист {sheet_name}: {str(e)}")

        message = "\n".join(
            ["Импортът завърши!", f"Създадени: {created_count}", f"Обновени: {updated_count}"] +
            (["", "Грешки:"] + [f"  {err}" for err in errors] if errors else [])
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Импортът завърши",
                "message": message,
                "type": "success" if not errors else "warning",
                "sticky": True
            }
        }


class TrinityNomenclatureImportNhis(models.TransientModel):
    _name = 'trinity.nomenclature.import.nhis'
    _description = 'Импорт на номенклатури от НЗОК'
    _rec_name = 'id'

    xml_data = fields.Binary(string='XML отговор', readonly=True, filename='response.xml')
    csv_data = fields.Binary(string='CSV данни', readonly=True)
    nomenclature_request = fields.Text(string='Заявка за номенклатура', copy=False)
    nomenclature_response = fields.Text(string='Отговор за номенклатура', copy=False)

    def _generate_request_xml(self, nomenclature_id):
        current_datetime_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        uuid_value = str(uuid.uuid4())

        return f"""
        <nhis:message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                      xmlns:nhis="https://www.his.bg"
                      xsi:schemaLocation="https://www.his.bg https://www.his.bg/api/v1/NHIS-X013.xsd">
            <nhis:header>
                <nhis:sender value="1"/>
                <nhis:senderId value="2300011682"/>
                <nhis:senderISName value="Supermed 1.0.1"/>
                <nhis:recipient value="4"/>
                <nhis:recipientId value="NHIS"/>
                <nhis:messageId value="{uuid_value}"/>
                <nhis:messageType value="C001"/>
                <nhis:createdOn value="{current_datetime_str}"/>
            </nhis:header>
            <nhis:contents>
                <nhis:nomenclatureId value="{nomenclature_id}"/>
            </nhis:contents>
        </nhis:message>"""

    def _send_request(self, nomenclature_id, model_name):
        self.xml_data = False
        self.csv_data = False
        self.nomenclature_request = False
        self.nomenclature_response = False

        request_xml = self._generate_request_xml(nomenclature_id)
        self.nomenclature_request = request_xml

        headers = {'Content-Type': 'application/xml'}
        response = requests.post('https://api.his.bg/v1/nomenclatures/all/get',
                                 headers=headers, data=request_xml.encode('utf-8'))

        if response.status_code == 200:
            self.xml_data = base64.b64encode(response.text.encode())
            self._process_response(model_name)
        else:
            self.xml_data = base64.b64encode(f"Error: {response.status_code}".encode())

    def _extract_json_from_xml(self, decoded_xml):
        ns = {'nhis': 'https://www.his.bg'}
        json_data = []
        try:
            for event, elem in ET.iterparse(BytesIO(decoded_xml), events=('end',)):
                if elem.tag == f'{{{ns["nhis"]}}}entry':
                    key = elem.find('.//nhis:key', ns)
                    description = elem.find('.//nhis:description', ns)
                    key_value = key.get('value') if key is not None else None
                    description_value = description.get('value') if description is not None else None

                    record_data = {'key': key_value, 'description': description_value}

                    for meta in elem.findall('.//nhis:meta', ns):
                        name = meta.find('.//nhis:name', ns).get('value', '')
                        value = meta.find('.//nhis:value', ns).get('value', '')
                        field_name = f"meta_{name.lower().replace(' ', '_')}"
                        record_data[field_name] = value

                    json_data.append(record_data)
                    elem.clear()
        except ET.ParseError as e:
            _logger.error(f"Грешка при парсиране на XML: {str(e)}")
        except Exception as e:
            _logger.error(f"Грешка при обработка: {str(e)}")

        return json_data

    def _extract_csv_from_xml(self, decoded_xml):
        ns = {'nhis': 'https://www.his.bg'}
        csv_data = []
        all_fields = set()

        try:
            for event, elem in ET.iterparse(BytesIO(decoded_xml), events=('end',)):
                if elem.tag == f'{{{ns["nhis"]}}}entry':
                    key = elem.find('.//nhis:key', ns)
                    description = elem.find('.//nhis:description', ns)
                    key_value = key.get('value') if key is not None else None
                    description_value = description.get('value') if description is not None else None

                    record_data = {'key': key_value, 'description': description_value}

                    for meta in elem.findall('.//nhis:meta', ns):
                        name = meta.find('.//nhis:name', ns).get('value', '')
                        value = meta.find('.//nhis:value', ns).get('value', '')
                        field_name = f"meta_{name.lower().replace(' ', '_')}"
                        record_data[field_name] = value
                        all_fields.add(field_name)

                    csv_data.append(record_data)
                    elem.clear()
        except ET.ParseError as e:
            _logger.error(f"Грешка при парсиране на XML: {str(e)}")
        except Exception as e:
            _logger.error(f"Грешка при обработка: {str(e)}")

        return csv_data, list(all_fields)

    def _process_response(self, model_name):
        decoded_xml = base64.b64decode(self.xml_data)
        nomenclature_id = model_name.split('.')[-1].upper()

        json_data = self._extract_json_from_xml(decoded_xml)
        csv_data, csv_fields = self._extract_csv_from_xml(decoded_xml)

        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        json_b64 = base64.b64encode(json_str.encode('utf-8'))

        csv_buffer = BytesIO()
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
            csv_b64 = base64.b64encode(csv_buffer.getvalue()).decode()
        else:
            csv_b64 = ""

        vals = {
            'cl_value': nomenclature_id,
            'xml_data': self.xml_data,
            'json_data': json_b64,
            'json_data_rows': len(json_data),
            'csv_data': csv_b64,
            'description': f'NHIS отговор за {nomenclature_id}',
            'is_from_nhif': True,
        }

        existing_record = self.env['trinity.nomenclature'].search([
            ('cl_value', '=', nomenclature_id),
            '|', ('active', '=', True), ('active', '=', False)
        ], limit=1)
        if existing_record:
            existing_record.write(vals)
            _logger.info(f"Обновен съществуващ запис за номенклатура {nomenclature_id}")
        else:
            self.env['trinity.nomenclature'].create(vals)
            _logger.info(f"Създаден нов запис за номенклатура {nomenclature_id}")

    def post_all_nomenclature_requests(self):
        for cl_model in CL_MODELS:
            try:
                model_name = f"trinity.nomenclature.{cl_model.lower()}"
                self._send_request(cl_model, model_name)
                _logger.info(f"Успешно изпълнена заявка за {cl_model}")
            except Exception as e:
                _logger.error(f"Грешка при изпълнение на заявка за {cl_model}: {str(e)}")


class TrinityCSVImport(models.TransientModel):
    _name = 'trinity.csv.import'
    _description = 'CSV Import'

    target_model = fields.Many2one('ir.model', string="Target Model", required=True)
    file = fields.Binary(string="CSV File", required=True)
    filename = fields.Char("Filename")

    def action_import_csv(self, batch_size=500):
        self.ensure_one()
        if not self.file or not self.target_model:
            raise ValidationError(_("Моля, предоставете CSV данни и изберете целеви модел."))

        try:
            df = pd.read_csv(BytesIO(base64.b64decode(self.file)))
        except Exception as e:
            raise ValidationError(_("Неуспешно парсиране на CSV: %s") % e)

        df = df.dropna(how='all')
        rows = df.to_dict("records")

        model = self.env[self.target_model.model]
        model_fields = model._fields

        all_errors, total_created, total_updated = [], 0, 0
        to_create, to_update = [], []

        m2o_cache = {}

        def m2o_find(rel_model, search_value):
            key = (rel_model._name, search_value)
            if key in m2o_cache:
                return m2o_cache[key]

            record = False
            lookup_fields = [rel_model._rec_name or "name", "name", "code"]
            for f in lookup_fields:
                if f in rel_model._fields:
                    try:
                        record = rel_model.search([(f, "=", search_value)], limit=1)
                        if record:
                            break
                    except Exception:
                        continue

            if not record and "name" in rel_model._fields:
                try:
                    record = rel_model.search([("name", "ilike", search_value)], limit=1)
                except Exception:
                    pass

            m2o_cache[key] = record.id if record else None
            return m2o_cache[key]

        def convert_value(field, value, row_idx, field_name):
            try:
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    return None

                if field.type == "many2one":
                    search_value = str(value).strip()
                    if not search_value:
                        return None
                    rel_model = self.env[field.comodel_name]
                    rec_id = m2o_find(rel_model, search_value)
                    if not rec_id:
                        all_errors.append(
                            f"Ред {row_idx}: Не е намерен запис за '{field_name}' = '{search_value}'"
                        )
                    return rec_id

                if field.type in ["char", "text", "selection"]:
                    return str(int(value)) if isinstance(value, float) and value.is_integer() else str(value).strip()

                if field.type == "integer":
                    return int(str(value).replace(",", ""))

                if field.type == "float":
                    return float(str(value).replace(",", ""))

                if field.type == "boolean":
                    return str(value).strip().lower() in ["1", "true", "t", "y", "yes"]

                if field.type == "date":
                    return str(value).strip()

                return str(value).strip()

            except Exception as e:
                all_errors.append(
                    f"Ред {row_idx}, поле '{field_name}': неуспешно конвертиране на '{value}' ({e})"
                )
                return None

        for i, row in enumerate(rows, 1):
            if not isinstance(row, dict):
                all_errors.append(f"Ред {i}: Невалидни данни - очаква се речник")
                continue

            vals = {}
            for field_name, value in row.items():
                if not isinstance(field_name, str) or field_name not in model_fields or field_name == "id":
                    continue
                field = model_fields[field_name]
                if field.type == "one2many":
                    continue

                converted = convert_value(field, value, i, field_name)
                if converted is not None:
                    vals[field_name] = converted

            existing_rec = None
            xmlid = str(row.get("id") or "").strip()
            if xmlid:
                rec_id = self.env["ir.model.data"]._xmlid_to_res_id(xmlid, raise_if_not_found=False)
                if rec_id:
                    existing_rec = model.browse(rec_id)

            if not existing_rec and model._rec_name in row:
                rec_name_value = str(row[model._rec_name]).strip()
                if rec_name_value:
                    try:
                        existing_rec = model.search([(model._rec_name, "=", rec_name_value)], limit=1)
                    except Exception:
                        pass

            if existing_rec and existing_rec.exists():
                to_update.append((existing_rec, vals))
            else:
                to_create.append(vals)

            if len(to_create) >= batch_size:
                try:
                    model.create(to_create)
                    total_created += len(to_create)
                except Exception as e:
                    all_errors.append(f"Неуспешно създаване на партида при ред {i}: {e}")
                finally:
                    to_create = []

            if len(to_update) >= batch_size:
                for rec, v in to_update:
                    try:
                        rec.write(v)
                    except Exception as write_error:
                        rec_id = getattr(rec, "id", "Unknown")
                        rec_name = getattr(rec, "name", rec_id)
                        all_errors.append(f"Неуспешно обновяване {rec_name}: {write_error}")
                total_updated += len(to_update)
                to_update = []

        if to_create:
            try:
                model.create(to_create)
                total_created += len(to_create)
            except Exception as e:
                all_errors.append(f"Неуспешно финално създаване: {e}")

        if to_update:
            for rec, v in to_update:
                try:
                    rec.write(v)
                except Exception as write_error:
                    rec_id = getattr(rec, "id", "Unknown")
                    rec_name = getattr(rec, "name", rec_id)
                    all_errors.append(f"Неуспешно обновяване {rec_name}: {write_error}")
            total_updated += len(to_update)

        message = [
            f"Обработени {len(rows)} реда",
            f"Създадени: {total_created}",
            f"Обновени: {total_updated}",
        ]
        if all_errors:
            message.extend(["", "Грешки:"] + all_errors[:10])
            if len(all_errors) > 10:
                message.append(f"...и още {len(all_errors)-10} грешки")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("CSV Импорт"),
                "message": "\n".join(message),
                "type": "success" if not all_errors else "warning",
                "sticky": True,
            },
        }

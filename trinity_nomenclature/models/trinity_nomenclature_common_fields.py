from odoo import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class TrinityNomenclatureCommonFields(models.AbstractModel):
    _name = "trinity.nomenclature.common.fields"
    _description = "Trinity Nomenclature Common Fields"

    name = fields.Char(string='Име', store=True, compute='compute_name_field')
    active = fields.Boolean(string='Активен', compute='_compute_active', store=True)
    key = fields.Char(string='Key', required=True, index=True)
    description = fields.Char(string='Description', required=True)
    valid_since_version = fields.Char(string='Valid Since Version')
    valid_until_version = fields.Char(string='Valid Until Version')
    current_version = fields.Char(string='Current Version')

    @api.depends('key','description')
    def compute_name_field(self):
        for record in self:
            record.name = f"{record.key} - {record.description}"

    @api.depends('current_version', 'valid_since_version', 'valid_until_version')
    def _compute_active(self):
        for record in self:
            if not record.current_version:
                record.active = True
                continue

            current = record.current_version
            since = record.valid_since_version or ''
            until = record.valid_until_version or ''

            since_is_date = since and not since.strip().lower().startswith('v')
            until_is_date = until and not until.strip().lower().startswith('v')

            if since_is_date or until_is_date:
                current_date = fields.Date.today()

                since_valid = True
                if since_is_date:
                    since_date = self._parse_date(since)
                    since_valid = not since_date or current_date >= since_date
                else:
                    since_valid = not since or self._compare_versions(current, since) >= 0

                until_valid = True
                if until_is_date:
                    until_date = self._parse_date(until)
                    until_valid = not until_date or current_date < until_date
                else:
                    until_valid = not until or self._compare_versions(current, until) < 0

                record.active = since_valid and until_valid
            else:

                since_valid = not since or self._compare_versions(current, since) >= 0
                until_valid = not until or self._compare_versions(current, until) < 0
                record.active = since_valid and until_valid

    def _parse_date(self, date_str):

        if not date_str:
            return None
        try:
            date_obj = datetime.strptime(date_str.strip(), '%d.%m.%Y').date()
            return date_obj
        except ValueError:
            _logger.warning("Failed to parse date '%s' (expected format: dd.mm.yyyy)", date_str)
            return None

    def _compare_versions(self, version1, version2):
        if not version1 or not version2:
            return 0
        try:
            v1_parts = [int(x) for x in version1.strip().lstrip('v').split('.')]
            v2_parts = [int(x) for x in version2.strip().lstrip('v').split('.')]
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0]*(max_len - len(v1_parts)))
            v2_parts.extend([0]*(max_len - len(v2_parts)))
            for a,b in zip(v1_parts, v2_parts):
                if a < b: return -1
                elif a > b: return 1
            return 0
        except Exception:
            _logger.warning("Failed to parse versions '%s' or '%s'", version1, version2)
            return (version1 > version2) - (version1 < version2)

    _sql_constraints = [
        ('unique_key', 'UNIQUE(key)', 'Key must be unique!')
    ]

    @api.model
    def delete_duplicate_records_based_on_key(self):
        table_name = self._table
        query = f"""
            WITH duplicates AS (
                SELECT id
                FROM (
                    SELECT id,
                        ROW_NUMBER() OVER (PARTITION BY lower(coalesce(key, '')) ORDER BY id) AS rn
                    FROM {table_name}
                ) t
                WHERE t.rn > 1
            )
            DELETE FROM {table_name}
            WHERE id IN (SELECT id FROM duplicates)
            RETURNING id;
        """
        self.env.cr.execute(query)
        deleted_ids = self.env.cr.fetchall()
        total_deleted = len(deleted_ids)
        return total_deleted


    @api.constrains('key')
    def restrict_duplicates(self):
        for rec in self:
            duplicates = self.env[rec._name].search([
                ('key', '=', rec.key),
                ('id', '!=', rec.id),
                '|', ('active', '=', True), ('active', '=', False)
            ])

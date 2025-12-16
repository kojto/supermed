from odoo import models, fields

class TrinityCommunicator(models.Model):
    _name = 'trinity.communicator'
    _description = 'Trinity Communicator'
    _rec_name = 'action_name'
    _order = 'action_name desc'

    active = fields.Boolean(string='Активен', default=True)
    is_for_testing = fields.Boolean(string='За тестване', default=False)
    action_name = fields.Char(string='Име на действието')
    field_origin = fields.Char(string='Изходно поле')
    field_origin_raw = fields.Char(string='Изходно поле в raw формат')
    field_response = fields.Char(string='Отговорно поле')
    url_value = fields.Char(string='URL')
    lrn_origin_field = fields.Char(string='LRN изходно поле')

    def write(self, vals):
        result = super().write(vals)

        if 'is_for_testing' in vals:
            for record in self:
                if record.url_value:
                    if vals['is_for_testing']:
                        if record.url_value.startswith('https://'):
                            record.url_value = record.url_value.replace('https://', 'https://ptest-', 1)
                    else:
                        if record.url_value.startswith('https://ptest-'):
                            record.url_value = record.url_value.replace('https://ptest-', 'https://', 1)

        return result

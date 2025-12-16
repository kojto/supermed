from odoo import api, fields, models
import requests

class TrinityRequests(models.Model):
    _name = 'trinity.requests'
    _description = 'Заявки'

    field_origin = fields.Text(string='Заявка')
    field_response = fields.Text(string='Отговор')
    url = fields.Char(string='URL')
    access_token = fields.Text(string='Access Token')

    def make_api_post_request(self):
        headers = {
            'Content-Type': 'application/xml',
            'Authorization': f'Bearer {self.access_token}',
        }

        field_origin_value = self.field_origin.encode('utf-8')

        try:
            response = requests.post(self.url, data=field_origin_value, headers=headers)
            self.field_response = response.text
        except Exception as e:
            self.field_response = str(e)

        return True
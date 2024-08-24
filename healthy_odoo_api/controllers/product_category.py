import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import json
from pprint import pprint
import requests
from .settings import _validate_data


class Category(http.Controller):
    def config_data(self):
        return {
            'db': 'Healthy-production',
            'username': 'admin',
            'password': '@@131412',
            'url': 'http://147.182.192.42:2022',
            'HealthyToken': 'k87d5883-8344-4623-u763-7n46449a'
        }

    def dev_config_data(self):
        return {
            'db': 'Healthy-Live1',
            'username': 'admin',
            'password': 'Admin@2',
            'url': 'http://138.68.105.65:2022',
            'HealthyToken': 'k87d5883-8344-4623-u763-7n46449a'
        }

    @http.route('/api/v1/get_all_categories', type='json', auth='public', methods=['POST'])
    def get_all_category(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['product.category'].sudo().search([('id', '>=', data.get('id'))],
                                                                       limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(model_data))
        return json.loads(json.dumps(response))

    def get_data(self, record):
        return {
            "odoo_id": record.id,
            "name": record.name,
            "parent_category_id": record.parent_id.id,
            "parent_category_name": record.parent_id.name,
        }

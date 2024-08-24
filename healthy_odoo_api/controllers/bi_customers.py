import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data
from  dateutil.relativedelta import relativedelta


class Customers(http.Controller):

    @http.route('/api/v1/bi_get_customers', type='json', auth='public', methods=['POST'])
    def bi_get_customers(self, *kw,**args):
        response = {}
        relational_fields={}
        required_parameter = ['token','limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['res.partner'].sudo().search([('id', '>=', data.get('id')),('customer', '=', True)], limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print(model_data)
        return json.loads(json.dumps(response)) 

    def get_data(self, record):
        return {
            "customer_id": record.id,
            "customer_name": record.name,
            "customer_phone": record.phone,
            "customer_complete_address": self.get_address(record),
            "customer_created_on": "{}".format(record.create_date+relativedelta(hours=2)),
            "company_id": record.branch_id.id,
            "company_display_name": record.branch_id.name
        }

    def get_address(self, object):
        if object.street and object.street2:
            address = "{} {}".format(object.street , object.street2)
        elif object.street and not object.street2:
            address = object.street
        elif not object.street and object.street2:
            address = object.street2
        else:
            address = None
        return address

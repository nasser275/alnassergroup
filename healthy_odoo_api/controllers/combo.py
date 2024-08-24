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


class Combo(http.Controller):

    @http.route('/api/v1/get_available_combo', type='json', auth='public', methods=['GET'])
    def get_available_combo(self, *kw,**args):
        response = {}
        relational_fields={}
        required_parameter = ['token']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['product.product'].sudo().search([('is_combo','=',True)], order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print(model_data)
        return json.loads(json.dumps(response))

    def get_data(self, record):
        return {
            "odoo_id": record.id,
            "combo_name": record.name,
            # 'combo_available': record.check_lload(),

        }



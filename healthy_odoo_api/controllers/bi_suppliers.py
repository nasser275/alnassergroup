import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data


class Suppliers(http.Controller):

    @http.route('/api/v1/bi_get_suppliers', type='json', auth='public', methods=['POST'])
    def bi_get_suppliers(self, *kw,**args):
        response = {}
        relational_fields={}
        required_parameter=['token', 'limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['res.partner'].sudo(2).search([('id', '>=', data.get('id')),('supplier', '=', True), ('parent_id', '=', False)], limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("suppliers count ---->", len(final_data_list))
        # return json.dumps(response)
        return json.loads(json.dumps(response)) 

    def get_data(self, record):
        return {
            "supplier_id": record.id,
            "supplier_code": record.supplier_code or None,
            "name": record.name,
            "city": record.city,
            "category": None,
            "discount_from": record.discount_from or None,
            "discount_to": record.discount_to or None,
            "payment": record.payment_days or 0,
            "delivery": None,
            "replenishment":record.replenishment or None,
            "label": record.label or None,
            "start_date": "{}".format(record.start_date) or None,
            "end_date": "{}".format(record.end_date) or None,
            "contract": None,
            "status": "Active" if record.active else "Inactive",
            "notes": record.comment or None,
            "consignment": record.consignment,
            "returns_per": record.returns_per,
        }

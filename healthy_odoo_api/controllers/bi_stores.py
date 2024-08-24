import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data


class Stores(http.Controller):

    @http.route('/api/v1/bi_get_stores', type='json', auth='public', methods=['POST'])
    def bi_get_stores(self, *kw,**args):
        response = {}
        relational_fields={}
        required_parameter=['token', 'limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['res.company'].sudo().search([('id', '>=', data.get('id'))], limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print(model_data)
        return json.loads(json.dumps(response)) 

    def get_data(self, record):
        return {
            "store_id": record.id,
            "country": record.country_id.name or None,
            "region": record.region_id.name or None,
            "governorate": record.state_id.name or None,
            "area": record.area_id.name or None,
            "city": record.city or None,
            "store_Name": record.name or None,
            "adress": self.get_address(record),
            "luanching_date": "{}".format(record.luanching_date) if record.luanching_date else None,
            "branch_area_m2": record.branch_area_m2,
            "contracted_date":  "{}".format(record.contracted_date) if record.contracted_date else None,
            "end_of_contracted_date": "{}".format(record.contracted_end_date) if record.contracted_end_date else None,
            "module": record.module_id.name or None,
            "status": record.status or None,
            "closed_Date": "{}".format(record.closing_date) if record.closing_date else None,
            "rent_amount": record.rent_Amount or 0,
            "location_rank": record.location_rank,
            "num_of_staff": record.num_of_staff or 0,
            "license_num": record.license_number or None,
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

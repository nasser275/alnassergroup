import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data


class Inventory(http.Controller):

    @http.route('/api/v1/bi_get_inventory', type='json', auth='public', methods=['POST'])
    def bi_get_inventory(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token','limit']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        model_data = []
        if not response.get('message', False):
            domian = self.search_domian(data)
            if domian:
                model_data = request.env['stock.quant'].sudo().search(domian, limit=data.get('limit'), order='id')
            final_data_list = []
            if model_data:
                for record in model_data:
                    final_data_list.append(self.get_data(record))
        response['results'] = final_data_list
        pprint(response)
        print("records count -> ", len(model_data))
        return json.loads(json.dumps(response)) 

    def get_locations_by_company_id(self, company_id=False):
        if company_id:
            ids = request.env['stock.location'].sudo().search([('company_id', '=', company_id)])
            print('location ids ---------->', ids)
        else:
            ids = request.env['stock.location'].sudo().search([('id', '>', 1)])
            print('location ids else ---------->', ids)
        return ids

    def search_domian(self, data):
        domain = []
        location_ids = self.get_locations_by_company_id()
        if location_ids:
            domain += [('location_id', 'in', location_ids.ids), ('company_id', '!=', False),('id', '>=', data.get('id'))]
        else:
            domain = [('company_id', '!=', False), ('id', '>=', data.get('id'))]
        print('domain', domain)
        return domain

    def get_data(self, record):
        return {
            "stock_id": record.id,
            "stock_product_id": record.product_id.id,
            "stock_product_name": record.product_id.name,
            "company_id": record.branch_id.id,
            "company_name": record.branch_id.name,
            "vendor_id": record.product_id.supplier_id.id or None,
            "vendor_name": record.product_id.supplier_id.name or None,
            "on_hand_quantity": record.quantity,
            "cost": record.product_id.standard_price,
            "price": record.product_id.lst_price,
        }

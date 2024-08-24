import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data


class PackProducts(http.Controller):



    def get_product_from_temp(self,bi_product_template):
        print("bi_product_template",bi_product_template)
        return request.env['product.product'].sudo().search([('product_tmpl_id','=',bi_product_template)],limit=1)


    @http.route('/api/v1/bi_get_pack_products', type='json', auth='public', methods=['POST'])
    def bi_get_products(self, *kw,**args):
        response = {}
        relational_fields={}
        required_parameter=['token', 'limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['product.pack'].sudo().search([('id', '>=', data.get('id'))], limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                product_id = self.get_product_from_temp(record.bi_product_template.id)
                if product_id.active:
                    final_data_list.append(self.get_data(product_id,record))
            response['results'] = final_data_list
            print("records count -> ",len(model_data))
        return json.loads(json.dumps(response)) 

    def get_data(self,product_id, record):
            return {
              "product_id":product_id.id,
              "product_pack_id":record.product_id.id,
              "product_pack_name":record.product_id.name,
              "quantity":record.qty_uom,
            }

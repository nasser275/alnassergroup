import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import json
from pprint import pprint
import requests
from .settings import _validate_data


class Products(http.Controller):
    def config_data(self):
        return {
            'db': 'Healthy-production',
            'username': 'admin',
            'password': '@@131412',
            'url': 'http://157.230.96.56:2244',
            'HealthyToken': 'k87d5883-8344-4623-u763-7n46449a'
        }

    def dev_config_data(self):
        return {
            'db': 'healthy2022-3',
            'username': 'admin',
            'password': '@@131412',
            'url': 'http://147.182.192.42:2022',
            'HealthyToken': 'k87d5883-8344-4623-u763-7n46449a'
        }

    @http.route('/api/v1/get_products_price', type='json', auth='public', methods=['POST'])
    def get_products_price(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['product.product'].sudo().search([('id', '>=', data.get('id'))],
                                                                      limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(model_data))
        return json.loads(json.dumps(response))

    def get_data(self, record):
        # we will make this pricelist selected from inteface in the future
        pricelist = request.env['product.pricelist'].sudo().search([('id', '=', 1)])
        unit_price = pricelist.get_product_price(record, 1, False)
        return {
            "product_id": record.id,
            "price": unit_price
        }

    @http.route('/api/v1/get_all_products_by_company', type='json', auth='public', methods=['POST'])
    def index(self, **args):
        response = {}
        config = self.config_data()
        data = args
        print('args,kw ============>', data)
        current_user = request.env.user
        print('current_user ============>', current_user)
        response = self.validate_data(data)
        if not response.get('message', False):
            stock_quant_fields = ['product_id', 'company_id', 'quantity', 'branch_id']
            product_fields = ['name', 'company_id', 'qty_available', 'branch_id']
            list_data = []
            if data.get('branch_id') > 0:
                found_company = request.env['res.branch'].sudo().search([('id', '=', data.get('branch_id'))], limit=1)
                if found_company:
                    location_ids = self.get_locations_by_company_id(found_company.id)
                    print('location_ids', location_ids)
                    result = request.env['stock.quant'].sudo().search_read([('location_id', 'in', location_ids.ids)],
                                                                           fields=stock_quant_fields)
                    for line in result:
                        list_data.append({'branch_id': line.get('branch_id', False)[0],
                                          'product_id': line.get('product_id', False)[0],
                                          'quantity': line.get('quantity', 0.0)})
                    response['result'] = list_data
                    response['status'] = 200
                    response['message'] = "Success."
            else:
                location_ids = self.get_locations_by_company_id()
                print('location_ids', location_ids)
                result = request.env['stock.quant'].sudo().search_read([('location_id', 'in', location_ids.ids)],
                                                                       fields=stock_quant_fields)
                for line in result:
                    list_data.append(
                        {'company_id': line.get('company_id', False)[0], 'product_id': line.get('product_id', False)[0],
                         'quantity': line.get('quantity', 0.0)})
                response['result'] = list_data
                # response['result'] = api.api_search_read(table='stock.quant', domain=[('location_id', 'in', location_ids)], fields=stock_quant_fields)
                response['status'] = 200
                response['message'] = "Success."
        pprint(response)
        return json.loads(json.dumps(response))

    @http.route('/api/v1/get_last_month_created_products', type='json', auth='public', methods=['POST'])
    def get_last_month_created_products(self, *args, **kwargs):
        data = kwargs
        print('args,kw ============>', args, kwargs)
        response = self.validate_data_for_creating_product_from_specific_date(data)
        if not response.get('message', False):
            list_data = []
            products = request.env['product.product'].sudo().search([('create_date', '>=', data.get('datetime'))],
                                                                    limit=data.get('limit'))
            print('products', products)
            if products:
                url_crud = 'http://admin.healthyandtasty.net/api/v1/crud_product'
                for product in products:
                    data = self.mapping_product_create(product)
                    if data and url_crud:
                        try:
                            request_response = requests.post(url_crud, data)
                            list_data.append(product.id)
                            print("Response: %s , status: %s" % (request_response.text, request_response.status_code))
                        except Exception as e:
                            print(e)
            response['result'] = list_data
            response['status'] = 200
            response['message'] = "Success."
        pprint(response)
        return json.loads(json.dumps(response))

    @http.route('/api/v1/get_products_data_by_ids', type='json', auth='public', methods=['GET'])
    def get_products_data_by_ids(self, *args, **kwargs):
        relational_fields = {}
        required_parameter = ['token']
        data = http.request.jsonrequest
        response1 = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        print('args,kw ============>', args, kwargs)
        response = self.validate_data_product_ids_api(data)
        if not response1.get('message', False):
            if not response.get('message', False):
                list_data = []
                products = request.env['product.product'].sudo().search([('id', 'in', data.get('product_ids'))])
                print('products', products)
                for record in products:
                    if record.active:
                        data = record.mapping_product_update()
                        list_data.append(data)
                print(list_data)
                response['results'] = list_data
                response['status'] = 200
                response['message'] = "Success."
            pprint(response)
        return json.loads(json.dumps(response))

    def mapping_product_create(self, product):
        return {
            "odoo_id": product.id,
            "name": product.name,
            "price": product.list_price,
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }

    def get_locations_by_company_id(self, branch_id=False):
        if branch_id:
            ids = request.env['stock.location'].sudo().search([('branch_id', '=', branch_id)])
            print('location ids ---------->', ids)
        else:
            ids = request.env['stock.location'].sudo().search([('id', '>', 1)])
            print('location ids else ---------->', ids)
        return ids

    def validate_data(self, data):
        response = {}
        config = self.config_data()
        if not 'token' in data:
            response['message'] = 'token parameter is missing.'
            response['status'] = 500
        if not 'company_id' in data:
            response['message'] = 'company_id parameter is missing.'
            response['status'] = 500
        if not data.get('token') == config['HealthyToken']:
            print("data.get('token') == config['HealthyToken']", data.get('token') == config['HealthyToken'])
            response['result'] = []
            response['message'] = 'Invalid token.'
            response['status'] = 301
        if data.get('company_id') and data.get('company_id') > 0:
            found_company = request.env['res.company'].sudo().search([('id', '=', data.get('company_id'))], limit=1)
            if not found_company:
                response['result'] = []
                response['message'] = "Company id not found in database please insert correct id."
                response['status'] = 404
        return response

    def validate_data_for_creating_product_from_specific_date(self, data):
        response = {}
        config = self.config_data()
        if not 'token' in data:
            response['message'] = 'token parameter is missing.'
            response['status'] = 500
        if not 'datetime' in data:
            response['message'] = 'datetime parameter is missing.'
            response['status'] = 500
        if not 'limit' in data:
            response['message'] = 'limit parameter is missing.'
            response['status'] = 500
        if data.get('token') != config['HealthyToken']:
            print("data.get('token') == config['HealthyToken']", data.get('token') == config['HealthyToken'])
            response['result'] = []
            response['message'] = 'Invalid token.'
            response['status'] = 301
        return response

    def validate_data_product_ids_api(self, data):
        response = {}
        config = self.config_data()
        if not 'token' in data:
            response['message'] = 'token parameter is missing.'
            response['status'] = 500
        if not 'product_ids' in data:
            response['message'] = 'product_ids parameter is missing.'
            response['status'] = 500
        if data.get('token') != config['HealthyToken']:
            print("data.get('token') == config['HealthyToken']", data.get('token') == config['HealthyToken'])
            response['result'] = []
            response['message'] = 'Invalid token.'
            response['status'] = 301
        return response

    @http.route('/api/v1/get_all_products', type='json', auth='public', methods=['POST'])
    def get_all_products(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['product.product'].sudo().search([('id', '>=', data.get('id'))],
                                                                      limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_product_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(model_data))
        return json.loads(json.dumps(response))

    def get_product_data(self, record):
        return {
            "odoo_id": record.id,
            "name": record.name,
            "price": record.list_price,
            "can_be_sold": record.sale_ok,
            "categ_id": record.categ_id.id,
            "categ_name": record.categ_id.name,
        }

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


class Products(http.Controller):



    def get_history_price(self, company_id, product_id ,date=None):
        history = request.env['product.price.history'].sudo().search([
            ('company_id', '=', company_id),
            ('product_id', '=', product_id),
            ('datetime', '<=', date or datetime.now())], order='datetime desc,id desc', limit=1)
        return history.cost or 0.0

    @http.route('/api/v1/bi_get_products', type='json', auth='public', methods=['POST'])
    def bi_get_products(self, *kw,**args):
        response = {}
        relational_fields={}
        required_parameter=['token', 'limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['product.product'].sudo().search([('id', '>=', data.get('id'))], limit=data.get('limit'), order='id')
            final_data_list = []
            for record in model_data:
                final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ",len(model_data))
        return json.loads(json.dumps(response)) 

    def get_data(self, record):
        return {
            "product_id": record.id,
            "category_1": record.categ_full_path,
            "category_2": None,
            "category_3": None,
            "category_id": record.categ_id.parent_id.id,
            "flavor": record.flavor_id.name or None,
            "supplier": record.supplier_id.id or None,
            "sku_name_english": record.sku_name_english or None,
            "sku_name_Arabic": record.name or None,
            "supplier_name": record.supplier_id.name or None,
            "original_supplier_id": record.original_supplier_id.id or None,
            "original_supplier_name": record.original_supplier_id.name or None,
            "supplier_item_code": None,
            "sku_code": None,
            "description": record.description,
            "discontinued": 'Yes' if record.active else 'No',
            "shelf_life": record.shelf_life or None,
            "size": record.size or None,
            "weight": record.healty_weight or None,
            "height": record.height or None,
            "base_width": record.base_width or None,
            "base_depth": record.base_depth or None,
            "container_type": record.container_type_id.name or None,
            "container_shape": record.container_shape_id.name or None,
            "container_material": record.container_material_id.name or None,
            "color": record.color_id.name or None,
            "low_carb": record.low_carb,
            "low_protein": record.low_brotein,
            "pbd": record.pbd,
            "vegeterian": record.vegeterian,
            "odor_less": record.odor_less,
            "content_type": record.content_type_id.name or None,
            "storage_type": record.storage_type_id.name or None,
            "storage_temprature": record.storage_temprature,
            "measurement_unit": record.uom_id.name,
            "calories": record.calories,
            "sugar": record.sugar,
            "sodium": record.sodium,
            "product_nature": record.product_nature,
            "created_on": "{}".format(record.create_date+relativedelta(hours=2)),
            "original_cost": self.get_history_price(22, record.id),
            "original_cost_1": None,
            "original_cost_2": None,
            "cost_1": record.standard_price,
            "cost_2": None,
            "cost_3": None,
            "price_1": record.lst_price,
            "price_2": None,
            "price_3": None,
            "status": "Active" if record.active else "Inactive",
            "is_pack":record.is_pack,
            "price_changing_date": "{}".format(record.price_changing_date + relativedelta(hours=2)) if record.price_changing_date else None,
            "last_change_price":record.last_change_price,
            "product_name_net":record.product_name_net,
            "can_be_sold":record.sale_ok,
            "can_be_purchased":record.purchase_ok,
            "stock_moves":request.env['stock.move.line'].sudo().search_count([('product_id', '=', record.id),('state','=','done')])

        }


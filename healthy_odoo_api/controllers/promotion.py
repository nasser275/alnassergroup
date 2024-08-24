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


class Promotion(http.Controller):

    @http.route('/api/v1/get_available_promotion', type='json', auth='public', methods=['GET'])
    def get_available_combo(self, *kw,**args):
        response = {}
        relational_fields={}
        required_parameter = ['token']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['pos.promotion'].sudo().search([], order='id')
            final_data_list = []
            for record in model_data:
                if record.promotion_type == 'quantity_discount':
                    for line in record.pos_quntity_ids:
                        final_data_list.append({
                            "odoo_id": record.id,
                            "promotion_code": record.promotion_code,
                            "promotion_type": record.promotion_type,
                            "from_date": str(record.from_date),
                            "to_date": str(record.to_date),
                            "product_id": record.product_id_qty.id,
                            "product_name": record.product_id_qty.name,
                            "quantity_dis": line.quantity_dis,
                            "discount": line.discount_dis,

                        })
                if record.promotion_type == 'discount_on_multi_product':
                    for line in record.multi_products_discount_ids:
                        for product in line.product_ids:
                            final_data_list.append({
                                "odoo_id": record.id,
                                "promotion_code": record.promotion_code,
                                "promotion_type": record.promotion_type,
                                "from_date": str(record.from_date),
                                "to_date": str(record.to_date),
                                "product_id": product.id,
                                "product_name": product.name,
                                "discount": line.products_discount,

                            })
                if record.promotion_type == 'discount_on_multi_categ':
                    if record.filter_supplier:
                        for line in record.multi_categ_discount_ids:
                            for supplier in line.supplier_ids:
                                rres=request.env['product.product'].sudo().search([('supplier_id','=',supplier.id)])
                                for product in rres:
                                    final_data_list.append({
                                        "odoo_id": record.id,
                                        "promotion_code": record.promotion_code,
                                        "promotion_type": record.promotion_type,
                                        "from_date": str(record.from_date),
                                        "to_date": str(record.to_date),
                                        "product_id": product.id,
                                        "product_name": product.name,
                                        "discount": line.categ_discount,

                                    })
                    if record.filter_supplier==False:
                        for line in record.multi_categ_discount_ids:
                            for categ_id in line.categ_ids:
                                rres=request.env['product.product'].sudo().search([('categ_id','=',categ_id.id)])
                                for product in rres:
                                    final_data_list.append({
                                        "odoo_id": record.id,
                                        "promotion_code": record.promotion_code,
                                        "promotion_type": record.promotion_type,
                                        "from_date": str(str(record.from_date)),
                                        "to_date": str(record.to_date),
                                        "product_id": product.id,
                                        "product_name": product.name,
                                        "discount": line.categ_discount,
                                    })
            response['results'] = final_data_list
        return json.loads(json.dumps(response))





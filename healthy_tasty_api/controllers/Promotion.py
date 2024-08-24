# -*- coding: utf-8 -*-
from odoo import http,models,fields
from odoo.http import Controller, request, route
from .config import validate_data,get_image_url_for_prod
import json
class Promotion(http.Controller):

    @http.route('/api/v1/promotion', type='json', auth='public', methods=['GET'])
    def promotion(self, *kw, **args):
        response = {}
        data = http.request.jsonrequest
        token=data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        if not response.get('message', False):
            model_data = request.env['pos.promotion'].sudo().search([], order='id')
            final_data_list = []
            for record in model_data:
                if record.promotion_type == 'quantity_discount':
                    for line in record.pos_quantity_ids:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        image=get_image_url_for_prod(base, record.product_id_qty.id)
                        final_data_list.append({
                            "odoo_id": record.id,
                            "promotion_code": record.promotion_code,
                            "promotion_type": record.promotion_type,
                            "from_date": str(record.from_date),
                            "to_date": str(record.to_date),
                            "product_id": record.product_id_qty.id,
                            "product_name": record.product_id_qty.name,
                            "quantity_dis": line.quantity_dis,
                            "price_before_discount": record.product_id_qty.list_price,
                            "discount": line.discount_dis,
                            "price_after_discount": (record.product_id_qty.list_price -(record.product_id_qty.list_price * (line.discount_dis/100))) if line.discount_dis else record.product_id_qty.list_price,
                            "image": image,

                        })
                if record.promotion_type == 'discount_on_multi_product':
                    for line in record.multi_products_discount_ids:
                        for product in line.product_ids:
                            base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                            image = get_image_url_for_prod(base, product.id)
                            final_data_list.append({
                                "odoo_id": record.id,
                                "promotion_code": record.promotion_code,
                                "promotion_type": record.promotion_type,
                                "from_date": str(record.from_date),
                                "to_date": str(record.to_date),
                                "product_id": product.id,
                                "product_name": product.name,
                                "price_before_discount": product.list_price,
                                "discount": line.products_discount,
                                "price_after_discount": (product.list_price -(product.list_price * (line.products_discount/100))) if line.products_discount else product.list_price,
                                "image": image,

                            })
                if record.promotion_type == 'discount_on_multi_category':
                    if record.filter_supplier:
                        for line in record.multi_category_discount_ids:
                            for supplier in line.supplier_ids:
                                rres = request.env['product.product'].sudo().search([('supplier_id', '=', supplier.id)])
                                for product in rres:
                                    base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                    image = get_image_url_for_prod(base, product.id)
                                    final_data_list.append({
                                        "odoo_id": record.id,
                                        "promotion_code": record.promotion_code,
                                        "promotion_type": record.promotion_type,
                                        "from_date": str(record.from_date),
                                        "to_date": str(record.to_date),
                                        "product_id": product.id,
                                        "product_name": product.name,
                                        "price_before_discount":product.list_price,
                                        "discount": line.category_discount,
                                        "price_after_discount": (product.list_price - (product.list_price * (
                                                    line.category_discount / 100))) if line.category_discount else product.list_price,

                                        "image": image,

                                    })
                    if record.filter_supplier == False:
                        for line in record.multi_category_discount_ids:
                            for categ_id in line.category_ids:
                                rres = request.env['product.product'].sudo().search([('categ_id', '=', categ_id.id)])
                                for product in rres:
                                    base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                    image = get_image_url_for_prod(base, product.id)
                                    final_data_list.append({
                                        "odoo_id": record.id,
                                        "promotion_code": record.promotion_code,
                                        "promotion_type": record.promotion_type,
                                        "from_date": str(str(record.from_date)),
                                        "to_date": str(record.to_date),
                                        "product_id": product.id,
                                        "product_name": product.name,
                                        "price_before_discount": product.list_price,
                                        "discount": line.category_discount,
                                        "price_after_discount": (product.list_price - (product.list_price * (
                                                line.category_discount / 100))) if line.category_discount else product.list_price,
                                        "image": image,
                                    })
            response['results'] = final_data_list
        return json.loads(json.dumps(response))

import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from .settings import _validate_data
from dateutil.relativedelta import relativedelta
from datetime import datetime


class ProductsAv(http.Controller):

    @http.route('/api/v1/get_products_branch', type='json', auth='public', methods=['GET'])
    def get_available_products_by_branch(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['offset', 'limit', 'token', 'branch_id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_product_data = request.env['product.product'].sudo().search([('active', '=', True)], limit=data.get('limit'),
                                                                              offset=data.get('offset'), order='id')
            all_product_data = request.env['product.product'].sudo().search([('active', '=', True),('available_in_pos','=',True)], order='id')
            model_data_count = request.env['stock.quant'].sudo().search(
                [('branch_id', '=', data.get('branch_id'))])
            # model_product_data_count = request.env['stock.quant'].sudo().search(
            #     [('branch_id', '=', int(data.get('branch_id'))), ('product_id', '=', int(model_product_data.id))],
            # )
            final_data_list = []
            for record in model_product_data:
                if record.active:
                    model_product_data_count = request.env['stock.quant'].sudo().search(
                        [('branch_id', '=', model_data_count[0].branch_id.id),
                         ('product_id', '=', record.id)], limit=1
                    )
                    if model_product_data_count.available_quantity:
                        data = {
                            'odoo_id': record.id,
                            'name': record.name,
                            'barcode': record.barcode,
                            'quantity': model_product_data_count.quantity
                        }
                        final_data_list.append(data)
                    else:
                        data = {
                            'odoo_id': record.id,
                            'name': record.name,
                            'barcode': record.barcode,
                            'quantity': 0
                        }
                        final_data_list.append(data)
            response['results'] = final_data_list
            response['branch_products'] = len(all_product_data)
        return response

    @http.route('/api/v1/get_available_products', type='json', auth='public', methods=['GET'])
    def get_available_products(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['offset', 'limit', 'token']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['product.product'].sudo().search([], limit=data.get('limit'),
                                                                      offset=data.get('offset'), order='id')
            print(model_data)
            final_data_list = []
            for record in model_data:
                if record.active:
                    data = record.mapping_product_update()
                    final_data_list.append(data)
            print(final_data_list)
            response['results'] = final_data_list
        return response

    def mapping_product_update(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return {
            "odoo_id": self.id,
            "name": self.name,
            "price": self.list_price,
            "can_be_sold": self.sale_ok,
            "categ_id": self.categ_id.id,
            "categ_name": self.categ_id.name,
            "sku_name_english": self.sku_name_english,
            "sku_supplier_code": self.sku_supplier_code,
            "ht_sku_code": self.ht_sku_code,
            "supplier_id": self.supplier_id.id,
            "supplier_name": self.supplier_id.name,
            "original_supplier_id": self.original_supplier_id.id,
            "original_supplier_name": self.original_supplier_id.name,
            "shelf_life": self.shelf_life,
            "size": self.size,
            "healty_weight": self.healty_weight,
            "height": self.height,
            "base_width": self.base_width,
            "base_depth": self.base_depth,
            "storage_temprature": self.storage_temprature,
            "calories": self.calories,
            "sugar": self.sugar,
            "sodium": self.sodium,
            "container_type_id": self.container_type_id.id,
            "container_type_name": self.container_type_id.name,
            "container_shape_id": self.container_shape_id.id,
            "container_shape_name": self.container_shape_id.name,
            "container_material_id": self.container_material_id.id,
            "container_material_name": self.container_material_id.name,
            "content_type_id": self.content_type_id.id,
            "content_type_name": self.content_type_id.name,
            "storage_type_id": self.storage_type_id.id,
            "storage_type_name": self.storage_type_id.name,
            "color_id": self.color_id.id,
            "color_name": self.color_id.name,
            "flavor_id": self.flavor_id.id,
            "flavor_name": self.flavor_id.name,
            "healthy": self.healthy,
            "natural": self.natural,
            "keto": self.keto,
            "low_carb": self.low_carb,
            "low_brotein": self.low_brotein,
            "pbd": self.pbd,
            "vegan": self.vegan,
            "vegeterian": self.vegeterian,
            "odor_less": self.odor_less,
            "website_description": self.website_description,
            "display_on_mwebsite": self.display_on_mwebsite if self.active else False,
            "brand_id": self.brand_id.id,
            "brand_name": self.brand_id.name,
            # "website_name": self.website_name,
            "image": str(
                base) + "/productimage?product_id=" + str(
                self.id),
            'egg_allergies': self.egg_allergies,
            'gluten_allergies': self.gluten_allergies,
            'nuts_allergies': self.nuts_allergies,
            'lactose_allergies': self.lactose_allergies,
            'crustacean_allergies': self.crustacean_allergies,
            'peanut_allergies': self.peanut_allergies,
            'is_combo': self.is_combo,
            "combo_date_start": self.combo_date_start,
            "combo_date_end": self.combo_date_end,
            'combo_limit': self.combo_limit,
            # 'combo_available': self.check_lload(),
            'fats_protein': self.fats_protein,
            'Protein': self.Protein,
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }

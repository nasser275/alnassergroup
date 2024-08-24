# -*- coding: utf-8 -*-

"""
Description: This module acts as http reuqester and listner on ERP customers and product actions
"""
import json
import logging

import requests
from odoo import http
from odoo import models, api
from .settings import get_domain_for_host_by_ip_address, chec_ip_is_live, \
    get_image_url_512_for_categ, get_image_url_for_prod

logger = logging.getLogger(__name__)

# url To Update status in power bi
update_status_url = "http://powerbi.healthyandtasty.net/updateStatus.php"
tayar = "http://demoadmin.healthyandtasty.net/api/v1/ODDO_APIS/Tayar/order"


class HttpProduct(models.Model):
    _inherit = 'product.product'
    """ This url which we will send data to it from odoo """
    # old urls
    # url_crud = 'http://academy.e3melbusiness.com/healthyProject/public/api/v1/crud_product'
    # url_delete = 'http://academy.e3melbusiness.com/healthyProject/public/api/v1/delete_product'
    # end old urls
    # url_crud = 'https://healthyandtasty.net/healthyProject/public/api/v1/crud_product'
    # url_delete = 'https://healthyandtasty.net/healthyProject/public/api/v1/delete_product'

    # url_crud = 'http://admin.healthyandtasty.net/admin/public/api/v1/crud_product'
    # url_delete = 'http://admin.healthyandtasty.net/admin/public/api/v1/delete_product'

    url_crud = '{}/api/v1/crud_product'.format(get_domain_for_host_by_ip_address())
    # url_delete = 'https://admin.healthyandtasty.net/api/v1/ODDO_APIS/Product/delete_product?token=PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh'

    """Listens to creation methoget_domain_for_host_by_ip_addressd and sends http request"""

    @api.model
    def create(self, vals):
        res = super(HttpProduct, self).create(vals)
        if res:
            data = self.mapping_product_create(res)
            print("::", data)
            if data and self.url_crud:
                try:
                    response = requests.post(self.url_crud, data)
                    logger.info("Create Product:%s", response.text)
                    print("Response: %s , status: %s" % (response.text, response.status_code))
                except Exception as e:
                    print(e)
        return res

    """Listens to write method and sends http request"""

    def write(self, vals):
        res = super(HttpProduct, self).write(vals)
        flag = False
        flag = any([key for key in vals.keys() if key in self.mapping_product_update_keys()])
        if flag:
            if res:
                response = requests.get(
                    "https://admin.healthyandtasty.net/api/v1/ODDO_APIS/changeProductApi?token"
                    "=PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh&odoo_id=%s" % (
                        self.id))
                logger.info("Write Product:%s", response.text)
                print("Response: %s , status: %s" % (response.text, response.status_code))

        return res

    """Listens to write method and sends http request"""

    def unlink(self):
        data = self.mapping_product_delete()
        if data:
            try:
                print(data)
                response = requests.delete(
                    "https://admin.healthyandtasty.net/api/v1/ODDO_APIS/Product/delete_product?token=PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh&odoo_id=%s" % (
                        self.id))
                logger.info("Delete Product:%s", response.text)
                print("Response: %s , status: %s" % (response.text, response.status_code))
            except Exception as e:
                print(e)
        res = super(HttpProduct, self).unlink()
        return res

    # """Returns an object of the changed data for the product"""
    # def mapping_product_update(self, vals, res):
    # 	if not res:
    # 		return {}
    # 	data = {}
    # 	payload = {
    # 		"name": ["name", res.name],
    # 		"price": ["lst_price", res.lst_price],
    # 	}
    # 	for line in payload:
    # 		if payload[line][0] in vals and payload[line][1]:
    # 			data[line] = payload[line][1]
    # 	if data:
    # 		data['odoo_id'] = res.id
    # 		data['token'] = 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
    # 	return data

    """Returns an object of the changed data for the product"""

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
	    "barcode":self.barcode,
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
            "meta": self.meta_description if self.meta_description else "",
            # "website_name": self.website_name,
            "image": str(
                base) + "/productimage?product_id=" + str(
                self.id) if self.image_1920 else False,
            'egg_allergies': self.egg_allergies,
            'gluten_allergies': self.gluten_allergies,
            'nuts_allergies': self.nuts_allergies,
            'lactose_allergies': self.lactose_allergies,
            'crustacean_allergies': self.crustacean_allergies,
            'peanut_allergies': self.peanut_allergies,
            'is_combo': self.is_combo,
            # "combo_date_start": self.combo_date_start,
            # "combo_date_end": self.combo_date_end,
            'combo_limit': self.combo_limit,
            # 'combo_available': self.check_lload(),
            'fats_protein': self.fats_protein,
            'Protein': self.Protein,
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }

    def mapping_product_update_keys(self):
        return {
            "odoo_id",
            "name",
            "price",
            "can_be_sold",
            "categ_id",
            "categ_name",
            "sku_name_english",
            "sku_supplier_code",
            "ht_sku_code",
            "supplier_id",
            "supplier_name",
            "original_supplier_id",
            "original_supplier_name",
            "shelf_life",
            "size",
            "healty_weight",
            "height",
            "base_width",
            "base_depth",
            "storage_temprature",
            "calories",
            "sugar",
            "sodium",
            "container_type_id",
            "container_type_name",
            "container_shape_id",
            "container_shape_name",
            "container_material_id",
            "container_material_name",
            "content_type_id",
            "content_type_name",
            "storage_type_id",
            "storage_type_name",
            "color_id",
            "color_name",
            "flavor_id",
            "flavor_name",
            "healthy",
            "natural",
            "keto",
            "low_carb",
            "low_brotein",
            "pbd",
            "vegan",
            "vegeterian",
            "odor_less",
            "website_description",
            "website_name",
            "image_1920",
            "display_on_mwebsite",
            "brand_id",
            'egg_allergies',
            'gluten_allergies',
            'nuts_allergies',
            'lactose_allergies',
            'crustacean_allergies',
            'peanut_allergies',
            'is_combo',
            'combo_date_start',
            'combo_date_end',
            'combo_limit',
            'fats_protein',
            'Protein',
        }

    """Returns an object of the needed data for the product"""

    def mapping_product_create(self, res):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not res:
            return {}
        return {
            "odoo_id": res.id,
            "name": res.name,
            "price": res.list_price,
            "can_be_sold": res.sale_ok,
            "categ_id": res.categ_id.id,
            "categ_name": res.categ_id.name,
            "sku_name_english": res.sku_name_english,
            "sku_supplier_code": res.sku_supplier_code,
            "ht_sku_code": res.ht_sku_code,
            "supplier_id": res.supplier_id.id,
            "supplier_name": res.supplier_id.name,
            "original_supplier_id": res.original_supplier_id.id,
            "original_supplier_name": res.original_supplier_id.name,
            "shelf_life": res.shelf_life,
            "size": res.size,
            "healty_weight": res.healty_weight,
            "height": res.height,
            "base_width": res.base_width,
            "base_depth": res.base_depth,
            "storage_temprature": res.storage_temprature,
            "calories": res.calories,
            "sugar": res.sugar,
            "sodium": res.sodium,
            "container_type_id": res.container_type_id.id,
            "container_type_name": res.container_type_id.name,
            "container_shape_id": res.container_shape_id.id,
            "container_shape_name": res.container_shape_id.name,
            "container_material_id": res.container_material_id.id,
            "container_material_name": res.container_material_id.name,
            "content_type_id": res.content_type_id.id,
            "content_type_name": res.content_type_id.name,
            "storage_type_id": res.storage_type_id.id,
            "storage_type_name": res.storage_type_id.name,
            "color_id": res.color_id.id,
            "color_name": res.color_id.name,
            "flavor_id": res.flavor_id.id,
            "flavor_name": res.flavor_id.name,
            "healthy": res.healthy,
            "natural": res.natural,
            "keto": res.keto,
            "low_carb": res.low_carb,
            "low_brotein": res.low_brotein,
            "pbd": res.pbd,
            "vegan": res.vegan,
            "fats_protein": res.fats_protein,
            "Protein": res.Protein,
            "vegeterian": res.vegeterian,
            "odor_less": res.odor_less,
            "website_description": res.website_description,
            "display_on_mwebsite": res.display_on_mwebsite,
            "brand_id": res.brand_id.id,
            "brand_name": res.brand_id.name,
            # "website_name": res.website_name,
            # "image": get_image_url_for_prod(base, res.id),
            'egg_allergies': res.egg_allergies,
            'gluten_allergies': res.gluten_allergies,
            'nuts_allergies': res.nuts_allergies,
            'lactose_allergies': res.lactose_allergies,
            'crustacean_allergies': res.crustacean_allergies,
            'peanut_allergies': res.peanut_allergies,
            'is_combo': res.is_combo,
            # "combo_date_start": res.combo_date_start,
            # "combo_date_end": res.combo_date_end,
            'combo_limit': res.combo_limit,
            # 'combo_available': res.check_lload(),
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }

    """Returns an id of the deleted data for the product"""

    def mapping_product_delete(self):
        return {
            "odoo_id": self.id
        }

    # def mapping_product_update2(self):
    #     base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     return {
    #         "odoo_id": self.id,
    #         "name": self.name,
    #         "image": str(
    #             base) + "/productimage?product_id=" + str(
    #             self.id),
    #         "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
    #     }

    # def update_prods_image(self):
    #     for product in self:
    #         data = product.mapping_product_update2()
    #
    #         logger.info("API>>>>>>>>>>>>>>>>>%s%s", data, self.url_crud)
    #         if data:
    #             try:
    #                 response = requests.post(self.url_crud, data)
    #                 logger.info("Response:%s", response.text)
    #             except Exception as e:
    #                 print(e)


class HttpCompany(models.Model):
    _inherit = 'res.branch'

    # old urls
    # url_crud = 'http://academy.e3melbusiness.com/healthyProject/public/api/v1/crud_branch'
    # url_delete = 'http://academy.e3melbusiness.com/healthyProject/public/api/v1/delete_branch'
    # end old urls
    # url_crud = 'https://healthyandtasty.net/healthyProject/public/api/v1/crud_branch'
    # url_delete = 'https://healthyandtasty.net/healthyProject/public/api/v1/delete_branch'
    #
    # url_crud = 'http://admin.healthyandtasty.net/admin/public/api/v1/crud_branch'
    # url_delete = 'http://admin.healthyandtasty.net/admin/public/api/v1/delete_branch'

    url_crud = '{}/api/v1/crud_branch'.format(get_domain_for_host_by_ip_address())
    url_delete = '{}/api/v1/delete_branch'.format(get_domain_for_host_by_ip_address())

    @api.model
    def create(self, vals):
        res = super(HttpCompany, self).create(vals)
        if res and res.name:
            data = self.mapping_company_create(res)
            if data and self.url_crud:
                print(data)
                try:
                    # pass
                    response = requests.post(self.url_crud, data)
                    print("Response: %s , status: %s" % (response.text, response.status_code))
                except Exception as e:
                    print(e)
        return res

    # @api.model
    def write(self, vals):
        res = super(HttpCompany, self).write(vals)
        if 'name' in vals.keys():
            if res:
                for rec in self:
                    data = rec.mapping_company_update(vals, res)
                    if data:
                        try:
                            print(data)
                            # pass
                            response = requests.post(self.url_crud, data)
                            print("Response: %s , status: %s" % (response.text, response.status_code))
                        except Exception as e:
                            print(e)
        if 'address' in vals.keys():
            if res:
                for rec in self:
                    data = rec.mapping_company_update(vals, res)
                    if data:
                        try:
                            print(data)
                            # pass
                            response = requests.post(self.url_crud, data)
                            print("Response: %s , status: %s" % (response.text, response.status_code))
                        except Exception as e:
                            print(e)

        return res

    """Listens to write method and sends http request"""

    # @api.model
    def unlink(self):
        data = self.mapping_company_delete()
        try:
            print(data)
            # pass
            response = requests.post(self.url_delete, data)
            print("Response: %s , status: %s" % (response.text, response.status_code))
        except Exception as e:
            print(e)
        res = super(HttpCompany, self).unlink()
        return res

    def mapping_company_update(self, vals, res):
        if not res:
            return {}

        return {
            "odoo_id": self.id,
            "name": self.name,
            "address": self.address,

            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }
        # data = {}
        # payload = {
        #     "name": ["name", self.name],
        # }
        # for line in payload:
        #     if payload[line][0] in vals and payload[line][1]:
        #         data[line] = payload[line][1]
        # if data:
        #     data['odoo_id'] = self.id
        #     data['token'] = 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        # return data

    def mapping_company_create(self, res):
        if not res:
            return {}
        return {
            "odoo_id": res.id,
            "name": res.name,
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }

    """Returns an id of the deleted data for the product"""

    def mapping_company_delete(self):
        return {
            "odoo_id": self.id,
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }


class HttpCategory(models.Model):
    _inherit = 'product.category'

    # old urls
    # url_crud = 'http://academy.e3melbusiness.com/healthyProject/public/api/v1/crud_branch'
    # url_delete = 'http://academy.e3melbusiness.com/healthyProject/public/api/v1/delete_branch'
    # end old urls
    # url_crud = 'https://healthyandtasty.net/healthyProject/public/api/v1/crud_branch'
    # url_delete = 'https://healthyandtasty.net/healthyProject/public/api/v1/delete_branch'
    #
    # url_crud = 'http://admin.healthyandtasty.net/admin/public/api/v1/crud_branch'
    # url_delete = 'http://admin.healthyandtasty.net/admin/public/api/v1/delete_branch'

    url_crud = '{}/api/v1/crud_category'.format(get_domain_for_host_by_ip_address())

    # url_delete = '{}/api/v1/delete_branch'.format(get_domain_for_host_by_ip_address())

    @api.model
    def create(self, vals):
        res = super(HttpCategory, self).create(vals)
        if res and res.name:
            data = self.mapping_category_create(res)
            if data and self.url_crud:
                print(data)
                try:
                    # pass
                    response = requests.post(self.url_crud, data)
                    print("Response: %s , status: %s" % (response.text, response.status_code))
                except Exception as e:
                    print(e)
        return res

    # @api.model
    def write(self, vals):
        res = super(HttpCategory, self).write(vals)
        if 'name' in vals.keys() or 'parent_id' in vals.keys() or 'image' in vals.keys():
            if res:
                for rec in self:
                    data = rec.mapping_category_update()
                    if data:
                        try:
                            print(self.url_crud)
                            # pass
                            response = requests.post(self.url_crud, data)
                            print("Response: %s , status: %s" % (response.text, response.status_code))
                        except Exception as e:
                            print(e)
        return res

    """Listens to write method and sends http request"""

    def mapping_category_update(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return {
            "odoo_id": self.id,
            "name": self.name,
            "parent_id": self.parent_id.id,
            "parent_name": self.parent_id.name,
            "image": get_image_url_512_for_categ(base, self.id),
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }

    def mapping_category_create(self, res):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        if not res:
            return {}
        return {
            "odoo_id": res.id,
            "name": res.name,
            "parent_id": res.parent_id.id,
            "parent_name": res.parent_id.name,
            # "image": get_image_url_512_for_categ(base, res.id),
            "token": 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
        }

# Traking status
# class HttpPosOrder(models.Model):
#     _inherit = 'pos.order'
#
#     def write(self, vals):
#         res = super(HttpPosOrder, self).write(vals)
#         if res and 'state' in vals.keys() and chec_ip_is_live():
#             for order in self:
#                 data = {"tablename": "receipts", "status": order.state, "id": order.id, }
#                 if data:
#                     try:
#                         response = requests.put(update_status_url, json.dumps(data))
#                         print("Response: %s , status: %s" % (response.text, response.status_code))
#                     except Exception as e:
#                         print(e)
#         # tayar
#         logger.info("helloooooooooooo tayer:%s", 0)
#         if chec_ip_is_live():
#             for order in self:
#                 logger.info("helloooooooooooo tayer:%s", 1)
#                 if order.app_order_id:
#                     logger.info("helloooooooooooo tayer:%s", 5)
#                     pass
#                 else:
#                     logger.info("helloooooooooooo tayer:%s", 4)
#                     logger.info("helloooooooooooo tayer:%s", order.send_to_tayar)
#                     if order.send_to_tayar == False and order.delivery_person_id:
#                         logger.info("helloooooooooooo tayer:%s", 2)
#                         data = order.get_data_tayar()
#                         data = json.dumps(data, ensure_ascii=False)
#                         print(data)
#                         if data:
#                             logger.info("helloooooooooooo tayer:%s", 3)
#                             try:
#                                 headers = {
#                                     'Content-Type': 'application/json'
#                                 }
#                                 response = requests.post(tayar, data=data.encode(), headers=headers)
#                                 logger.info("Create tayer:%s", response.text)
#                                 order.send_to_tayar = True
#                             except Exception as e:
#                                 print(e)
#         return res
#
#     def get_data_tayar(self):
#         data = {
#             'odoo_id': self.company_id.id,
#             'order': {
#                 'id': self.id,
#                 'delivered_date': str(self.date_order.date()),
#                 'delivery_time_name': '10:23',
#                 'price_after_discount': self.amount_total,
#                 'note': ''
#             },
#             'customer': {
#                 'id': self.partner_id.id,
#                 'name': self.partner_id.name,
#                 'mobile': self.partner_id.phone
#             },
#             'address': {
#                 'address': self.get_address(self.partner_id),
#                 'note': "",
#                 'building_number': '',
#                 'flat_number': '',
#                 'hallmark': '',
#                 'lat': '',
#                 'lng': ''
#             },
#             'product_details': [
#                 {
#                     'product_id': line.product_id.id,
#                     'product_name_ar': line.product_id.name,
#                     'product_price': line.price_unit,
#                     'quantity': line.qty,
#                     'product_tax': ''
#                 } for line in self.lines],
#             'token': 'PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh',
#
#         }
#         return data
#
#     def get_address(self, object):
#         if object.street and object.street2:
#             address = "{} {}".format(object.street, object.street2)
#         elif object.street and not object.street2:
#             address = object.street
#         elif not object.street and object.street2:
#             address = object.street2
#         else:
#             address = None
#         return address

#
# class HttpPurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     # @api.model
#     def write(self, vals):
#         res = super(HttpPurchaseOrder, self).write(vals)
#         if res and 'state' in vals.keys() and chec_ip_is_live():
#             for order in self:
#                 data = {"tablename": "purchasing", "status": order.state, "id": order.id}
#                 if data:
#                     try:
#                         print("purchase", data)
#                         response = requests.put(update_status_url, json.dumps(data))
#                         print("Response: %s , status: %s" % (response.text, response.status_code))
#                     except Exception as e:
#                         print(e)
#         return res
#
#
# class HttpPurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'
#
#     # @api.model
#     def write(self, vals):
#         res = super(HttpPurchaseOrderLine, self).write(vals)
#         if res and 'qty_received' in vals.keys() and chec_ip_is_live():
#             for line in self:
#                 data = {"tablename": "purchasing", "order_lines_recieved_qty": line.qty_received, "po_line_id": line.id}
#                 if data:
#                     try:
#                         print("purchase", data)
#                         response = requests.put(update_status_url, json.dumps(data))
#                         print("Response: %s" % (response.text))
#                     except Exception as e:
#                         print(e)
#         return res
#
#
# class HttpAccountInvoice(models.Model):
#     _inherit = 'account.move'
#
#     # @api.model_create_multi
#     def write(self, vals):
#         res = super(HttpAccountInvoice, self).write(vals)
#         if res and 'state' in vals.keys() and chec_ip_is_live():
#             for inv in self:
#                 data = {"tablename": "returns", "status": inv.state, "id": inv.id}
#                 if data:
#                     try:
#                         print("returns", data)
#                         response = requests.put(update_status_url, json.dumps(data))
#                         print("Response: %s , status: %s" % (response.text, response.status_code))
#                     except Exception as e:
#                         print(e)
#         return res

# -*- coding: utf-8 -*-

from odoo import models, fields, api





class Product(models.Model):
    _inherit='product.product'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        res= super(Product, self).check_access_rights(operation, raise_exception=raise_exception)
        if operation=='create':
            if self.env.user.has_group('product_create_access.group_allow_create_edit_product'):
                return res
            else:
               return False
        return res

class ProductTemplate(models.Model):
    _inherit='product.template'

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        res= super(ProductTemplate, self).check_access_rights(operation, raise_exception=raise_exception)
        if operation=='create':
            if self.env.user.has_group('product_create_access.group_allow_create_edit_product'):
                return res
            else:
                return False
        return res
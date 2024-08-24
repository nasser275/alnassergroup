# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'
    enable_service = fields.Boolean(string='Enable Service Product', default=False)
    service_product_id = fields.Many2one('product.product', string='Service  Product',
                                         domain="[('sale_ok', '=', True)]")

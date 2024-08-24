# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    barcode = fields.Char(string="Barcode", related='product_id.barcode')

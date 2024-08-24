# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    @api.constrains('product_uom_qty')
    def check_qty_line(self):

        for rec in self:
            if rec.product_uom_qty <= 0:
                raise ValidationError(_("you can not request products by negative (-) or Zero !"))



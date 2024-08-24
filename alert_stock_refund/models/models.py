# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError



class Operation(models.Model):
    _inherit = 'stock.picking.type'

    alert_stock_refund = fields.Boolean(string="Alert Stock Refund")


class Picking(models.Model):
    _inherit = 'stock.picking'
    alert_stock_refund = fields.Boolean(string="Alert Stock Refund",related='picking_type_id.alert_stock_refund', store=True)



    def button_validate(self):
        if self.alert_stock_refund:
            for line in self.move_line_ids_without_package:
                qty_available=self.get_single_product_refund( line.product_id.id,self.location_id.id)
                if line.qty_done>qty_available:
                    raise ValidationError(str(line.product_id.name)+"""Refund Quantity ({qty_done}) > Quantity Available ({qty_available})! """.format(qty_done=line.qty_done,qty_available=qty_available))
        res = super(Picking, self).button_validate()

        return res

    def get_single_product_refund(self, product_id, location_id):
        quants = self.env['stock.quant'].sudo().search([('product_id', '=', product_id), ('location_id', '=', location_id)])
        quantity=0
        for quant in quants:
            quantity += quant.quantity
        return quantity


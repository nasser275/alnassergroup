# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import Warning
import random
from odoo.tools import float_is_zero
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class pos_stock_config(models.Model):
    _inherit = 'pos.config'

    def _get_default_location(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)],
                                                  limit=1).lot_stock_id

    pos_display_stock = fields.Boolean(string='Display Stock in POS')
    pos_stock_type = fields.Selection(
        [('onhand', 'Qty on Hand'), ('incoming', 'Incoming Qty'), ('outgoing', 'Outgoing Qty'),
         ('available', 'Qty Available')], string='Stock Type', help='Seller can display Different stock type in POS.')
    pos_allow_order = fields.Boolean(string='Allow POS Order When Product is Out of Stock')
    pos_deny_order = fields.Char(string='Deny POS Order When Product Qty is goes down to')

    show_stock_location = fields.Selection([
        ('all', 'All Warehouse'),
        ('specific', 'Current Session Warehouse'),
    ], string='Show Stock Of', default='all')

    stock_location_id = fields.Many2one(
        'stock.location', string='Stock Location',
        domain=[('usage', '=', 'internal')], required=True, default=_get_default_location)


class pos_order(models.Model):
    _inherit = 'pos.order'

    is_point_converted = fields.Boolean(string='Points Converted')
    location_id = fields.Many2one(
        comodel_name='stock.location',
        related='config_id.stock_location_id',
        string="Location", store=True,
        readonly=True,
    )


class stock_quant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None,
                                  strict=False):
        """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                              strict=strict)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = sum(
                quants.filtered(lambda q: float_compare(q.quantity, 0, precision_rounding=rounding) > 0).mapped(
                    'quantity')) - sum(quants.mapped('reserved_quantity'))
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(_('It is not possible to reserve more products of %s than you have in stock.',
                                  product_id.display_name))
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            # if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
            #     raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.',
            #                       product_id.display_name))
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity,
                                                                                     precision_rounding=rounding):
                break
        return reserved_quants

    def get_stock_location_qty(self, location):
        res = {}
        product_ids = self.env['product.product'].search([])
        for product in product_ids:
            quants = self.env['stock.quant'].search(
                [('product_id', '=', product.id), ('location_id', '=', location['id'])])
            if len(quants) > 1:
                quantity = 0.0
                for quant in quants:
                    quantity += quant.quantity
                res.update({product.id: quantity})
            else:
                res.update({product.id: quants.quantity})
        return [res]

    def get_products_stock_location_qty(self, location, products):
        res = {}
        product_ids = self.env['product.product'].sudo().browse(products)
        for product in product_ids:
            quants = self.env['stock.quant'].sudo().search([('product_id', '=', product.id),
                                                            ('location_id', 'child_of', location['id'])])
            if len(quants) > 1:
                quantity = 0.0
                for quant in quants:
                    quantity += quant.quantity
                res.update({product.id: quantity})
            else:
                res.update({product.id: quants.quantity})
        return [res]

    def get_single_product(self, product, location):
        res = []
        pro = self.env['product.product'].browse(product)
        quants = self.env['stock.quant'].search(
            [('product_id', '=', pro.id), ('location_id', 'child_of', location['id'])])
        if len(quants) > 1:
            quantity = 0.0
            for quant in quants:
                quantity += quant.quantity
            res.append([pro.id, quantity])
        else:
            res.append([pro.id, quants.quantity])
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    disable_show_in_franchise = fields.Boolean(string="Disable Show In Franchisee Report?")


class product(models.Model):
    _inherit = 'product.product'

    available_quantity = fields.Float('Available Quantity')
    disable_show_in_franchise = fields.Boolean(string="Disable Show In Franchisee Report?")

    def get_stock_location_avail_qty(self, location, products):
        res = {}
        product_ids = self.env['product.product'].browse(products)
        for product in product_ids:
            quants = self.env['stock.quant'].search(
                [('product_id', '=', product.id), ('location_id', 'child_of', location['id'])])
            outgoing = self.env['stock.move'].search(
                [('product_id', '=', product.id), ('location_id', 'child_of', location['id'])])
            incoming = self.env['stock.move'].search(
                [('product_id', '=', product.id), ('location_id', 'child_of', location['id'])])
            qty = 0.0
            product_qty = 0.0
            incoming_qty = 0.0
            if len(quants) > 1:
                for quant in quants:
                    qty += quant.quantity

                if len(outgoing) > 0:
                    for quant in outgoing:
                        if quant.state not in ['done']:
                            product_qty += quant.product_qty

                if len(incoming) > 0:
                    for quant in incoming:
                        if quant.state not in ['done']:
                            incoming_qty += quant.product_qty
                    product.available_quantity = qty - product_qty + incoming_qty
                    res.update({product.id: qty - product_qty + incoming_qty})
            else:
                if not quants:
                    if len(outgoing) > 0:
                        for quant in outgoing:
                            if quant.state not in ['done']:
                                product_qty += quant.product_qty

                    if len(incoming) > 0:
                        for quant in incoming:
                            if quant.state not in ['done']:
                                incoming_qty += quant.product_qty
                    product.available_quantity = qty - product_qty + incoming_qty
                    res.update({product.id: qty - product_qty + incoming_qty})
                else:
                    if len(outgoing) > 0:
                        for quant in outgoing:
                            if quant.state not in ['done']:
                                product_qty += quant.product_qty

                    if len(incoming) > 0:
                        for quant in incoming:
                            if quant.state not in ['done']:
                                incoming_qty += quant.product_qty
                    product.available_quantity = quants.quantity - product_qty + incoming_qty
                    res.update({product.id: quants.quantity - product_qty + incoming_qty})
        return [res]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer_ref = fields.Char('Transfer REF')

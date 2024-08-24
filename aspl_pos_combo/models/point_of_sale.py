# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from datetime import datetime

from odoo import models, fields, api
from functools import partial

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_combo = fields.Boolean('Enable Combo')
    edit_combo = fields.Boolean('Single Click for Edit Combo')
    hide_uom = fields.Boolean('Hide UOM')


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def create(self, values):
        res = super(PosOrder, self).create(values)
        for line in res.lines:
            if line.product_id.is_combo:
                line.write({
                    'price_subtotal': 0,
                    'price_subtotal_incl': 0,
                })
                for ext_line_info in line.combo_ext_line_info:
                    product_combo_discount = 0
                    print('combo_line_id', ext_line_info)
                    if ext_line_info.discount == 0:
                        product_combo_discount = self.env['product.combo'].sudo().search(
                            [('id', '=', ext_line_info.combo_id)], limit=1).discount
                        print('combo_line_discount', product_combo_discount)
                        x_line = self.env['pos.order.line'].create({
                            'product_id': ext_line_info.product_id.id,
                            'full_product_name': ext_line_info.product_id.name,
                            'qty': line.qty * ext_line_info.qty,
                            'price_unit': ext_line_info.price,
                            # 'discount': ext_line_info.discount,
                            'discount': product_combo_discount,
                            'combo_name': line.product_id.name,
                            'is_combo': True,
                            'price_subtotal': 0,
                            'price_subtotal_incl': 0,
                            'tax_ids': [(6, 0, [x.id for x in ext_line_info.product_id.taxes_id])],
                            'order_id': res.id,
                        })
                        x_line._onchange_qty()
                        x_line.order_id._onchange_amount_all()
                    else:
                        x_line = self.env['pos.order.line'].create({
                            'product_id': ext_line_info.product_id.id,
                            'full_product_name': ext_line_info.product_id.name,
                            'qty': line.qty * ext_line_info.qty,
                            'price_unit': ext_line_info.price,
                            'discount': ext_line_info.discount,
                            # 'discount': product_combo_discount,
                            'combo_name': line.product_id.name,
                            'is_combo': True,
                            'price_subtotal': 0,
                            'price_subtotal_incl': 0,
                            'tax_ids': [(6, 0, [x.id for x in ext_line_info.product_id.taxes_id])],
                            'order_id': res.id,
                        })
                        x_line._onchange_qty()
                        x_line.order_id._onchange_amount_all()
                    print("Combo Line: %s , Session: %s" % ({
                                                                'product_id': ext_line_info.product_id.id,
                                                                'full_product_name': ext_line_info.product_id.name,
                                                                'qty': line.qty * ext_line_info.qty,
                                                                'price_unit': ext_line_info.price,
                                                                'discount': ext_line_info.discount,
                                                                'combo_name': line.product_id.name,
                                                                'is_combo': True,
                                                                'price_subtotal': 0,
                                                                'price_subtotal_incl': 0,
                                                                'tax_ids': [(6, 0, [x.id for x in
                                                                                    ext_line_info.product_id.taxes_id])],
                                                                'order_id': res.id,
                                                            }, x_line.order_id.name))
        return res


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    main_combo = fields.Boolean("Main Combo")
    is_combo = fields.Boolean("Is Combo")
    combo_name = fields.Char(string="Combo Name", required=False)
    combo_price = fields.Float(string="Combo Price", required=False)
    combo_cost = fields.Float(string="Combo Cost", required=False)
    combo_line_cost = fields.Float(string="Line Combo Cost")
    combo_line_price = fields.Float(string="Line Combo Price")
    combo_ext_line_info = fields.One2many(comodel_name="pos.order.combo.line", inverse_name="order_line")


    def _prepare_refund_data(self, refund_order, PosOrderLineLot):
        res=super()._prepare_refund_data(refund_order, PosOrderLineLot)
        res['main_combo']=self.main_combo
        res['is_combo']=self.is_combo
        res['combo_name']=self.combo_name
        res['combo_price']=self.combo_price
        res['combo_cost']=self.combo_cost
        res['combo_line_cost']=self.combo_line_cost
        res['combo_line_price']=self.combo_line_price
        return res

    def _export_for_ui(self, orderline):
        res=super(PosOrderLine, self)._export_for_ui(orderline)
        res['is_combo']=orderline.is_combo
        res['combo_name']=orderline.combo_name
        res['main_combo']=orderline.main_combo
        return res



    @api.model
    def create(self, values):
        res = super(PosOrderLine, self).create(values)
        if res.product_id.is_combo:
            res.main_combo=True
            res.is_combo=True
            res.product_id.product_tmpl_id.sudo().write({'combo_limit':res.product_id.combo_limit - 1})
        if res.refunded_orderline_id:
            res.main_combo=res.refunded_orderline_id.main_combo
            res.is_combo=res.refunded_orderline_id.is_combo
            res.combo_name=res.refunded_orderline_id.combo_name
            res.combo_price=res.refunded_orderline_id.combo_price
            res.combo_cost=res.refunded_orderline_id.combo_cost
            res.combo_line_cost=res.refunded_orderline_id.combo_line_cost
            res.combo_line_price=res.refunded_orderline_id.combo_line_price
        return res







class ProductTemplate(models.Model):
    _inherit = "product.template"
    is_combo = fields.Boolean("Is Combo")
    combo_date_start = fields.Date("Combo Start Date")
    combo_date_end = fields.Date("Combo End Date")
    combo_limit = fields.Integer("Combo Limit", default=1)
    combo_cost = fields.Float(string="Combo Cost",compute='_calc_combo_cost',store=True)
    combo_price = fields.Float(string="Combo Price",compute='_calc_combo_cost',store=True)
    product_combo_ids = fields.One2many('product.combo', 'product_tmpl_id')
    product_combo_line_ids = fields.One2many('product.combo.line', 'product_tmpl_id')
    expect_branch_ids = fields.Many2many(comodel_name="res.branch", relation="combo_nbranchs", string="Expect Branch")
    pos_load = fields.Boolean(compute="calc_load")


    @api.depends('combo_date_start', 'combo_date_end')
    def calc_load(self):
        for rec in self:
            if self.env.user.branch_id.id in rec.expect_branch_ids.ids:
                rec.pos_load = False
            else:
                if self.check_expiry(rec.combo_date_start, rec.combo_date_end):
                    rec.pos_load = True
                else:
                    rec.pos_load = False

    def check_expiry(self, start, end):
        today = datetime.now().date()
        if (start and end):
            if (today < start or today > end):
                return False
        elif (start):
            if (today < start):
                return False
        elif (end):
            if (today > end):
                return False
        return True

    def create_combo_lines(self):
        lines = []
        products = []
        for combo in self.product_combo_ids:
            for product in combo.product_ids:
                if product.id not in products:
                    products.append(product.id)
                    lines.append((0,0,{
                        'product_id': product.id
                    }))
            print(">>>products",products)
        self.product_combo_line_ids = [(5, 0, 0)]
        self.product_combo_line_ids = lines

    @api.depends('product_combo_line_ids')
    def _calc_combo_cost(self):
        for rec in self:
            sum_cost=0
            sum_price=0
            for line in rec.product_combo_line_ids:
                sum_cost+=line.combo_line_cost
                sum_price+=line.combo_line_price
            rec.combo_cost=sum_cost
            rec.combo_price=sum_price





class ProductCombo(models.Model):
    _name = 'product.combo'
    _description = 'Product Combo'

    product_tmpl_id = fields.Many2one('product.template')
    require = fields.Boolean("Required", Help="Don't select it if you want to make it optional")
    pos_category_id = fields.Many2one('pos.category', "Categories")
    product_ids = fields.Many2many('product.product', string="Products")
    discount = fields.Float("Discount")
    no_of_items = fields.Integer("No. of Items", default=1)

    @api.onchange('require')
    def onchage_require(self):
        if self.require:
            self.pos_category_id = False


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args
        if self._context.get('is_required', False):
            args += [['available_in_pos', '=', True]]
        if self._context.get('category_from_line', False):
            pos_category_id = self.env['pos.category'].browse(self._context.get('category_from_line'))
            args += [['pos_categ_id', 'child_of', pos_category_id.id], ['available_in_pos', '=', True]]
        return super(ProductProduct, self).name_search(name, args=args, operator='ilike', limit=100)







class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    main_combo = fields.Boolean("Main Combo")
    is_combo = fields.Boolean("Is Combo")
    combo_name = fields.Char(string="Combo Name", required=False)
    combo_price = fields.Float(string="Combo Price", required=False)
    combo_cost = fields.Float(string="Combo Cost", required=False)
    combo_line_cost = fields.Float(string="Line Combo Cost")
    combo_line_price = fields.Float(string="Line Combo Price")

    def _select(self):
        return super(PosOrderReport,
                     self)._select() + ", l.is_combo, l.main_combo, l.combo_name, l.combo_price,l.combo_cost,l.combo_line_cost,l.combo_line_price"

    def _group_by(self):
        return super(PosOrderReport,
                     self)._group_by() + ", l.is_combo, l.main_combo, l.combo_name, l.combo_price,l.combo_cost,l.combo_line_cost,l.combo_line_price"


class ProductComboLine(models.Model):
    _name = 'product.combo.line'

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False)
    combo_line_cost = fields.Float(string="Line Combo Cost")
    combo_line_price = fields.Float(string="Line Combo Price")
    product_tmpl_id = fields.Many2one('product.template')
class product(models.Model):
    _inherit='product.product'

    def create_combo_lines(self):
        lines = []
        products = []
        for combo in self.product_combo_ids:
            for product in combo.product_ids:
                if product.id not in products:
                    products.append(product.id)
                    lines.append((0,0,{
                        'product_id': product.id
                    }))
        self.product_combo_line_ids = [(5, 0, 0)]
        self.product_combo_line_ids = lines


class OrderComboLine(models.Model):
    _name='pos.order.combo.line'
    product_id = fields.Many2one(comodel_name="product.product")
    product_name = fields.Char(string='Product Name')
    qty = fields.Integer()
    price = fields.Float()
    discount = fields.Float()
    price_w_o_tax = fields.Float()
    tax = fields.Boolean()
    combo_id = fields.Integer()
    order_line = fields.Many2one(comodel_name="pos.order.line")

    @api.model
    def create(self, values):
        if 'combo_name' in values.keys():
            values.pop('combo_name')
        if 'id' in values.keys():
            values.pop('id')
        if 'name' in values.keys():
            values.pop('name')
        return super(OrderComboLine, self).create(values)


class ProductTemplate(models.Model):
    _inherit='product.template'
    hide_discount = fields.Boolean(string='Hide From POS')
class Product(models.Model):
    _inherit='product.product'
    price_w_o_tax= fields.Float(compute='_compute_price_w_o_tax',store=False)
    @api.depends('taxes_id', 'list_price')
    def _compute_price_w_o_tax(self):
        for record in self:
            tax=record._construct_tax_string2(record.list_price)
            if tax:
                record.price_w_o_tax = abs(record.list_price-tax)
            else:
                record.price_w_o_tax = 0

    def _construct_tax_string2(self, price):
        currency = self.currency_id
        res = self.taxes_id.compute_all(price, product=self, partner=self.env['res.partner'])
        included = res['total_included']
        if currency.compare_amounts(included, price):
            return included
        excluded = res['total_excluded']
        if currency.compare_amounts(excluded, price):
            return excluded



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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class PosPromotion(models.Model):
    _name = 'pos.promotion'
    _order = "sequence"
    _rec_name = 'promotion_code'
    _description = 'Pos Promotion'

    AVAILABLE_TIMES = [
        ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
        ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'),
        ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'),
        ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23')
    ]

    promotion_code = fields.Char('Promotion Code', required=True)
    promotion_type = fields.Selection([('buy_x_get_y', 'Buy X Get Y Free'),
                                       ('buy_x_get_dis_y', 'Buy X Get Discount On Y'),
                                       ('discount_total', 'Discount (%) on Total Amount'),
                                       ('quantity_discount', 'Percent Discount on Quantity'),
                                       ('quantity_price', 'Fix Discount on Quantity'),
                                       ('discount_on_multi_product', 'Discount On Combination Products'),
                                       ('discount_on_multi_category', 'Discount On Multiple Categories')],
                                      default="buy_x_get_y", required=True)
    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)
    from_time = fields.Selection(AVAILABLE_TIMES, string="From Time")
    to_time = fields.Selection(AVAILABLE_TIMES, string="To Time")
    day_of_week_ids = fields.Many2many('day.week', string="Day Of The Week", required=True)
    pos_condition_ids = fields.One2many('pos.conditions', 'pos_promotion_rel')
    pos_quantity_ids = fields.One2many('quantity.discount', 'pos_quantity_rel')
    pos_quantity_amt_ids = fields.One2many('quantity.discount.amt', 'pos_quantity_amt_rel')
    pos_quantity_dis_ids = fields.One2many('get.discount', 'pos_quantity_dis_rel')
    product_id_qty = fields.Many2one('product.product', 'Product')
    product_id_amt = fields.Many2one('product.product', 'Select Product')
    product_id_x_y = fields.Many2one('product.product', 'Choose Product')
    multi_products_discount_ids = fields.One2many('discount.multi.products', 'multi_product_dis_rel')
    multi_category_discount_ids = fields.One2many('discount.multi.categories', 'multi_category_dis_rel')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of promotions.")
    # Invoice Promotion
    total_amount = fields.Float('Total Invoice Amount')
    operator = fields.Selection([('is_eql_to', 'Is Equal To'),
                                 ('greater_than_or_eql', 'Greater Than Or Equal')])
    total_discount = fields.Float('Total Discount(%)')
    discount_product = fields.Many2one("product.product", "Discount Product",
                                       default=lambda self: self.env.ref('aspl_pos_promotion.disc_product').id)
    active = fields.Boolean("Active", default=True)
    parent_product_ids = fields.Many2many(comodel_name='product.product', string="Products")
    discount_price_ids = fields.One2many('discount.above.price', 'pos_promotion_id')
    # expect_companies = fields.Many2many(comodel_name="res.company", relation="promotion_companies",
    #                                     string="Expect Companies")
    expect_branch_ids = fields.Many2many(comodel_name="res.branch", relation="promotion_nbranchs",
                                         string="Expect Branch")

    filter_supplier = fields.Boolean(string="Filter By Supplier")
    limit = fields.Integer(string="Limit", required=False)
    promotion_cost = fields.Float(string="Promotion Cost", required=False)
    apply_on_order_source = fields.Boolean(
        string='Apply On Order Sources',
        required=False)


    @api.model
    def check_expect_branch(self, promotion=False):
        prom = self.sudo().browse(promotion.get('id'))
        if prom.expect_branch_ids:
            if self.env.user.branch_id.id in prom.expect_branch_ids.ids:
                return True
            else:
                return False
        else:
            return False

    @api.model
    def default_get(self, fields_list):
        res = super(PosPromotion, self).default_get(fields_list)
        days = self.env['day.week'].search([])
        list_day = []
        for rec in days:
            list_day.append(rec.id)
        res['day_of_week_ids'] = [(6, 0, list_day)]
        return res

    @api.constrains('from_date', 'to_date')
    def date_check(self):
        if self.from_date > self.to_date:
            raise ValidationError("To Date must be greater than From date")

    @api.constrains('from_time', 'to_time')
    def time_check(self):
        if self.from_time and not self.to_time:
            raise ValidationError("You have to set 'To' Time.")
        if not self.from_time and self.to_time:
            raise ValidationError("You have to set 'From' Time.")
        if self.from_time and self.to_time and int(self.from_time) > int(self.to_time):
            raise ValidationError("To Time must be greater than From Time")

    @api.model
    def update_promotion_data_to_backend(self, data):
        prom = data.get('id')
        if prom:
            res = self.browse(prom)
            if res:
                res.write({'limit': res.limit - 1})
                return True
            else:
                return False
        else:
            return False

    @api.model
    def get_available_combo(self):
        model_data = self.env['pos.promotion'].sudo().search([('limit', '>', 0)], order='id')
        print("model_data",model_data)
        final_data_list = []
        for record in model_data:
            print("D>D>D>>D",record.promotion_type,self.check_expiry(record.from_date, record.to_date))
            if self.check_expiry(record.from_date, record.to_date):
                if record.promotion_type == 'quantity_discount':
                    final_data_list.append(record.product_id_qty.id)
                if record.promotion_type == 'discount_on_multi_product':
                    for line in record.multi_products_discount_ids:
                        for product in line.product_ids:
                            final_data_list.append(product.id)
                if record.promotion_type == 'discount_on_multi_category':
                    if record.filter_supplier:
                        for line in record.multi_category_discount_ids:
                            for supplier in line.supplier_ids:
                                rres = self.env['product.product'].sudo().search([('supplier_id', '=', supplier.id)])
                                for product in rres:
                                    final_data_list.append(product.id)
                    if record.filter_supplier == False:
                        for line in record.multi_category_discount_ids:
                            for categ_id in line.categ_ids:
                                rres = self.env['product.product'].sudo().search([('categ_id', '=', categ_id.id)])
                                for product in rres:
                                    final_data_list.append(product.id)
                if record.promotion_type == 'buy_x_get_y':
                    for con in record.pos_condition_ids:
                        final_data_list.append(con.product_x_id.id)
        return final_data_list

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


class PosCondition(models.Model):
    _name = 'pos.conditions'
    _description = 'Pos Promotion Conditions'

    pos_promotion_rel = fields.Many2one('pos.promotion')
    product_x_id = fields.Many2one('product.product', 'Product(X)')
    operator = fields.Selection([('greater_than_or_eql', 'Greater Than Or Equal')])
    quantity = fields.Float('Quantity(X)')
    product_y_id = fields.Many2one('product.product', 'Product(Y)')
    quantity_y = fields.Float('Quantity(Y)')
    promotion_cost = fields.Float(string="Promotion Cost", required=False)


class QuantityDiscount(models.Model):
    _name = 'quantity.discount'
    _description = 'Quantity Discount'

    pos_quantity_rel = fields.Many2one('pos.promotion')
    quantity_dis = fields.Integer('Quantity')
    discount_dis = fields.Float('Discount(%)')
    promotion_cost = fields.Float(string="Promotion Cost", required=False)


class QuantityDiscountAmount(models.Model):
    _name = 'quantity.discount.amt'
    _description = "Quantity Discount Amount"

    pos_quantity_amt_rel = fields.Many2one('pos.promotion')
    quantity_amt = fields.Integer('Quantity')
    discount_price = fields.Float('Discount Price (Fixed)')
    promotion_cost = fields.Float(string="Promotion Cost", required=False)


class GetProductDiscount(models.Model):
    _name = 'get.discount'
    _description = "Get Discount"

    pos_quantity_dis_rel = fields.Many2one('pos.promotion')
    product_id_dis = fields.Many2one('product.product', 'Product')
    qty = fields.Float("Quantity")
    discount_dis_x = fields.Float('Discount (%)')
    promotion_cost = fields.Float(string="Promotion Cost", required=False)


class DiscountOnMultipleProducts(models.Model):
    _name = 'discount.multi.products'
    _description = "Apply Discount on Multiple Products"

    multi_product_dis_rel = fields.Many2one('pos.promotion')
    products_discount = fields.Float("Discount")
    product_ids = fields.Many2many(comodel_name='product.product', string="Products")
    promotion_cost = fields.Float(string="Promotion Cost", required=False)


class DiscountOnMultipleCategories(models.Model):
    _name = 'discount.multi.categories'
    _description = "Apply Discount on Multiple Categories"

    multi_category_dis_rel = fields.Many2one('pos.promotion')
    category_discount = fields.Float("Discount")
    category_ids = fields.Many2many(comodel_name='pos.category', string="Categories")
    supplier_ids = fields.Many2many(comodel_name='res.partner', string="Suppliers")
    promotion_cost = fields.Float(string="Promotion Cost", required=False)


class DiscountOnAbovePrice(models.Model):
    _name = 'discount.above.price'
    _description = "Apply Discount, if price is above define price"

    pos_promotion_id = fields.Many2one('pos.promotion')
    discount = fields.Float("Discount (%)")
    price = fields.Float("Price")
    discount_type = fields.Selection([('percentage', 'Percentage'),
                                      ('fix_price', 'Fix Price'),
                                      ('free_product', 'Free Product')])
    fix_price_discount = fields.Char("Price Discount")
    product_category_ids = fields.Many2many('pos.category', 'discount_pos_categ_rel', string="Categories")
    product_brand_ids = fields.Many2many('product.brand', 'product_brand_rel', string="Product Brands")
    free_product = fields.Many2one('product.product', string="Product")
    promotion_cost = fields.Float(string="Promotion Cost", required=False)


class DayWeek(models.Model):
    _name = 'day.week'
    _description = "Promotion Week Days"

    name = fields.Char(string="Name")


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    is_promotion = fields.Boolean(string="Is Promotion")
    promotion_code = fields.Char(string="Promotion Code")
    promotion_cost = fields.Float(string="Promotion Cost", readonly=True)

class PosOrder(models.Model):
    _inherit = 'pos.order'
    is_delivery = fields.Boolean()

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    is_promotion = fields.Boolean(string="Is Promotion")
    promotion_cost = fields.Float(string="Promotion Cost", required=False)
    promotion_code = fields.Char(string="Promotion Code")

    def _select(self):
        return super(PosOrderReport, self)._select() + ", l.is_promotion,l.promotion_cost,l.promotion_code"

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ",l.is_promotion,l.promotion_cost,l.promotion_code"


class ProudctTemplate(models.Model):
    _inherit = 'product.template'
    supplier_id = fields.Many2one(comodel_name="res.partner", string="Supplier", required=False)

# -*- coding: utf-8 -*- 
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError


class PosVoucher(models.Model):
    _name = 'pos.voucher'

    name = fields.Char(string="Voucher Name", required=True)
    voucher_type = fields.Selection(
        selection=[
            ('product', 'Product'),
            ('multi', 'Multi Product'),
            ('all', 'All Products'),
        ], string="Applicable on ", default='product',required=True
    )
    discount_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed Amount'),
            ('percent', 'Percentage')
        ], string="Discount Type ", default='fixed',required=True
    )
    calc_by = fields.Selection(
        selection=[
            ('order', 'Total Pos Order'),
            ('product', 'Products Price')
        ], string="Calculate By", default='product',required=True
    )
    coupon_usage = fields.Selection(
        selection=[
            ('limited', 'Limited'),
            ('no_limit', 'No Limits'),
        ], string="Coupons Usage", default='limited', required=True
    )
    discount_rule = fields.Selection(
        selection=[
            ('alert', "Doesn't Allow Discount Over Price"),
            ('allow', "Allow Discount Anyway"),
        ], string="Discount Rule",required=True, default='alert', help="its ask if you would like to use discount even if product price less than discount value or order total."
    )
    product_id = fields.Many2one('product.product', string="Product")
    product_ids = fields.Many2many('product.product', string="Products")
    except_product_ids = fields.Many2many('product.product', string="Except Products",relation="voucher_expect_prods")
    except_category_ids = fields.Many2many('product.category', string="Except Categories",relation="vourcher_expect_category")
    # except_check = fields.Boolean(string="Except")
    except_check = fields.Selection(string="Except", selection=[('product', 'Product'), ('category', 'Category'), ], required=False)
    coupon_ids = fields.One2many('pos.coupon', 'voucher_id', string="Products", readonly=True)
    coupon_usage_limit = fields.Integer(string="Coupon Limit", default=1)
    coupons_counts = fields.Integer(string="Coupons Count To Generate", required=True)
    discount_value = fields.Float(string="Discount Value", required=True)
    min_order_value = fields.Float(string="Minimum Order Value", required=True, help="apply when the order total value more than this value")
    start_date = fields.Date(string="Start Date", required=True, help='The Start date of Voucher.')
    end_date = fields.Date(string="End Date", required=True, help='The expiry date of Voucher.')
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('generated', 'Coupons Generated'),
        ], string="Status", default='new',required=True, copy=False
    )
    remove_promotion = fields.Boolean(string="Remove Promotion")
    disable_combo = fields.Boolean(string="Disable Combo")
    partner_id = fields.Many2one('res.partner', string="Partner")
    partner_limit = fields.Float(string='Partner Limit')



    def action_generated(self):
        self.write({'state': 'generated'})


    def generate_coupons(self):
        Coupon = self.env['pos.coupon']
        data_to_create = {
            'voucher_id': self.id,
            'voucher_type': self.voucher_type,
            'except_check': self.except_check,
            'discount_type': self.discount_type,
            'calc_by': self.calc_by,
            'coupon_usage': self.coupon_usage,
            'product_id': self.product_id.id,
            'product_ids': [(6,0, self.product_ids.ids)],
            'except_product_ids': [(6,0, self.except_product_ids.ids)],
            'except_category_ids': [(6,0, self.except_category_ids.ids)],
            'coupon_usage_limit': self.coupon_usage_limit,
            'discount_value': self.discount_value,
            'min_order_value': self.min_order_value,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'discount_rule': self.discount_rule,
            'partner_id': self.partner_id.id,
            'partner_limit': self.partner_limit,
        }
        print('data_to_create', data_to_create)
        for i in range(self.coupons_counts):
            Coupon.create(data_to_create)
        self.action_generated()
        return True

    @api.constrains('coupons_counts')
    def _constrains_coupons_counts(self):
        if self.coupons_counts < 1:
            raise ValidationError('Coupon count must be positave.')

    @api.constrains('discount_type', 'discount_value')
    def _constrains_discount_type(self):
        if self.discount_type == 'percent':
            if self.discount_value > 100:
                raise ValidationError('You can not set Discount Value > 100 while you select Percentage Type.')

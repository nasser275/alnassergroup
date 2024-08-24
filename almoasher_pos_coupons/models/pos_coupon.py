# -*- coding: utf-8 -*-
import string
import random
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class PosCoupon(models.Model):
    _name = 'pos.coupon'

    def get_code(self):
        size = 10
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    name = fields.Char(string="Code", default=get_code, copy=False, required=True)
    voucher_id = fields.Many2one('pos.voucher', string="Voucher", required=True, copy=False)
    remove_promotion = fields.Boolean(string="Remove Promotion", related='voucher_id.remove_promotion', store=True,
                                      readonly=False)
    disable_combo = fields.Boolean(string="Disable Combo", related='voucher_id.disable_combo', store=True,
                                   readonly=False)
    used_times = fields.Integer(string="Used Times", compute="_compute_used_times", store=True, index=True, copy=False)
    # done_used_times = fields.Integer(compute='_compute_used_times', string='Done Used Times', copy=False)
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('available', 'Available In POS'),
            ('used', 'Fully Used'),
            ('deleted', 'Deleted'),
        ], string="Status", default='active', required=True, copy=False
    )
    voucher_type = fields.Selection(
        selection=[
            ('product', 'Product'),
            ('multi', 'Multi Product'),
            ('all', 'All Products'),
        ], string="Applicable on ", default='product', required=True
    )
    discount_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed Amount'),
            ('percent', 'Percentage')
        ], string="Discount Type ", default='fixed', required=True
    )
    calc_by = fields.Selection(
        selection=[
            ('order', 'Total Pos Order'),
            ('product', 'Products Price')
        ], string="Calculate By", default='product', required=True
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
        ], string="Discount Rule", required=True, default='alert',
        help="its ask if you would like to use discount even if product price less than discount value or order total."
    )
    product_id = fields.Many2one('product.product', string="Product")
    # except_check = fields.Boolean(string="Except")
    except_check = fields.Selection(string="Except", selection=[('product', 'Product'), ('category', 'Category'), ],
                                    required=False)
    product_ids = fields.Many2many('product.product', string="Products")
    except_product_ids = fields.Many2many('product.product', string="Except Products", relation="coupon_expect_prods")
    except_category_ids = fields.Many2many('product.category', string="Except Categories",
                                           relation="coupon_expect_category")
    coupon_lines = fields.One2many('pos.coupon.line', 'coupon_id', string="Coupon Lines", required=True)
    coupon_usage_limit = fields.Integer(string="Coupon Limit", default=1)
    discount_value = fields.Float(string="Discount Value", required=True)
    min_order_value = fields.Float(string="Minimum Order Value", required=True)
    start_date = fields.Date(string="Start Date", required=True, help='The Start date of Voucher.')
    end_date = fields.Date(string="End Date", required=True, help='The expiry date of Voucher.')
    partner_id = fields.Many2one('res.partner', string="Partner")
    partner_limit = fields.Float(string='Partner Limit')
    partner_total = fields.Float(string='Partner Total',compute='_calc_partner_total',store=True)
    partner_rest = fields.Float(string='Partner-Residual value',compute='_calc_partner_rest',store=True)

    @api.depends('coupon_lines')
    def _calc_partner_total(self):
        for rec in self:
            rec.partner_total=abs(sum(self.env['pos.order.line'].sudo().search([('order_id.coupon_id','=',rec.id),('order_id.partner_id','=',rec.partner_id.id),('product_id.name','=','POS-Coupon-Product')]).mapped('price_unit')))

    @api.depends('partner_total','partner_limit')
    def _calc_partner_rest(self):
        for rec in self:

            rec.partner_rest = rec.partner_limit - rec.partner_total

    def action_deleted(self):
        self.write({'state': 'deleted'})

    def action_available(self):
        self.write({'state': 'available'})

    def action_used(self):
        if self.used_times == self.coupon_usage_limit:
            self.write({'state': 'used'})
        else:
            if self.state in ['used']:
                self.action_available()

    def action_deleted(self):
        self.write({'state': 'deleted'})

    @api.depends('coupon_lines.state')
    def _compute_used_times(self):
        for rec in self:
            # count = rec.coupon_lines.mapped('state').count('done')
            count = len([line for line in rec.coupon_lines if line.state == 'done'])
            print('count -------------------------------------------->', count)
            # rec.done_used_times = count
            rec.used_times = count
            # rec.update_used_times_count(count)

    # @api.onchange('done_used_times')
    # def _onchange_used_times(self):
    #     if self.done_used_times:
    #         self.used_times = self.done_used_times
    #     else:
    #         self.used_times = 0

    @api.model
    def update_used_times_count(self, count):
        self.write({'used_times': count})

    @api.onchange('voucher_id')
    def _onchange_voucher_code(self):
        if self.voucher_id:
            self.voucher_type = self.voucher_id.voucher_type
            self.discount_type = self.voucher_id.discount_type
            self.calc_by = self.voucher_id.calc_by
            self.coupon_usage = self.voucher_id.coupon_usage
            self.product_id = self.voucher_id.product_id.id
            # self.product_ids = self.voucher_id.product_ids.ids
            self.product_ids = [(6, 0, self.voucher_id.product_ids.ids)]
            self.except_product_ids = [(6, 0, self.voucher_id.except_product_ids.ids)]
            self.except_check = self.voucher_id.except_check
            self.coupon_usage_limit = self.voucher_id.coupon_usage_limit
            self.discount_value = self.voucher_id.discount_value
            self.min_order_value = self.voucher_id.min_order_value
            self.start_date = self.voucher_id.start_date
            self.end_date = self.voucher_id.end_date
            self.discount_rule = self.voucher_id.discount_rule
        else:
            self.voucher_type = False
            self.discount_type = False
            self.calc_by = False
            self.coupon_usage = False
            self.product_id = False
            self.product_ids = False
            self.except_product_ids = False
            self.except_check = False
            self.coupon_usage_limit = False
            self.discount_value = False
            self.min_order_value = False
            self.start_date = False
            self.end_date = False
            self.discount_rule = False

    @api.constrains('discount_type', 'discount_value')
    def _constrains_discount_type(self):
        if self.discount_type == 'percent':
            if self.discount_value > 100:
                raise ValidationError('You can not set Discount Value > 100 while you select Percentage Type.')

    @api.constrains('name')
    def _constrains_name(self):
        record_id = self.env['pos.coupon'].search([('name', '=', self.name), ('state', '!=', 'deleted')]) - self
        # print("record_id", record_id)
        if len(record_id) >= 1:
            raise ValidationError('Coupon code already exist.')

    def unlink(self):
        for record in self:
            record.action_deleted()
        return True

    # POS methods which talk with js
    @api.model
    def sync_pos_coupon_to_pos(self, company_id=False):
        domain = [('state', 'in', ['active'])]
        not_synced_read = self.search_read(domain, fields=[])
        not_synced_read_ids = self.search(domain)
        line_domain = [('id', 'in', not_synced_read_ids.ids)]
        not_synced_lines_read = []
        for order in not_synced_read:
            record = self.search([('id', '=', order['id'])])
            not_synced_lines_read = self.env['pos.coupon.line'].search_read(line_domain, fields=[])
            record.sudo().action_available()
        return {"not_synced_read": not_synced_read, "not_synced_lines_read": not_synced_lines_read}

    @api.model
    def sync_deleted_pos_coupon_to_pos(self, company_id=False):
        domain = [('state', 'in', ['deleted'])]
        deleted_not_synced_read = self.search(domain)
        line_domain = [('id', 'in', deleted_not_synced_read.ids)]
        deleted_synced_lines_read = []
        for order in deleted_not_synced_read:
            record = self.search([('id', '=', order.id)])
            deleted_synced_lines_read = self.env['pos.coupon.line'].search(line_domain)
            record.sudo().action_deleted()
        deleted = deleted_not_synced_read.ids if deleted_not_synced_read else False
        deleted_lines = deleted_synced_lines_read.ids if deleted_synced_lines_read else False
        return {'deleted_not_synced_read': deleted, 'deleted_synced_lines_read': deleted_lines}

    @api.model
    def get_last_confirmed_coupon_line_by_order(self, order_name, coupon_id):
        if coupon_id:
            coupon_id = self.env['pos.coupon.line'].search(
                [('coupon_id', '=', coupon_id), ('order_name', '=', order_name), ('state', '=', 'confirmed')],
                order="id desc", limit=1)
        else:
            coupon_id = self.env['pos.coupon.line'].search(
                [('order_name', '=', order_name), ('state', '=', 'confirmed')], order="id desc", limit=1)
        return coupon_id.id or False

    @api.model
    def action_update_data_from_pos(self, data):
        coupon_id = self.env['pos.coupon'].search([('id', '=', data.get('coupon_id'))])
        print("record,data", coupon_id, data)
        if coupon_id:
            if 'state' in data and data.get('state') and data.get('coupon_id'):
                coupon_id.sudo().write({'state': data.get('state')})
            coupon_id.sudo()._compute_used_times()
            coupon_id.sudo().action_used()
            if data.get('coupon_line_data'):
                record = self.env['pos.coupon.line'].sudo().create(data.get('coupon_line_data'))
                if record:
                    coupon_id.sudo()._compute_used_times()
                    coupon_id.sudo().action_used()
            return {'id': coupon_id.id, 'code': coupon_id.name, 'state': coupon_id.state,
                    'used_times': coupon_id.used_times,'partner_total':coupon_id.partner_total}
        else:
            return False

    # @api.model
    # def _get_coupon_status(self,coupon_id):
    #     record = self.search([('id', '=', coupon_id)])
    #     return record.state


class PosCouponLines(models.Model):
    _name = 'pos.coupon.line'
    _description = 'Pos Coupon Line'

    coupon_id = fields.Many2one('pos.coupon', string="Pos Coupon", required=True)
    order_name = fields.Char(string="Pos Order", required=True)
    # order_id = fields.Many2one('pos.order', string="Pos Order", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    # is_done = fields.Boolean(string="Is Done")
    state = fields.Selection(
        selection=[
            ('verified', 'Verified'),
            ('confirmed', 'Confirmed Without Order Compelete'),
            ('done', 'Order Used Coupon Compeleted'),
        ], string="Status"
    )

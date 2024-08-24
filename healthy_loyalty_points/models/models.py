# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class partners_coupons(models.Model):
    _inherit = "pos.coupon"

    customer_id = fields.Many2one('res.partner', string='Customer')


class healthy_loyalty_points(models.Model):
    _name = 'loyalty.subscriber'

    customer_id = fields.Many2one('res.partner', string='Customer')
    customer_phone = fields.Char(related='customer_id.phone', string='Phone')
    customer_mobile = fields.Char(related='customer_id.mobile', string='Mobile')
    code = fields.Char(string='Generated Code', readonly=True)
    is_subscribed = fields.Boolean(string='subscription')
    points = fields.Float(string='Total Points', related='customer_id.total_points', readonly=False)
    date_action = fields.Datetime('Date', required=True, select=True
                                  , default=lambda self: fields.datetime.now())


class healthy_loyalty_points_system(models.Model):
    _name = 'orders.loyalty.points'

    order_id = fields.Many2one('pos.order', string='Order')
    customer_id = fields.Many2one('res.partner', string='Customer')
    points = fields.Float(string='Total Points')
    total_points_amount = fields.Float(string='Total Points Amount')
    total_order_amount = fields.Float(string='Total Amount', related='order_id.amount_total')


class healthy_loyalty_points_redeemed(models.Model):
    _name = 'redeem.loyalty.points'

    customer_id = fields.Many2one('res.partner', string='Customer')
    points = fields.Float(string='Total Points', related='customer_id.total_points')
    coupon = fields.Char(string="Coupon")
    expire_date = fields.Datetime(string='Expiry Date')
    points_amount = fields.Float(string='Total Amount')
    total_points_redeemed = fields.Float(string='Total Point Redeemed')
    points_residual = fields.Float(string='Point Residual')
    check_redeemed = fields.Boolean(string='Is Redeemed', default=False)


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    points_subscriped = fields.Boolean(string='Points Subscribed')
    code = fields.Char(string='Code')
    total_points = fields.Float(string='Total Loyalty Points')

    def modify_code_partners(self):
        partners = self.env['res.partner'].sudo().search([('points_subscriped', '=', False)])
        for i in partners:
            subscriber = self.env['loyalty.subscriber'].sudo().search([('customer_id', '=', i.id)])
            if subscriber:
                i.barcode = subscriber.code
                i.code = subscriber.code
                i.points_subscriped = True


class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    is_point_converted = fields.Boolean(string='Points Converted')
    point_rate = fields.Integer()

    def convert_points(self):
        # start_date = self.env['ir.config_parameter'].sudo().get_param('healthy_loyalty_points.loyal_points_start')
        point_rate = self.env['ir.config_parameter'].sudo().get_param('healthy_loyalty_points.points_rate')
        amount_rate = self.env['ir.config_parameter'].sudo().get_param('healthy_loyalty_points.amount_rate')
        for order in self.env['pos.order'].search([('is_point_converted', '=', False)]):
            sub_date = order.env['loyalty.subscriber'].sudo().search(
                [('customer_id', '=', order.partner_id.id)]).date_action
            if sub_date:
                if order.state in ['paid', 'done'] and not order.return_reason and order.date_order >= sub_date:
                    if order.env['loyalty.subscriber'].sudo().search(
                            [('customer_id', '=', order.partner_id.id)]).is_subscribed:
                        order.partner_id.points_subscriped = True
                        if int(point_rate) > 0:
                            points = order.amount_total / int(point_rate)
                        else:
                            points = 0
                        points_generate = self.env['orders.loyalty.points'].create({
                            'customer_id': order.partner_id.id,
                            'order_id': order.id,
                            'points': points,
                            'total_points_amount': points / int(amount_rate) if int(amount_rate) > 0 else 0
                        })

                        if points_generate:
                            order.is_point_converted = True
                            customer_points = order.partner_id.total_points
                            order.partner_id.total_points = customer_points + points

                elif order.state in ['paid', 'done'] and order.return_reason and order.date_order >= sub_date:
                    if order.env['loyalty.subscriber'].sudo().search(
                            [('customer_id', '=', order.partner_id.id)]).is_subscribed:
                        order.partner_id.points_subscriped = True
                        if int(point_rate) > 0:
                            points = order.amount_total / int(point_rate)
                        else:
                            points = 0
                        points_generate = self.env['orders.loyalty.points'].create({
                            'customer_id': order.partner_id.id,
                            'order_id': order.id,
                            'points': points,
                            'total_points_amount': points / int(amount_rate) if int(amount_rate) > 0 else 0
                        })

                        if points_generate:
                            order.is_point_converted = True
                            customer_points = order.partner_id.total_points
                            order.partner_id.total_points = customer_points + points

    def residual_points(self):
        amount_rate = self.env['ir.config_parameter'].sudo().get_param('healthy_loyalty_points.amount_rate')
        for rec in self.env['redeem.loyalty.points'].sudo().search([]):
            # rec.points_residual = rec.points - rec.total_points_redeemed
            rec.points_amount = rec.total_points_redeemed / int(amount_rate) if int(amount_rate) > 0 else 0

            customer_points_redeemed = self.env['redeem.loyalty.points'].sudo().search(
                [('customer_id', '=', rec.customer_id.id), ('check_redeemed', '=', False)])

            if customer_points_redeemed:
                customer_points = rec.customer_id.total_points
                rec.customer_id.total_points = customer_points - customer_points_redeemed[-1].total_points_redeemed
                customer_points_redeemed.check_redeemed = True


class ResCompanySettings(models.Model):
    _inherit = "res.company"

    points_rate = fields.Integer(string='Points Rate For Redeemed')
    amount_rate = fields.Integer(string='Amount Rate to Convert From Points')


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    points_rate = fields.Integer(related='company_id.points_rate', readonly=False,
                                 string='Points Rate For Redeemed',
                                 config_parameter='healthy_loyalty_points.points_rate')
    amount_rate = fields.Integer(related='company_id.amount_rate', readonly=False,
                                 string='Amount Rate to Convert From Points',
                                 config_parameter='healthy_loyalty_points.amount_rate')
    loyal_points_start = fields.Datetime(string='Loyal Points Starting Date')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        with_user = self.env['ir.config_parameter'].sudo()
        with_user.set_param('healthy_loyalty_points.loyal_points_start', self.loyal_points_start)

        return res

    @api.model
    def get_values(self):
        values = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        values['loyal_points_start'] = with_user.get_param('healthy_loyalty_points.loyal_points_start')
        return values

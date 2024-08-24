# -*- coding: utf-8 -*- 
from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError,ValidationError
import logging
import psycopg2
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    coupon_id = fields.Many2one('pos.coupon', string='Pos Coupon', readonly=True, copy=False)
    def _order_fields(self, ui_order):
        order = super(PosOrder, self)._order_fields(ui_order)
        print("DD>>",ui_order)
        order['coupon_id'] = ui_order.get('coupon_id')
        return order

    @api.model
    def create(self, values):
        res = super(PosOrder, self).create(values)
        print(">>>",values)
        coupon_line_data = {'state': 'done', 'coupon_id': res.coupon_id.id,
                                'order_name': res.name,
                                'partner_id': res.partner_id.id}
        data = {'coupon_id': res.coupon_id.id, 'coupon_line_data': coupon_line_data}
        res.coupon_id.action_update_data_from_pos(data)

        return res



class PosConfig(models.Model):
    _inherit = 'pos.config'

    show_coupon = fields.Boolean(string='Show Coupons', default=True)
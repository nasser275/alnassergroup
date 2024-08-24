# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_loyalty_exclude = fields.Boolean(string="Excluded from loyalty programs", default=False)

    def write(self, values):
        is_loyalty_exclude_change = False
        if values.get('is_loyalty_exclude') and values['is_loyalty_exclude']:
            is_loyalty_exclude_change = True
            values['loyalty_points'] = 0
        res = super(ResPartner, self).write(values)
        if is_loyalty_exclude_change and self.is_loyalty_exclude:
            pos_orders = self.env['pos.order'].search([('partner_id', '=', self.id), ('loyalty_points', '!=', 0)])
            for pos_order in pos_orders:
                pos_order.write({'loyalty_points': 0})
        return res

    def create(self, values):
        res=super(ResPartner, self).create(values)
        if self.env.user.branch_id.active_auto_set_point_for_customer and  self.env.user.branch_id.loyalty_points :
            res.loyalty_points= self.env.user.branch_id.loyalty_points

        return res



class Branch(models.Model):
    _inherit = 'res.branch'
    active_auto_set_point_for_customer = fields.Boolean(string='Active Auto Set Loyalty Points For New Customer')
    loyalty_points = fields.Float(string=' Loyalty Points')

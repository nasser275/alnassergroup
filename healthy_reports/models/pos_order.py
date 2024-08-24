from odoo import models, fields, api
from datetime import datetime


class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    is_total_computed = fields.Boolean(string='Total Without Tax Computed')


class PosPaymentInherit(models.Model):
    _inherit = "pos.payment"

    total_without_tax = fields.Float(string='Total Without Tax')
    total_tax = fields.Float(string='Total Tax')

    @api.depends('pos_order_id')
    def _comp_total_without_tax_order(self, reclimit=50):
        for rec in self.env['pos.order'].sudo().search([('is_total_computed', '=', False)], order="date_order desc",
                                                       limit=reclimit):
            print('Order IDD', rec.id)
            pos_lines = rec.env['pos.order.line'].sudo().search([('order_id', '=', rec.id)])
            total = 0
            for line in pos_lines:
                total += line.price_subtotal

            for pay in rec.payment_ids:
                pay.total_without_tax = total
                pay.total_tax = rec.amount_tax
                print('Order Total Without Tax >>', pay.total_without_tax)
                print('Order Total Without Tax >>', pay.total_tax)
            rec.is_total_computed = True

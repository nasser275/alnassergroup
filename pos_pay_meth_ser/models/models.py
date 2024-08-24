# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosPaymentMethod(models.Model):
    _inherit='pos.payment.method'

    serial_number_required = fields.Boolean(string="Serial Number Required?")
class PosPayment(models.Model):
    _inherit = 'pos.payment'
    transaction_id = fields.Char('Serial No')

class PosOrder(models.Model):
    _inherit = 'pos.order'
    payment_serial_no = fields.Char('Payment Serial No')

    def _order_fields(self, ui_order):
        order = super(PosOrder, self)._order_fields(ui_order)
        order['payment_serial_no'] = ui_order.get('payment_serial_no')
        return order
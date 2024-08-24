# -*- coding: utf-8 -*-

from odoo import fields, models, _
import xlsxwriter
import base64
import os
from odoo.exceptions import ValidationError


class CancelWiz(models.TransientModel):
    _name = 'pos.cancel.wiz'
    cancel_reason_id = fields.Many2one(comodel_name="pos.cancel.reasons", string="Cancel Reason", required=True)

    def cancel(self):
        res = self.env['pos.order'].browse(self._context.get('active_ids'))
        for order in res:
            order.action_pos_order_cancel()


class CancelReason(models.Model):
    _name = 'pos.cancel.reasons'

    _rec_name = 'reason'
    reason = fields.Char(string="Reason", required=False)


class ReturnReason(models.Model):
    _name = 'pos.return.reasons'

    _rec_name = 'reason'
    reason = fields.Char(string="Reason", required=False)


class PasswordreturnWiz(models.TransientModel):
    _name = 'pos.password.return.wiz'
    user_password = fields.Char(string="Pos Password", required=True)

    def return_products(self):
        user_pos_password = self.env['res.users'].search([('id', '=', self.env.uid)]).user_password
        if self.user_password == user_pos_password:
            res = self.env['pos.order'].browse(self._context.get('active_ids'))
            print(res)
            for order in res:
                order.validated_refund()
        else:
            raise ValidationError("Uncorrect Password")

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_id = fields.Integer(string='Customer Id', readonly=True)


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    not_send_reason = fields.Char(string='Reason')

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields


class AccountAnalyticBranch(models.Model):
    _inherit = 'res.branch'

    analytic_account = fields.Many2one('account.analytic.account', string='Analytic Account')


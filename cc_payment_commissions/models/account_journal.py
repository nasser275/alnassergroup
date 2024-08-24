from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    provider_account = fields.Many2one(comodel_name='account.account', string='Provider Account')
    amount = fields.Monetary(string='Provider Commission Fixed Fees')
    amount_percentage = fields.Float(string='Provider Commission Percentage')
    currency_id = fields.Many2one(related='company_id.currency_id', readonly=False,
                                  help='The currency used to enter statement',
                                  string="Currency")

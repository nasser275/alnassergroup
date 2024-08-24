from odoo import models, fields, api


class Move(models.Model):
    _inherit = 'account.move'

    refund_type = fields.Selection(string="Refund Type", selection=[('expird', 'Expird'),
                                                                    ('waset', 'Waset'),
                                                                    ('redistributed', 'Redistributed')
        , ('repacking', 'Repacking'), ('industrial', 'Industrial Defects')], required=False)

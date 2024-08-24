from odoo import models, fields, api, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    disable_show_in_franchise = fields.Boolean(related='product_id.disable_show_in_franchise', store=True)

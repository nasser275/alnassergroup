from odoo import api, fields, models
from odoo.exceptions import ValidationError


class User(models.Model):
    _inherit='res.users'
    show_price_control = fields.Boolean(string="Show Price Control")
    show_discount_control = fields.Boolean(string="Show Discount Control")
    can_edit_open_cash_control = fields.Boolean(string="Can Edit Open Cash Control")
    use_pos_password = fields.Boolean(string="Use Pos Password")
    user_password = fields.Char(string="Pos Password")
    show_cash_in_out = fields.Boolean(string="Show Cash In/Out")


from odoo import api, fields, models
from odoo.exceptions import ValidationError


class User(models.Model):
    _inherit='res.users'
    route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        ondelete="restrict",
    )
    return_route_id = fields.Many2one(
        "stock.location.route",
        string="Return Route",
        ondelete="restrict",
    )




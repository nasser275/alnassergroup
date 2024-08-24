from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Sliders(models.Model):
    _name='api.sliders'
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description", required=False)
    image = fields.Binary(string="Image")

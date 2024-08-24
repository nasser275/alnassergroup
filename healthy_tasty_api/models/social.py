from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Social(models.Model):
    _name = 'api.social'
    name = fields.Char(string="Name", required=True)
    url = fields.Char(string="Url")

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Contact(models.Model):
    _name='api.contact.us'
    name = fields.Char(string="Name", required=False)
    email = fields.Char(string="Email", required=False)
    phone = fields.Char(string="Phone", required=False)
    message = fields.Text(string="Message", required=False)

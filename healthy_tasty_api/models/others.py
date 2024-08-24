from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Other(models.Model):
    _name='api.others'
    name = fields.Char(string="Type", required=False)
    content = fields.Text(string="Content", required=False)

class Testimonials(models.Model):
    _name='api.testimonials'
    name = fields.Char(string="Name", required=False)
    description = fields.Text(string="description", required=False)
    image = fields.Binary(string="Image")

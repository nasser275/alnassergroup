from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit = 'product.template'
    is_feature = fields.Boolean(string="Is Feature?")
    is_popular = fields.Boolean(string="Is Popular?")



class Product_Category(models.Model):
    _inherit = 'product.category'
    is_website = fields.Boolean(string="Is Share To Website?")

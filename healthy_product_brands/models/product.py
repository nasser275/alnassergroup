from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit='product.template'
    brand_id = fields.Many2one(comodel_name="healthy.brands", string="Brand", required=False)


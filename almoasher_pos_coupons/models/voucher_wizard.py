import string
import random
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint

class VoucherCreateWizard(models.TransientModel):
    _name='voucher.create_wizard'

    name = fields.Char(string="Name", required=True)
    voucher_type = fields.Selection(
        selection=[
            ('product', 'Product'),
        ], string="Applicable on ", default='product', readonly=True
    )
    product_ids = fields.Many2many('product.product', string="Products")
    # product_categ = fields.Many2one('pos.category', string="Product Category")
    min_value = fields.Integer(string="Minimum Voucher Value", required=True)
    max_value = fields.Integer(string="Maximum Voucher Value", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True, help='The expiry date of Voucher.')


    def action_apply(self):
        VoucherObj = self.env['gift.voucher.pos']
        if self.product_ids:
            for product in self.product_ids:
                VoucherObj.create({
                    "name": "{}-{}".format(self.name, product.name),
                    "voucher_type": self.voucher_type,
                    "product_id": product.id,
                    "min_value": self.min_value,
                    "max_value": self.max_value,
                    "expiry_date": self.expiry_date,
                })

from odoo import api, fields, models
from datetime import datetime

class ProductSupplierinfo(models.Model):
    _inherit='product.supplierinfo'

    price_changing_date = fields.Datetime(string=" Price Changing Date", required=False)
    last_change_price = fields.Float(string="Last Change Price", required=False)

    def write(self, values):
        if 'price' in values.keys():
            values['price_changing_date'] = datetime.now()
            values['last_change_price'] = self.price
            self.push_product_price_change(self.price,values['price'])

        res = super(ProductSupplierinfo, self).write(values)
        return res

    def push_product_price_change(self,from_price,to_price):
        body = """<strong>Vendor Price Change From {from_price} to {to_price} By {user} </strong>""".format(
            from_price=from_price,to_price=to_price,user=self.env.user.name
        )
        if self.product_tmpl_id:
            self.product_tmpl_id.message_post(body=body)
            product=self.env['product.product'].search([('product_tmpl_id','=',self.product_tmpl_id.id)])
            product.message_post(body=body)
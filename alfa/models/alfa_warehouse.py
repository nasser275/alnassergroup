from odoo import models, fields, api


class AlfaWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    is_main_return = fields.Boolean(string='Main', default=False)
    warehouse_product_ids = fields.One2many('stock.quant', 'location_id', string='Available Products',
                                            compute='compute_warehouse_products')

    def compute_warehouse_products(self):
        for products in self:
            warehouse_all_products = self.env['stock.quant'].search([('location_id', 'child_of', self.code),
                                                                     ('product_id.active', '=', True)])
            # print(warehouse_all_products)
            if warehouse_all_products:
                for i in warehouse_all_products:
                    products.warehouse_product_ids = warehouse_all_products
            else:
                products.warehouse_product_ids = False

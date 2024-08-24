# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseProductBarcode(http.Controller):
#     @http.route('/purchase_product_barcode/purchase_product_barcode', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_product_barcode/purchase_product_barcode/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_product_barcode.listing', {
#             'root': '/purchase_product_barcode/purchase_product_barcode',
#             'objects': http.request.env['purchase_product_barcode.purchase_product_barcode'].search([]),
#         })

#     @http.route('/purchase_product_barcode/purchase_product_barcode/objects/<model("purchase_product_barcode.purchase_product_barcode"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_product_barcode.object', {
#             'object': obj
#         })

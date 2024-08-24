# -*- coding: utf-8 -*-
# from odoo import http


# class ProductPriceWithoutTax(http.Controller):
#     @http.route('/combo_tax_edit/combo_tax_edit', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/combo_tax_edit/combo_tax_edit/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('combo_tax_edit.listing', {
#             'root': '/combo_tax_edit/combo_tax_edit',
#             'objects': http.request.env['combo_tax_edit.combo_tax_edit'].search([]),
#         })

#     @http.route('/combo_tax_edit/combo_tax_edit/objects/<model("combo_tax_edit.combo_tax_edit"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('combo_tax_edit.object', {
#             'object': obj
#         })

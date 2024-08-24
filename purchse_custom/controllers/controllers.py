# -*- coding: utf-8 -*-
# from odoo import http


# class PurchseCustom(http.Controller):
#     @http.route('/purchse_custom/purchse_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchse_custom/purchse_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchse_custom.listing', {
#             'root': '/purchse_custom/purchse_custom',
#             'objects': http.request.env['purchse_custom.purchse_custom'].search([]),
#         })

#     @http.route('/purchse_custom/purchse_custom/objects/<model("purchse_custom.purchse_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchse_custom.object', {
#             'object': obj
#         })

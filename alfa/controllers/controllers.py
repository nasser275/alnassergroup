# -*- coding: utf-8 -*-
# from odoo import http


# class Alfa(http.Controller):
#     @http.route('/alfa/alfa/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alfa/alfa/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alfa.listing', {
#             'root': '/alfa/alfa',
#             'objects': http.request.env['alfa.alfa'].search([]),
#         })

#     @http.route('/alfa/alfa/objects/<model("alfa.alfa"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alfa.object', {
#             'object': obj
#         })

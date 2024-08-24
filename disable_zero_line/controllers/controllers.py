# -*- coding: utf-8 -*-
# from odoo import http


# class DisableZeroLine(http.Controller):
#     @http.route('/disable_zero_line/disable_zero_line', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/disable_zero_line/disable_zero_line/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('disable_zero_line.listing', {
#             'root': '/disable_zero_line/disable_zero_line',
#             'objects': http.request.env['disable_zero_line.disable_zero_line'].search([]),
#         })

#     @http.route('/disable_zero_line/disable_zero_line/objects/<model("disable_zero_line.disable_zero_line"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('disable_zero_line.object', {
#             'object': obj
#         })

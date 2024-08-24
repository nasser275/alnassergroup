# -*- coding: utf-8 -*-
# from odoo import http


# class HealthyFranshise(http.Controller):
#     @http.route('/healthy_franshise/healthy_franshise', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/healthy_franshise/healthy_franshise/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('healthy_franshise.listing', {
#             'root': '/healthy_franshise/healthy_franshise',
#             'objects': http.request.env['healthy_franshise.healthy_franshise'].search([]),
#         })

#     @http.route('/healthy_franshise/healthy_franshise/objects/<model("healthy_franshise.healthy_franshise"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('healthy_franshise.object', {
#             'object': obj
#         })

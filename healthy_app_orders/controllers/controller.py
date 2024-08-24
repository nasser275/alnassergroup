# -*- coding: utf-8 -*-


from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)


class WebsiteSale(http.Controller):
    @http.route(
        ['/checkapporder'],
        type='http', auth="user")
    def checkapporder(self):
        orders=request.env['app.order'].search([('state','=','draft'),('sync','=',False)])
        print("D>D>",orders)
        if orders:
            orders.sudo().write({'sync':True})
            return "yes"
        else:
            return "no"







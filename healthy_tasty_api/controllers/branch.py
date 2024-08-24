# -*- coding: utf-8 -*-
from odoo import http, models, fields
from odoo.http import Controller, request, route
from .config import validate_data, get_image_url_for_prod


class APIBranch(http.Controller):

    @http.route('/api/v1/branch/list', type='json', auth="none", methods=['GET'])
    def list(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            branchs = request.env['res.branch'].sudo().search([], limit=limit, offset=offset)
            print(">D>D", branchs)
            vals = []
            for branch in branchs:

                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(branch, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(branch, field).id
                        })
                    elif 'image' in field:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_for_prod(base, branch.id)
                        })
                    else:
                        val.update({
                            field: getattr(branch, field)
                        })
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/branch', type='json', auth="none", methods=['GET'])
    def branch(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        branch_id = data.get('branch_id')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            if branch_id:
                branchs = request.env['res.branch'].sudo().search([('id', '=', int(branch_id))])
            else:
                branchs = []
            vals = []
            for branch in branchs:
                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(branch, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(branch, field).id
                        })
                    elif 'image' in field:
                        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_for_prod(base, branch.id)
                        })
                    else:
                        val.update({
                            field: getattr(branch, field)
                        })
                vals.append(val)
            return {'result': vals}

    def get_fields(self):
        product_fields = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.branch_fields')
        fields = ['id']
        try:
            fields = eval(product_fields)
        except:
            pass
        return fields

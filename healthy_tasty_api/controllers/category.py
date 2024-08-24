# -*- coding: utf-8 -*-
from odoo import http, models, fields
from odoo.http import Controller, request, route
from .config import validate_data, get_image_url_512


class APICategory(http.Controller):

    @http.route('/api/v1/categ/list', type='json', auth="none", methods=['GET'])
    def list(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        order_by = data.get('order_by', None)
        categ_ids = data.get('categ_ids')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            if categ_ids:
                categs = request.env['product.category'].sudo().search(
                    [('id', 'in', categ_ids), ('is_website', '=', True)], limit=int(limit),
                    offset=int(offset), order=order_by)
            else:
                categs = request.env['product.category'].sudo().search([('is_website', '=', True), ('parent_id', '=', False)], limit=int(limit),
                                                                       offset=int(offset),
                                                                       order=order_by)
            vals = []

            for categ in categs:
                child = []
                val = {}
                parents = request.env['product.category'].sudo().search(
                    [('parent_id', '=', categ.id), ('is_website', '=', True)])
                for parent in parents:
                    child.append({'id': parent.id,
                                  'name': parent.name})
                val.update({'id': categ.id,
                            'name': categ.name,
                            'child': child})
                # val = {}
                # for field in fields:
                #     if '.display_name' in field:
                #         field = field.split('.')[0]
                #         val.update({
                #             field.replace('.', '_') + '_name': getattr(categ, field).display_name
                #         })
                #     elif '.id' in field:
                #         field = field.split('.')[0]
                #         val.update({
                #             field: getattr(categ, field).id
                #         })
                #     elif 'image' in field:
                #         base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                #         field = field.split('.')[0]
                #         val.update({
                #             field: get_image_url_512(base, categ.id)
                #         })
                #     else:
                #         val.update({
                #             field: getattr(categ, field)
                #         })
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/categ', type='json', auth="none", methods=['GET'])
    def categ(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        categ_id = data.get('categ_id')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            if categ_id:
                categs = request.env['product.category'].sudo().search(
                    [('id', '=', int(categ_id)), ('is_website', '=', True)])
            else:
                categs = []
            vals = []
            for categ in categs:
                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(categ, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(categ, field).id
                        })
                    elif 'image' in field:
                        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        field = field.split('.')[0]
                        val.update({
                            field: get_image_url_512(base, categ.id)
                        })
                    else:
                        val.update({
                            field: getattr(categ, field)
                        })
                vals.append(val)
            return {'result': vals}

    def get_fields(self):
        category_fields = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.category_fields')
        fields = ['id']
        try:
            fields = eval(category_fields)
        except:
            pass
        return fields

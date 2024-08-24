# -*- coding: utf-8 -*-
from odoo import http, models, fields
from odoo.http import Controller, request, route
from .config import validate_data, get_image_url_for_sliders, get_image_url_for_testimonials
import re


class APIOther(http.Controller):

    @http.route('/api/v1/social', type='json', auth="none", methods=['GET'])
    def social(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            socials = request.env['api.social'].sudo().search([], limit=limit, offset=offset)
            vals = []
            for social in socials:
                val = {
                    social.name: social.url
                }
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/sliders', type='json', auth="none", methods=['GET'])
    def sliders(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        else:
            sliders = request.env['api.sliders'].sudo().search([], limit=limit, offset=offset)
            vals = []
            for slider in sliders:
                val = {
                    'name': slider.name,
                    'description': slider.description,
                    'image': get_image_url_for_sliders(base, slider.id)
                }
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/others', type='json', auth="none", methods=['GET'])
    def get_others(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        type = data.get('type')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            if type:
                others = request.env['api.others'].sudo().search([('name', '=', type)], limit=limit, offset=offset)
            else:
                others = request.env['api.others'].sudo().search([], limit=limit, offset=offset)

            vals = []
            for other in others:
                val = {
                    'type': other.name,
                    'content': other.content,
                }
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/testimonials', type='json', auth="none", methods=['GET'])
    def testimonials(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        else:
            testimonials = request.env['api.testimonials'].sudo().search([], limit=limit, offset=offset)
            vals = []
            for testimonial in testimonials:
                val = {
                    'name': testimonial.name,
                    'description': testimonial.description,
                    'image': get_image_url_for_testimonials(base, testimonial.id),
                    'create_date': testimonial.create_date
                }
                vals.append(val)
            return {'result': vals}

    @http.route('/api/v1/contact_us', type='json', auth="none", csrf=False, methods=['POST'])
    def contact_us(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')
        if not self.is_valid_email(email):
            response['result'] = []
            response['message'] = "Invalid email address"
            response['status'] = 301
            return response
        res = request.env['api.contact.us'].sudo().create({
            'name': name,
            'email': email,
            'phone': phone,
            'message': message,
        })
        if res:
            response['status'] = 200
            response['message'] = "Success."

        else:
            response['message'] = 'not created'
            response['code'] = 505
        return response

    def is_valid_email(self, email):
        regex = r"^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
        return re.search(regex, email)

    @http.route('/api/v1/common_question', type='json', auth="none", methods=['GET'])
    def common_question(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            questions = request.env['common.questions'].sudo().search([], limit=limit, offset=offset)
            vals = []
            for question in questions:
                val = {
                    'title': question.name,
                    'description': question.description,
                }
                vals.append(val)
            return {'result': vals}

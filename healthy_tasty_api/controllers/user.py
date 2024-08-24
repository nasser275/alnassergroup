# -*- coding: utf-8 -*-
import datetime
import re
import jwt
from odoo import http, models, fields
from odoo.http import Controller, request, route
from .config import validate_data, get_image_url_for_user
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class APIUser(http.Controller):

    def check_login_by_id(self, user_id):
        user = request.env['res.users'].sudo().search([('id', '=', user_id)], limit=1)
        if user:
            return user
        return False

    @http.route('/api/v1/login', type='json', auth="none", csrf=False, methods=['POST'])
    def web_login(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        user_login = data.get('user_email')
        user_password = data.get('user_password')
        try:
            uid = request.session.authenticate(request.env.cr.dbname, user_login, user_password)
            user = request.env['res.users'].sudo().browse(uid)
            if user:
                user_dct = {
                    'user_id': user.id,
                    'partner_id': user.partner_id.id,
                    'user_name': user.name,
                    'user_photo': get_image_url_for_user(base, user.id),
                }
                data = self.create_token(user, user_login, token)
                user.sudo().update_user({'access_token_ids': [(0, 0, data)]})
                user_dct.update({
                    'access_token': data.get('token')
                })
                response['result'] = user_dct
                response['message'] = "Success."
                response['code'] = 200
            else:
                response['message'] = "User doesn't exist"
                response['code'] = 301
        except:
            response['message'] = "User doesn't exist"
            response['code'] = 601
        return response

    @http.route('/api/v1/get_user_info', type='json', auth="none", csrf=False, methods=['GET'])
    def get_user_info(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        user_id = data.get('user_id')
        user_token = data.get('user_token')
        chck_user_token = self.verify(user_token)
        if chck_user_token == False:
            response['message'] = "User Token invalid or expired"
            response['code'] = "301"
            return response

        if user_id:
            user_exist = self.check_login_by_id(int(user_id))
            if user_exist:
                user_dct = {
                    'user_id': user_exist.id,
                    'partner_id': user_exist.partner_id.id,
                    'user_name': user_exist.name,
                    'user_email': user_exist.login,
                    'user_photo': get_image_url_for_user(base, user_exist.id),
                    'user_phone': user_exist.phone,

                }
                response['result'] = user_dct
                response['message'] = "Success."
                response['code'] = 200
            else:
                response['message'] = "User doesn't exist"
                response['code'] = 301
        else:
            response['message'] = "User ID Required"
            response['code'] = 601
        return response

    @http.route('/api/v1/save_user_info', type='json', auth="public", csrf=False, methods=['POST'])
    def save_user_info(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        user_login = data.get('user_email')
        user_phone = data.get('user_phone')
        user_token = data.get('user_token')
        chck_user_token = self.verify(user_token)
        if chck_user_token == False:
            response['message'] = "User Token invalid or expired"
            response['code'] = "301"
            return response

        user_exist = self.check_login_by_id(int(user_id))
        if user_exist:
            user_dct = {
                'name': str(user_name)
            }
            if user_phone:
                user_dct.update({'phone': user_phone})

            if user_login:
                user_dct.update({'login': user_login})

            user_exist.sudo().write(user_dct)

            response['result'] = "Update Data"
            response['message'] = "Success."
            response['code'] = 200
        else:
            response['message'] = "User doesn't exist"
            response['code'] = 301
        return response

    def check_user_exist(self, login):
        user = request.env['res.users'].sudo().search([('login', '=', login)])
        if user:
            return True
        return False

    # - we have api called Sign Up to register new portal account
    @http.route('/api/v1/sign_up', type='json', auth="none", csrf=False, methods=['POST'])
    def sign_up(self, **args):

        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        user_name = data.get('user_name')
        user_email = data.get('user_email')
        user_password = data.get('user_password') or '222'
        user_phone = data.get('user_phone') or None
        user_exist = self.check_user_exist(user_email)
        if not self.is_valid_email(user_email):
            response['result'] = []
            response['message'] = "Invalid email address"
            response['status'] = 301
            return response
        if not user_exist:
            dct_partner = {
                'name': user_name,
                'phone': user_phone,

            }
            partner = request.env['res.partner'].sudo().create_partner(dct_partner)
            if partner:
                base_company = request.env.ref('base.main_company')
                portal_group = request.env.ref('base.group_portal')
                portal_user = request.env['res.users'].sudo().create_user({
                    'login': user_email,
                    'password': user_password or None,
                    'partner_id': partner.id,
                    'groups_id': [(6, 0, [portal_group.id])],
                    'company_ids': [(6, 0, [base_company.id])],
                    'company_id': base_company.id,
                })
                if portal_user:
                    response['status'] = 200
                    response['message'] = "Success."

        else:
            response['message'] = 'user exist already'
            response['code'] = 505
        return response

    def is_valid_email(self, email):
        regex = r"^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
        return re.search(regex, email)

    def create_token(self, user, login, key):
        try:
            exp = datetime.datetime.utcnow() + datetime.timedelta(days=30)
            payload = {
                'exp': exp,
                'iat': datetime.datetime.utcnow(),
                'sub': user.id,
                'lgn': login,
            }

            token = jwt.encode(
                payload,
                key,
                algorithm='HS256'
            )

            return self.save_token(token, exp)
        except Exception as ex:
            pass
            raise

    def save_token(self, token, exp):
        return {
            'expires': exp.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'token': token,
        }

    def verify(self, token):
        print(">D>D>", token)
        record = request.env['jwt_provider.access_token'].sudo().search([
            ('token', '=', token)
        ])

        if len(record) != 1:
            return False

        if record.is_expired:
            return False

        return record.user_id

    @http.route('/api/v1/logout', type='json', auth="none", csrf=False, methods=['POST'])
    def web_logout(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        user_token = data.get('user_token')
        try:
            access_token = request.env['jwt_provider.access_token'].sudo().search([
                ('token', '=', user_token)
            ])
            if access_token:
                access_token.unlink()
                response['message'] = "Success."
                response['code'] = 200
            else:
                response['message'] = "User Token doesn't exist"
                response['code'] = 301
        except:
            response['message'] = "User Token doesn't exist"
            response['code'] = 601
        return response

    @http.route('/api/v1/reset_password', type='json', auth="none", csrf=False, methods=['POST'])
    def reset_password(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        user_id = data.get('user_id')
        user_password = data.get('user_password', '1')
        user_token = data.get('user_token')
        chck_user_token = self.verify(user_token)
        if chck_user_token == False:
            response['message'] = "User Token invalid or expired"
            response['code'] = "301"
            return response

        user_exist = self.check_login_by_id(int(user_id))
        if user_exist:
            user_dct = {
            }
            if user_password:
                user_dct.update({'password': user_password})

            user_exist.sudo().write(user_dct)

            response['result'] = "Update Password"
            response['message'] = "Success."
            response['code'] = 200
        else:
            response['message'] = "User doesn't exist"
            response['code'] = 301
        return response

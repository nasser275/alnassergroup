# -*- coding: utf-8 -*-


from odoo import http, models, fields
from odoo.http import Controller, request, route
from .config import validate_data, get_image_url_for_user
import datetime
import re
from datetime import datetime, timedelta


class HealthyCoupons(http.Controller):
    @http.route('/api/v1/customer_app_coupon', type='json', auth="none", csrf=False, methods=['POST'])
    def customer_subscribe(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        customer_id = int(data.get('customer_id')) if data.get('customer_id') else False
        phone = data.get('phone')

        if customer_id or phone:
            print('Before Create')
            customer = self._get_or_create_customer(data)
            print('After Create', customer)

            if customer:
                voucher = request.env['pos.voucher'].sudo().search(
                    [('id', '=', 219)], limit=1)
                coupon = request.env['pos.coupon'].sudo().search(
                    [('customer_id', '=', customer), ('voucher_id', '=', voucher.id)], limit=1)
                if coupon:
                    response['result'] = "Customer Coupon Generated Successfully"
                    response['customer_id'] = customer
                    response['coupon'] = coupon.name
                    response['coupon_value'] = coupon.discount_value
                    response['coupon_expired_date'] = coupon.end_date
                    response['coupon_valid'] = 'Valid' if coupon.used_times == 0 else 'Not Valid'
                    response['message'] = "Success"
                    response['code'] = 200
                    return response
                else:
                    coupon_gen = request.env['pos.coupon'].sudo().search(
                        [('customer_id', '=', False), ('voucher_id', '=', voucher.id)], limit=1)
                    coupon_gen.customer_id = customer
                    response['result'] = "Customer Coupon Generated Successfully"
                    response['customer_id'] = customer
                    response['coupon'] = coupon_gen.name
                    response['coupon_value'] = coupon_gen.discount_value
                    response['coupon_expired_date'] = coupon_gen.end_date
                    response['coupon_valid'] = 'Valid' if coupon_gen.used_times == 0 else 'Not Valid'
                    response['message'] = "Success"
                    response['code'] = 200
                    return response

            else:
                response['customer_id'] = False
                response['coupon'] = False
                response['message'] = "Customer ID Is Invalid Or Missing Data"
                response['code'] = 401

                return response

    def _get_or_create_customer(self, data):
        partner_id = False
        if data.get('customer_id') or data.get('phone'):
            phone_woSymbol = re.sub(r"[^0-9+._ -]+", "", data.get('phone'))
            phone_woSpace = phone_woSymbol.replace(" ", "")
            phone_wCode = '+2' + phone_woSpace
            partner = request.env['res.partner'].sudo().search(['|', '|', ('id', '=', data.get(
                'customer_id')), ('phone', '=', phone_wCode), ('phone', '=', phone_woSpace)], limit=1)
            if partner:
                partner_id = partner.id
            # else:
            #     partner_id = request.env['res.partner'].sudo().create({
            #         'name': data.get('customer_name'),
            #         'customer_id': data.get('customer_id'),
            #         'phone': data.get('phone'),
            #     }).id
        # else:
        #     partner_id = request.env['res.partner'].sudo().create({
        #         'name': data.get('customer_name'),
        #         'customer_id': data.get('customer_id'),
        #         'phone': data.get('phone'),
        #     }).id
        return partner_id

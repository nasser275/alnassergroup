# -*- coding: utf-8 -*-


from odoo import http, models, fields
from odoo.http import Controller, request, route
from .config import validate_data, get_image_url_for_user
import datetime
from datetime import datetime, timedelta


class HealthyLoyaltyPoints(http.Controller):
    @http.route('/api/v1/customer_subscribe', type='json', auth="none", csrf=False, methods=['POST'])
    def customer_subscribe(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        customer_id = int(data.get('customer_id'))
        code = data.get('code')
        is_valid = data.get('is_valid')
        if not code:
            response['message'] = "PLease add Code Generated"
            response['code'] = 301
            return response
        if customer_id:
            customer = request.env['loyalty.subscriber'].sudo().search([('customer_id', '=', customer_id)])

            if customer:
                user_dct = {
                    'customer_id': customer.id,
                    'code': customer.code,
                    'is_subscribed': customer.is_subscribed
                }
                response['result'] = user_dct
                response['message'] = "Success"
                response['code'] = 200
                return response
            else:
                check_exist = request.env['res.partner'].sudo().search(
                    ['|', ('id', '=', customer_id), ('phone', '=', data.get('phone'))], limit=1)
                if check_exist:
                    loyal = request.env['loyalty.subscriber'].sudo().create({
                        'customer_id': check_exist.id,
                        'code': code,
                        'is_subscribed': is_valid
                    })
                    # check_exist.code = code
                    # check_exist.barcode = code
                    coupon_generate = request.env['pos.coupon'].sudo().create({
                        'voucher_id': 174,
                        'discount_type': 'percent',
                        'discount_value': 10,
                        'min_order_value': 100,
                        'voucher_type': 'all',
                        'calc_by': 'order',
                        'start_date': datetime.now(),
                        'end_date': datetime.now() + timedelta(days=15)
                    })
                    code_dct = {
                        'generated_coupon': coupon_generate.name,
                        'expiry_date': coupon_generate.end_date,
                        'type': coupon_generate.discount_type,
                        'amount': coupon_generate.discount_value
                    }
                    response['customer_id'] = customer_id
                    response['Coupon'] = code_dct
                    response['message'] = "Customer subscribe Success"
                    response['code'] = 200
                    return response
        else:
            response['customer_id'] = False
            response['Coupon'] = False
            response['message'] = "Customer ID Is Invalid"
            response['code'] = 401
            #     customer = request.env['res.partner'].sudo().create({
            #         'name': data.get('customer_name'),
            #         'phone': data.get('phone'),
            #     }).id
            #     if customer:
            #         request.env['loyalty.subscriber'].sudo().create({
            #             'customer_id': customer.id,
            #             'code': code,
            #             'is_subscribed': is_valid
            #         })
            #         customer.code = code
            #         customer.barcode = code
            #         coupon_generate = request.env['pos.coupon'].sudo().create({
            #             'voucher_id': 174,
            #             'discount_type': 'percent',
            #             'discount_value': 10,
            #             'min_order_value': 100,
            #             'start_date': datetime.datetime.now(),
            #             'end_date': datetime.datetime.now() + datetime.timedelta(days=15)
            #         })
            #         code_dct = {
            #             'generated_coupon': coupon_generate.name,
            #             'expiry_date': coupon_generate.end_date,
            #             'type': coupon_generate.discount_type,
            #             'amount': coupon_generate.discount_value
            #         }

            return response

    @http.route('/api/v1/check_subscribtion', type='json', auth="none", csrf=False, methods=['GET'])
    def check_subscribe(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        customer_id = int(data.get('customer_id'))
        if customer_id:
            customer = request.env['loyalty.subscriber'].sudo().search([('customer_id', '=', customer_id)])
            request.env['ir.cron'].sudo().search([('cron_name', '=', 'check_point')]).method_direct_trigger()
            # customer_points_now = request.env['res.partner'].sudo().search([('id', '=', customer_id)]).total_points
            if customer:
                p = str(customer.points)
                user_dct = {
                    'customer_id': customer_id,
                    'code': customer.code,
                    'is_subscribed': customer.is_subscribed,
                    'points': customer.points,
                    # 'customer_points': customer_points
                }
                response['result'] = user_dct
                response['message'] = "Success"
                response['code'] = 200
            else:

                response['message'] = "Customer not subscribe"
                response['code'] = 200

            return response

    @http.route('/api/v1/coupon_generation', type='json', auth="none", csrf=False, methods=['POST'])
    def coupon_generate(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        amount_rate = request.env['ir.config_parameter'].sudo().get_param('healthy_loyalty_points.amount_rate')
        response = validate_data(str(token), api_token)
        if response:
            return response
        customer_id = int(data.get('customer_id'))
        points = int(data.get('points_redeemed'))
        if customer_id:
            customer = request.env['loyalty.subscriber'].sudo().search([('customer_id', '=', customer_id)])
            if customer.is_subscribed and customer.points >= points:
                coupon_generate = request.env['pos.coupon'].sudo().create({
                    'voucher_id': 173,
                    'discount_value': points / int(amount_rate),
                    'min_order_value': points / int(amount_rate),
                    'voucher_type': 'all',
                    'calc_by': 'order',
                    'start_date': datetime.now(),
                    'end_date': datetime.now() + timedelta(days=30)
                })

                loyal_points_redeemed = request.env['redeem.loyalty.points'].sudo().create({
                    'customer_id': customer_id,
                    'coupon': coupon_generate.name,
                    'expire_date': coupon_generate.end_date,
                    'total_points_redeemed': points,
                    'points_residual': customer.points - points
                })
                # customer_p = customer.points - points
                # customer.points = customer_p
                code_dct = {
                    'generated_coupon': coupon_generate.name,
                    'expiry_date': coupon_generate.end_date,
                    'coupon_amount': coupon_generate.discount_value
                }
                # customer.customer_id.total_points = loyal_points_redeemed.points_residual
                response['result'] = code_dct
                response['message'] = "Success"
                response['code'] = 200
            else:

                response['message'] = "Customer not subscribe or The Points Redeemed Doesn't Exist"
                response['code'] = 200

            return response
        else:
            response['message'] = "Missing Data"
            response['code'] = 401

            return response

    @http.route('/api/v1/add_customer', type='json', auth="public", csrf=False, methods=['POST'])
    def add_customer(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        name = data.get('name')
        phone = data.get('phone')
        street = data.get('street', False)
        street2 = data.get('street2', False)
        # if not phone or name:
        #     response['message'] = "PLease add Required data"
        #     response['code'] = 301
        #     return response
        check_customer = request.env['res.partner'].sudo().search([('phone', '=', phone)],
                                                                  limit=1)

        if check_customer.id:
            response['message'] = "Customer Already Exist"
            response['Customer_id'] = check_customer.id
            response['code'] = 301
            return response
        else:
            customer = request.env['res.partner'].sudo().create({
                'company_id': 1,
                'name': name,
                'phone': phone,
                'street': street,
                'street2': street2,
            })
            response['message'] = "Customer Created Success"
            response['Customer_id'] = customer.id
            response['code'] = 200

            return response

    @http.route('/api/v1/check_coupon', type='json', auth="public", csrf=False, methods=['GET'])
    def check_coupon(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if response:
            return response
        customer_id = data.get('customer_id')
        date = data.get('date')
        d = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        if not date:
            response['message'] = "PLease add Date"
            response['code'] = 301
            return response
        check_coupon = request.env['pos.coupon'].sudo().search(
            [('voucher_id', 'in', [173, 174])])
        coupons = []
        for c in check_coupon:
            coupon_line = request.env['pos.coupon.line'].sudo().search(
                [('coupon_id', '=', c.id), ('create_date', '>=', date)], limit=1)

            if coupon_line.id:
                coupon_dct = {
                    'coupon': c.name,
                    'amount': c.discount_value,
                    'expiry_date': c.end_date
                }
                coupons.append(coupon_dct)

        response['result'] = coupons
        response['datetime'] = d
        response['type datetime'] = type(d)
        response['message'] = "Success"
        response['code'] = 200
        return response

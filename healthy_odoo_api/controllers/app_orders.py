import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data, try_except_decorator, timer
import re
import calendar, time, functools, threading


class AppOrder(http.Controller):

    def live_config_data(self):
        return {
            'HealthyToken': 'k87d5883-8344-4623-u763-7n46449a'
        }

    # ============================================================================================= #
    # Start Create App Order
    # ============================================================================================= #

    @http.route('/api/v1/create_odoo_app_order', type='json', auth='public', methods=['POST'])
    def create_app_order(self, *kw, **args):
        response = {}
        config = self.live_config_data()
        data = http.request.jsonrequest
        # print('request_body ============>', data)
        current_user = request.env.user
        # print('current_user ============>', current_user)
        # validate_selection = {}
        # relational_fields = {'external_app_id': {'model': 'app.order'}}
        required_parameter = [
            'token', 'customer_name', 'phone', 'company_id', 'branch_id',
            'customer_id', 'order_date', 'external_app_id', 'lines'
        ]
        response = _validate_data(
            data=data, required_parameter=required_parameter)
        partner_id = self._get_or_create_customer(data)
        if not response.get('message', False):
            created_data = self._create_app_order(data)
            if not 'message' in created_data:
                response['order_id'] = created_data['id']
                response['customer_id'] = partner_id
                response['status'] = 200
                response['message'] = "Creation Success."
            else:
                response['status'] = 500
                response['message'] = created_data['message']
        pprint(response)
        return json.loads(json.dumps(response))

    def _create_app_order(self, data):
        response = {}
        found_id = request.env['app.order'].sudo().search(
            [('external_app_id', '=', data.get('external_app_id'))], limit=1)
        if not found_id:
            partner_id = self._get_or_create_customer(data)
            done = False
            app_order = request.env['app.order'].sudo().create({
                'partner_id': partner_id,
                'external_app_id': data.get('external_app_id'),
                'company_id': data.get('company_id'),
                'branch_id': data.get('branch_id'),
                'sales_person': data.get('sales_person'),
                'order_date': data.get('order_date'),
                'discount_type': data.get('discount_type'),
                'discount': data.get('discount'),
                'free_delivery': data.get('free_delivery'),
                'customer_suggestion': data.get('customer_suggestion'),
                'customer_notes': data.get('customer_notes'),
                'call_center_agent_name': data.get('call_center_agent_name'),
                'order_address': "{} {}".format(data.get('street', ''), data.get('street2', '')),
            })
            if 'due_date' in data and data.get('due_date'):
                schedule_due_date = datetime.strptime(
                    str(data.get('due_date')), '%Y-%m-%d %H:%M:%S')
                app_order.sudo().write(
                    {'due_date': schedule_due_date - timedelta(hours=2)})
                app_order.sudo().write(
                    {'schedule_time': str(schedule_due_date.hour)})
            if 'delivery_cost' in data and data.get('delivery_cost'):
                app_order.sudo().write(
                    {'delivery_cost': data.get('delivery_cost')})
            if 'order_source' in data and data.get('order_source'):
                source = request.env['pos.order.source'].sudo().search([('id', '=', int(data.get('order_source')))])
                if source.id:
                    app_order.sudo().write({'order_source_id': source.id})
                #else:
                #    o_source = request.env['pos.order.source'].sudo().create({'name': data.get('order_source')})
                #    app_order.sudo().write({'order_source_id': o_source.id})
            if 'order_platform' in data and data.get('order_platform'):
                app_order.sudo().write(
                    {'order_platform': data.get('order_platform')})
            if 'payment' in data and data.get('payment'):
                app_order.sudo().write(
                    {'is_paid': data.get('payment')})
            for line in data.get('lines'):
                required_parameter_lines = [
                    'product_id', 'qty', 'price'
                ]
                response = _validate_data(
                    data=line, required_parameter=required_parameter_lines)
                print('response line', response)
                if not response.get('message', False):
                    request.env['app.order.lines'].sudo().create({
                        'app_order_id': app_order.id,
                        'product_id': line.get('product_id'),
                        'qty': line.get('qty'),
                        'price': line.get('price'),
                        'discount': line.get('discount'),
                    })
                    done = True
                    response['id'] = app_order.id
                    response['done'] = done
                else:
                    response['message'] = response['message']
                    response['done'] = done
                    break
        else:
            response['id'] = found_id.id
            response['done'] = True
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
                partner.write({
                    'street': data.get('street', False),
                    'street2': data.get('street2', False)
                })
                partner_id = partner.id
            else:
                partner_id = request.env['res.partner'].sudo().create({
                    'name': data.get('customer_name'),
                    'customer_id': data.get('customer_id'),
                    'phone': data.get('phone'),
                    'street': data.get('street', False),
                    'street2': data.get('street2', False),
                }).id
        else:
            partner_id = request.env['res.partner'].sudo().create({
                'name': data.get('customer_name'),
                'customer_id': data.get('customer_id'),
                'phone': data.get('phone'),
                'street': data.get('street', False),
                'street2': data.get('street2', False),
            }).id
        return partner_id

    # def _validate_data(self, data, config, required_parameter=[]):
    #     response = {}
    #     required_parameter += [
    #         'token', 'customer_name', 'phone', 'company_id',
    #         'customer_id', 'order_date', 'external_app_id', 'lines'
    #     ]
    #     required_parameter_lines = [
    #         'product_id', 'qty', 'price'
    #     ]
    #     param_models = {'company_id': 'res.company'}
    #     if data.get('token') != config['HealthyToken']:
    #         print("data.get('token') == config['HealthyToken']", data.get(
    #             'token') == config['HealthyToken'])
    #         response['result'] = []
    #         response['message'] = 'Invalid token.'
    #         response['status'] = 301
    #     for param in required_parameter:
    #         if not param in data:
    #             response['message'] = '{} parameter is missing.'.format(param)
    #             response['status'] = 500
    #         if param in param_models:
    #             if data.get(param) and data.get(param) > 0:
    #                 print('param, model', param)
    #                 found_data = request.env[param_models.get(param)].sudo().search(
    #                     [('id', '=', data.get(param))], limit=1)
    #                 if not found_data:
    #                     response['result'] = []
    #                     response['message'] = "{} not found in database please insert correct id.".format(
    #                         param)
    #                     response['status'] = 404
    #     # for lines_param in required_parameter_lines:
    #     #     if not lines_param in data.get('lines', False):
    #     #         response['message'] = '{} parameter is missing.'.format(lines_param)
    #     #         response['status'] = 500
    #     return response

    # ============================================================================================= #
    # Start Update App Order
    # ============================================================================================= #
    # @try_except_decorator
    @timer
    @http.route('/api/v1/update_odoo_app_order', type='json', auth='public', methods=['POST'])
    def update_app_order(self, *kw, **args):
        response = {}
        # config = self.live_config_data()
        # config = self.dev_config_data()
        data = http.request.jsonrequest
        # print('request_body ============>', data)
        current_user = request.env.user
        # print('current_user ============>', current_user)
        relational_fields = {'odoo_id': {'model': 'app.order'}}
        required_parameter = [
            'token', 'customer_name', 'phone', 'company_id', 'branch_id',
            'customer_id', 'order_date', 'lines', 'odoo_id'
        ]
        response = _validate_data(data=data, required_parameter=required_parameter, relational_fields=relational_fields)
        # response = self._validate_data(
        #     data, config, required_parameter=['odoo_id'])
        partner_id = self._get_or_create_customer(data)
        if not response.get('message', False):
            updated_data = self._update_app_order(data)
            if updated_data['done']:
                response['status'] = 200
                response['order_id'] = updated_data['id']
                response['customer_id'] = partner_id
                response['message'] = updated_data['message']
            else:
                response['status'] = 200
                response['order_id'] = updated_data['id']
                response['customer_id'] = partner_id
                response['message'] = updated_data['message']
        pprint(response)
        return json.loads(json.dumps(response))

    @timer
    def _update_app_order(self, data):
        partner_id = self._get_or_create_customer(data)
        done = False
        response = {}
        app_order = request.env['app.order'].sudo().browse(data.get('odoo_id'))
        schedule_due_date = datetime.strptime(
            str(data.get('due_date', False)), '%Y-%m-%d %H:%M:%S')
        if app_order and app_order.state == 'draft' and not app_order.synced:
            app_order.sudo().write({
                'partner_id': partner_id,
                'company_id': data.get('company_id'),
                'branch_id': data.get('branch_id'),
                'sales_person': data.get('sales_person'),
                'order_date': data.get('order_date'),
                'discount_type': data.get('discount_type'),
                'discount': data.get('discount'),
                'due_date': schedule_due_date - timedelta(hours=2),
                'schedule_time': str(schedule_due_date.hour),
                'delivery_cost': data.get('delivery_cost'),
                'order_platform': data.get('order_platform'),
                'customer_suggestion': data.get('customer_suggestion'),
                'customer_notes': data.get('customer_notes'),
                'call_center_agent_name': data.get('call_center_agent_name'),
            })
            app_order.app_lines.sudo().unlink()
            for line in data.get('lines'):
                request.env['app.order.lines'].sudo().create({
                    'app_order_id': app_order.id,
                    'product_id': line.get('product_id'),
                    'qty': line.get('qty'),
                    'price': line.get('price'),
                    'discount': line.get('discount'),
                })
            done = True
            response['id'] = app_order.id
            response['done'] = done
            response['message'] = "Update Success."
        else:
            response['id'] = app_order.id
            response['done'] = done
            response[
                'message'] = "To update an app order it must be draft and not synced with pos which mean that order can not be updated."
        return response

    # ============================================================================================= #
    # Start Delete App Order
    # ============================================================================================= #

    @http.route('/api/v1/cancel_odoo_app_order', type='json', auth='public', methods=['POST'])
    def cancel_odoo_app_order(self, *kw, **args):
        response = {}
        config = self.live_config_data()
        data = http.request.jsonrequest
        # print('request_body ============>', data)
        if data.get('odoo_id') and data.get('cancel_reason'):
            app_order = request.env['app.order'].sudo().browse(
                data.get('odoo_id'))
            if app_order and app_order.state in ('draft', 'received'):
                app_order.write({
                    'state': 'cancel',
                    'cancel_reason': data.get('cancel_reason')
                })
                response['status'] = 200
                response['message'] = "Cancellation Success."
            else:
                response['status'] = 500
                response[
                    'message'] = "Sorry but you can not cancel app order which not in status ('draft', 'received')."
        else:
            response['status'] = 500
            response['message'] = "odoo_id required."
        pprint(response)
        return json.loads(json.dumps(response))

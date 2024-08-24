import odoo.http as http
from odoo.http import Controller, request, route
import json
from datetime import datetime, timedelta
from pprint import pprint
from .config import validate_data


class AppOrder(http.Controller):

    @http.route('/api/v1/create_odoo_app_order', type='json', auth='public', methods=['POST'])
    def create_app_order(self, *kw, **args):
        response = {}
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')

        data = http.request.jsonrequest
        required_parameter = [
            'healthy_tasty_token', 'customer_name', 'phone', 'company_id',
            'customer_id', 'order_date', 'external_app_id', 'lines'
        ]
        response = self._validate_data(token=api_token,
                                       data=data, required_parameter=required_parameter, )
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
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = {}
        found_id = request.env['app.order'].sudo().search(
            [('external_app_id', '=', data.get('external_app_id'))], limit=1)

        if not found_id:
            if data.get('lines'):
                partner_id = self._get_or_create_customer(data)
                done = False
                app_order = request.env['app.order'].sudo().create({
                    'partner_id': partner_id,
                    'external_app_id': data.get('external_app_id'),
                    'company_id': data.get('company_id'),
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
                # if 'order_source' in data and data.get('order_source'):
                #     app_order.sudo().write({'order_source': data.get('order_source')})
                if 'order_platform' in data and data.get('order_platform'):
                    app_order.sudo().write(
                        {'order_platform': data.get('order_platform')})
                for line in data.get('lines'):
                    required_parameter_lines = [
                        'product_id', 'qty', 'price'
                    ]
                    response = self._validate_data(
                        token=api_token, data=line, required_parameter=required_parameter_lines)
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
                response['message'] = "Add Lines"
                response['done'] = False

        else:
            response['id'] = found_id.id
            response['done'] = True
        return response

    def _get_or_create_customer(self, data):
        partner_id = False
        if data.get('customer_id') or data.get('phone'):
            partner = request.env['res.partner'].sudo().search(['|', ('id', '=', data.get(
                'customer_id')), ('phone', '=', data.get('phone'))], limit=1)
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

    @http.route('/api/v1/update_odoo_app_order', type='json', auth='public', methods=['POST'])
    def update_app_order(self, *kw, **args):
        response = {}
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')

        data = http.request.jsonrequest
        relational_fields = {'odoo_id': {'model': 'app.order'}}
        required_parameter = [
            'fleurelle_token', 'customer_name', 'phone', 'company_id',
            'customer_id', 'order_date', 'lines', 'odoo_id'
        ]
        response = self._validate_data(token=api_token, data=data, required_parameter=required_parameter,
                                       relational_fields=relational_fields)
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
                'sales_person': data.get('sales_person'),
                'order_date': data.get('order_date'),
                'discount_type': data.get('discount_type'),
                'discount': data.get('discount'),
                'due_date': schedule_due_date - timedelta(hours=2),
                'schedule_time': str(schedule_due_date.hour),
                'delivery_cost': data.get('delivery_cost'),
                # 'order_platform': data.get('order_platform'),
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

    @http.route('/api/v1/cancel_odoo_app_order', type='json', auth='public', methods=['POST'])
    def cancel_odoo_app_order(self, *kw, **args):
        response = {}
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
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

    def _validate_data(self, token, data, relational_fields={}, required_parameter=[], validate_selection={}):
        response = {}
        required = self._required_parameters(data, token, required_parameter)
        if 'message' in required:
            response['message'] = required['message']
            response['status'] = required['status']
        relational = self._relational_fields(data, relational_fields)
        if 'message' in relational:
            response['message'] = relational['message']
            response['status'] = relational['status']
        selections = self._validate_selection_options(data, validate_selection)
        if 'message' in selections:
            response['message'] = selections['message']
            response['status'] = 422
        return response

    def _required_parameters(self, data, Token, required_parameter):
        response = {}
        if required_parameter:
            for param in required_parameter:
                if not param in data:
                    response['message'] = '{} parameter is missing.'.format(param)
                    response['status'] = 404
                if param == 'limit' and not isinstance(data.get('limit'), int):
                    response['message'] = '{} parameter must be integer.'.format(
                        param)
                    response['status'] = 200
                if param == 'healthy_tasty_token' and data.get('healthy_tasty_token') != Token:
                    response['result'] = []
                    response['message'] = 'Invalid token.'
                    response['status'] = 301
        return response

    def _relational_fields(self, data, relational_fields):
        response = {}
        if relational_fields:
            for field, model in relational_fields.items():
                # print('data.get(field)', data.get(field))
                if field in data and data.get(field):
                    if not isinstance(model, dict):
                        found_data = request.env[model].search(
                            [('id', '=', data.get(field))], limit=1)
                    else:
                        if 'domian' in model and model.get('domian'):
                            found_data = request.env[model.get('model')].search(
                                [('id', '=', data.get(field))] + model.get('domian'), limit=1)
                        else:
                            found_data = request.env[model.get('model')].search(
                                [('id', '=', data.get(field))], limit=1)
                    if not found_data:
                        response['result'] = []
                        response['message'] = "{} value ({}) not found in database please insert correct id.".format(
                            field, data.get(field))
                        response['status'] = 404
                else:
                    response['message'] = "{} parameter is missing or doesn't has a value.".format(
                        field)
                    response['status'] = 404

        print('_relational_fields', response)
        return response

    def _validate_selection_options(self, data, validate_selection):
        response = {}
        if validate_selection:
            for key, value in validate_selection.items():
                if key in data and data.get(key) not in value:
                    response[
                        'message'] = "wrong value for parameter ({}) you should use one of these values {}.".format(
                        key, value)
        return response

    @http.route('/api/v1/orders/list', type='json', auth="none", methods=['GET'])
    def list(self, **args):
        data = http.request.jsonrequest
        token = data.get('healthy_tasty_token')
        partner_id = data.get('partner_id', None)
        from_date = data.get('from_date', None)
        to_date = data.get('to_date', None)
        limit = data.get('limit', None)
        offset = data.get('start', 0)
        order_by = data.get('order_by', None)
        orde_ids = data.get('categ_ids')
        api_token = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.api_token')
        response = validate_data(str(token), api_token)
        if response:
            return response
        else:
            fields = self.get_fields()
            fields_lines = self.get_lines_fields()
            domain = []
            if orde_ids:
                domain.append(('id', 'in', orde_ids))
            if partner_id:
                domain.append(('partner_id', '=', partner_id))
            if from_date:
                domain.append(('order_date', '>=', str(from_date)))
            if to_date:
                domain.append(('order_date', '<=', str(to_date)))

            orders = request.env['app.order'].sudo().search(domain, limit=int(limit),
                                                            offset=int(offset), order=order_by)

            vals = []
            for order in orders:
                lines = []
                val = {}
                for field in fields:
                    if '.display_name' in field:
                        field = field.split('.')[0]
                        val.update({
                            field.replace('.', '_') + '_name': getattr(order, field).display_name
                        })
                    elif '.id' in field:
                        field = field.split('.')[0]
                        val.update({
                            field: getattr(order, field).id
                        })

                    else:
                        val.update({
                            field: getattr(order, field)
                        })
                for line in order.app_lines:
                    val2 = {}
                    for field in fields_lines:
                        if '.display_name' in field:
                            field = field.split('.')[0]
                            val2.update({
                                field.replace('.', '_') + '_name': getattr(line, field).display_name
                            })
                        elif '.id' in field:
                            field = field.split('.')[0]
                            val2.update({
                                field: getattr(line, field).id
                            })

                        else:
                            val2.update({
                                field: getattr(line, field)
                            })
                    lines.append(val2)
                    val.update({
                        'lines': lines
                    })

                vals.append(val)

            return {'result': vals}

    def get_fields(self):
        order_fields = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.order_fields')
        fields = ['id']
        try:
            fields = eval(order_fields)
        except:
            pass
        return fields

    def get_lines_fields(self):
        order_fields = request.env['ir.config_parameter'].sudo().get_param('healthy_tasty_api.order_line_fields')
        fields = ['id']
        try:
            fields = eval(order_fields)
        except:
            pass
        return fields

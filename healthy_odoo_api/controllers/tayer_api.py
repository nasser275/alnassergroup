import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from .settings import _validate_data
from dateutil.relativedelta import relativedelta
from datetime import datetime


class Tayer(http.Controller):

    @http.route('/api/v1/get_available_delivery', type='json', auth='public', methods=['GET'])
    def get_available_delivery(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            model_data = request.env['pos.order'].sudo().search([('is_delivery','=',True)],limit=100, order='id desc')
            print(model_data)
            final_data_list = []
            for record in model_data:
                print(record.send_to_tayar)
                print('date', record.date_order.date())
                print('date now', datetime.now().date())
                if record.date_order.date() == datetime.now().date():
                    if record.send_to_tayar is False and record.is_delivery is True and not record.not_send_reason:
                        data = {
                            'odoo_id': record.branch_id.id,
                            'order': {
                                'id': record.id,
                                'delivered_date': str(record.date_order.date()),
                                'delivery_time_name': '10:23',
                                'price_after_discount': record.amount_total,
                                'note': ''
                            },
                            'customer': {
                                'id': record.partner_id.id,
                                'name': record.partner_id.name,
                                'mobile': record.partner_id.phone
                            },
                            'address': {
                                'address': self.get_address(record.partner_id),
                                'note': "",
                                'building_number': '',
                                'flat_number': '',
                                'hallmark': '',
                                'lat': '',
                                'lng': ''
                            },
                            'product_details': [
                                {
                                    'product_id': line.product_id.id,
                                    'product_name_ar': line.product_id.name,
                                    'product_price': line.price_unit,
                                    'quantity': line.qty,
                                    'product_tax': ''
                                } for line in record.lines],
                        }
                        print(data)
                        final_data_list.append(data)
            print(final_data_list)
            response['results'] = final_data_list
        return json.loads(json.dumps(response))

    def get_address(self, object):
        if object.street and object.street2:
            address = "{} {}".format(object.street, object.street2)
        elif object.street and not object.street2:
            address = object.street
        elif not object.street and object.street2:
            address = object.street2
        else:
            address = None
        return address

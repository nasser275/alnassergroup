import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from .settings import _validate_data
from dateutil.relativedelta import relativedelta


class TayerStatus(http.Controller):

    @http.route('/api/v1/get_status_delivery', type='json', auth='public', methods=['POST'])
    def cancel_odoo_app_order(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        if not response.get('message', False):
            print('request_body ============>', data)
            if data.get('order_id'):
                order = request.env['pos.order'].sudo().browse(
                    data.get('order_id'))
                if order:
                    order.write({
                        'send_to_tayar': data.get('deliverd'),
                        'not_send_reason': data.get('reason')
                    })
                    response['status'] = 200
                    response['message'] = "Status Updated."
                else:
                    response['status'] = 500
                    response[
                        'message'] = "Sorry but you can not Find order"
            else:
                response['status'] = 500
                response['message'] = "order_id required."
            return json.loads(json.dumps(response))

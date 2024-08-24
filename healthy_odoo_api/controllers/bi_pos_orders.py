import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data
from  dateutil.relativedelta import relativedelta


class POSOrders(http.Controller):

    @http.route('/api/v1/bi_get_pos_orders', type='json', auth='public', methods=['POST'])
    def bi_get_pos_orders(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token', 'limit', 'id', 'delivered_time', 'cancel_time']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        model_data = []
        if not response.get('message', False):
            domian = self.search_domian(data)
            if domian:
                model_data = request.env['pos.order'].sudo().search(domian, limit=data.get('limit'), order='id')
            final_data_list = []
            if model_data:
                for record in model_data:
                    final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(model_data))
        return json.loads(json.dumps(response)) 

    def search_domian(self, data):
        domain = []
        if data.get('id', False):
            domain += [('id', '>=', data.get('id'))]
        if data.get('status', False) in ( 'paid', 'done', 'cancel', 'invoiced'):
            domain += [('state', '=', data.get('status'))]
        if data.get('delivered_time', None) and data.get('delivered_time', None) != None:
            delivered_time = datetime.strptime(data.get('delivered_time'), '%Y-%m-%d %H:%M:%S')
            print("delivered_time , data.get('delivered_time'), datetime.now()", delivered_time, data.get('delivered_time'), datetime.now())
            if delivered_time > datetime.now() - timedelta(hours=1):
                domain += [('delivered_time', '>=', data.get('delivered_time'))]
            else:
                domain = []
        elif data.get('cancel_time', False) and data.get('cancel_time', None) != None:
            cancel_time = datetime.strptime(data.get('delivered_time'), '%Y-%m-%d %H:%M:%S')
            print("cancel_time , data.get('cancel_time'), datetime.now()",cancel_time , data.get('cancel_time'), datetime.now())
            if cancel_time > datetime.now() - timedelta(hours=1):
                domain += [('cancel_time', '>=', data.get('cancel_time'))]
            else:
                domain = []
        else:
            domain += []
        print('domain', domain)
        return domain

    def get_address(self, object):
        if object.street and object.street2:
            address = "{} {}".format(object.street , object.street2)
        elif object.street and not object.street2:
            address = object.street
        elif not object.street and object.street2:
            address = object.street2
        else:
            address = None
        return address


    def get_data(self, record):
        return {
            "order_id": record.id,
            "order_ref": record.name,
            "receipt_ref": record.pos_reference,
            "customer_id": record.partner_id.id,
            "customer_name": record.partner_id.name,
            "customer_phone": record.partner_id.phone,
            "customer_complete_address": self.get_address(record.partner_id),
            "customer_created_on": "{}".format(record.partner_id.create_date+relativedelta(hours=2)) if record.partner_id else False ,
            "company_id": record.branch_id.id,
            "company_display_name": record.branch_id.name,
            "order_date": "{}".format(record.date_order+relativedelta(hours=2)),
            "total": record.amount_total,
            "order_channel":  record.order_platform,
            "order_status": record.state,
            "return_status": record.return_status,
            "return_order": record.return_order_id.name,
            "salesperson_id": record.user_id.id,
            "salesperson_display_name": record.user_id.display_name,
            "delivery_person_id": record.delivery_person_id.id,
            "delivery_person_display_name": record.delivery_person_id.display_name,
            "free_delivery": record.free_delivery,
            "sales_represtiative_id": record.employee_id.id,
            "sales_represtiative_name": record.employee_id.name,

        }

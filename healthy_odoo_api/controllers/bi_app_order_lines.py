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


class APPOrdersLines(http.Controller):




    @http.route('/api/v1/bi_get_app_order_lines', type='json', auth='public', methods=['POST'])
    def bi_get_app_order_lines(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token','limit', 'id']
        data = http.request.jsonrequest
        AppOrderLine = request.env['app.order.lines'].sudo()
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        model_data = []
        if not response.get('message', False):
            domian = self.search_domian(data)
            if domian:
                model_data = AppOrderLine.search(domian, limit=data.get('limit'), order='id')
            final_data_list = []
            if model_data:
                for record in model_data:
                    final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(final_data_list))
            pprint(final_data_list)
        return json.loads(json.dumps(response)) 

    def search_domian(self, data):
        return [('id', '>=', data.get('id'))]


    def get_data(self, record):
        return {
            "app_order_line_id": record.id or None,
            "app_order_id": record.app_order_id.id or None,
            "customer_id": record.app_order_id.partner_id.id or None,
            "customer_name": record.app_order_id.partner_id.name or None,
            "company_id": record.app_order_id.company_id.id or None,
            "company_display_name": record.app_order_id.company_id.display_name or None,
            "order_date": "{}".format(record.app_order_id.order_date+relativedelta(hours=2) or None),
            "pos_created_time": "{}".format(record.app_order_id.pos_created_time or None),
            "order_status": record.app_order_id.state or None,
            "created_on": "{}".format(record.app_order_id.create_date+relativedelta(hours=2) or None),
            "total": record.app_order_id.amount_total or None,
            "order_source": record.app_order_id.order_platform or None,
            "cancel_reason": record.app_order_id.cancel_reason or None,
            "order_lines_product_id": record.product_id.id or None,
            "order_lines_product_name": record.product_id.name or None,
            "order_lines_quantity": record.qty or None,
            "order_lines_unit_price": record.price or None,
            "salesperson_id": record.app_order_id.sales_person.id or None,
            "salesperson_display_name": record.app_order_id.sales_person.display_name or None,
            "call_center_agent_name": record.app_order_id.call_center_agent_name or None if record.app_order_id else None,
            "app_order_name": record.app_order_id.name  or None if record.app_order_id else None,
            "schedule_start_date": "{}".format(record.app_order_id.schedule_start_date or None),
            "schedule_end_date": "{}".format(record.app_order_id.schedule_end_date or None),
            "schedule_time": record.app_order_id.schedule_time or None,
            "is_schedule": record.app_order_id.is_schedule,
        }

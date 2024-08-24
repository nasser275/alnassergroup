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


class Purchasing(http.Controller):

    @http.route('/api/v1/bi_get_purchasing', type='json', auth='public', methods=['POST'])
    def bi_get_purchasing(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token', 'limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        model_data = []
        if not response.get('message', False):
            domian = self.search_domian(data)
            if domian:
                model_data = request.env['purchase.order.line'].sudo().search(domian, limit=data.get('limit'), order='id')
            final_data_list = []
            if model_data:
                for record in model_data:
                    final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(model_data))
            pprint(final_data_list)
        return json.loads(json.dumps(response)) 

    def search_domian(self, data):
        return [('id', '>=', data.get('id'))]

    def get_data(self, record):
        return {
            "po_line_id": record.id,
            "po_id": record.order_id.id,
            "order_reference": record.order_id.name,
            "order_date": "{}".format(record.order_id.date_order+relativedelta(hours=2)),
            "effective_date": "{}".format(record.order_id.effective_date+relativedelta(hours=2) if record.order_id.effective_date else False),
            "status": record.order_id.state,
            "company_id": record.order_id.branch_id.id,
            "company_display_name": record.order_id.branch_id.name,
            "vendor_id": record.order_id.partner_id.id,
            "vendor_name": record.order_id.partner_id.name,
            "order_lines_product_id": record.product_id.id,
            "order_lines_display_name": record.product_id.display_name,
            "order_lines_quantity": record.product_qty,
            "order_lines_received_qty": record.qty_received,
            "order_lines_unit_cost": record.product_id.standard_price,
            "order_lines_unit_price": record.price_unit,
            "order_lines_tax": record.taxes_id[0].name if record.taxes_id else None,
        }

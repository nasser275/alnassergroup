import odoo.http as http
from odoo.http import Controller, request, route
from odoo.exceptions import UserError, ValidationError
import json
from datetime import datetime, timedelta
from pprint import pprint
import requests
import os
from .settings import _validate_data


class Returns(http.Controller):

    @http.route('/api/v1/bi_get_returns', type='json', auth='public', methods=['POST'])
    def bi_get_returns(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token', 'limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        model_data = []
        if not response.get('message', False):
            parent_model_ids = request.env['account.move'].sudo().search(
                [('state', 'in', ('open', 'paid')), ('type', '=', 'in_refund')], order='id').ids
            domian = self.search_domian(data, parent_model_ids)
            if domian:
                model_data = request.env['account.move.line'].sudo().search(domian, limit=data.get('limit'), order='id')
            final_data_list = []
            if model_data:
                for record in model_data:
                    final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(model_data))
            pprint(final_data_list)
        return json.loads(json.dumps(response))

    def search_domian(self, data, parent_model_ids):
        return [('id', '>=', data.get('id')), ('move_id', 'in', parent_model_ids)]

    def get_data(self, record):
        return {
            "return_line_id": record.id,
            "return_id": record.move_id.id,
            "order_reference": record.move_id.name,
            "invoice_date": "{}".format(record.move_id.date_invoice),
            "status": record.move_id.state,
            "company_id": record.move_id.company_id.id,
            "company_display_name": record.move_id.company_id.display_name,
            "vendor_id": record.move_id.partner_id.id,
            "vendor_name": record.move_id.partner_id.name,
            "order_lines_product_id": record.product_id.id,
            "order_lines_display_name": record.product_id.display_name,
            "order_lines_quantity": record.quantity,
            "order_lines_unit_cost": record.product_id.standard_price,
            "order_lines_unit_price": record.price_unit,
            "order_lines_tax": record.invoice_line_tax_ids[0].name if record.invoice_line_tax_ids else None,
            "refund_type": record.move_id.refund_type if record.move_id.refund_type else None
        }

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



class POSOrdersLine(http.Controller):

    @http.route('/api/v1/bi_get_pos_order_lines', type='json', auth='public', methods=['POST'])
    def bi_get_pos_order_lines(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token','limit', 'id']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        model_data = []
        if not response.get('message', False):
            domian = self.search_domian(data)
            if domian:
                model_data = request.env['pos.order.line'].sudo().search(domian, limit=data.get('limit'), order='id')
            final_data_list = []
            if model_data:
                for record in model_data:
                    final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            print("records count -> ", len(final_data_list))
            pprint(final_data_list)
        return json.loads(json.dumps(response)) 

    def search_domian(self, data):
        return [('id', '>=', data.get('id')),('order_id.state', 'in', [ 'paid', 'done', 'cancel', 'invoiced'])]

    def search_domian2(self, data):
        domain=[]
        if data.get('id'):
            domain.append(('id', '>=', data.get('id')))
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
            "order_line_id": record.id,
            "order_id": record.order_id.id,
            "order_ref": record.order_id.name,
            "receipt_ref": record.order_id.pos_reference,
            "customer_id": record.order_id.partner_id.id or None,
            "customer_name": record.order_id.partner_id.name or None,
            "customer_phone": record.order_id.partner_id.phone or None,
            "customer_complete_address": self.get_address(record.order_id.partner_id),
            "customer_created_on": "{}".format(record.order_id.partner_id.create_date+relativedelta(hours=2)) if record.order_id.partner_id.create_date else None,
            "company_id": record.order_id.branch_id.id,
            "company_display_name": record.order_id.branch_id.name,
            "order_date": "{}".format(record.order_id.date_order+relativedelta(hours=2)),
            "order_status": record.order_id.state,
            "supplier_id": record.product_id.supplier_id.id if record.product_id.supplier_id else None,
            "supplier_name": record.product_id.supplier_id.name if record.product_id.supplier_id else None,
            "product_category_id": record.product_id.categ_id.id if record.product_id.categ_id else None,
            "product_category_name": record.product_id.categ_id.name if record.product_id.categ_id else None,
            "total": record.order_id.amount_total,
            "order_channel": record.order_id.order_platform,
            "return_status": record.order_id.return_status or None,
            "return_order": record.order_id.return_order_id.name or None,
            "salesperson_id": record.order_id.user_id.id or None,
            "salesperson_display_name": record.order_id.user_id.display_name or None,
            "delivery_person_id": record.order_id.delivery_person_id.id or None,
            "delivery_person_display_name": record.order_id.delivery_person_id.display_name or None,
            "created_on": "{}".format(record.order_id.create_date+relativedelta(hours=2)),
            "order_lines_product_id": record.product_id.id,
            "order_lines_product_name": record.product_id.name,
            "order_lines_product_display_name": record.product_id.display_name,
            "order_lines_product_product_category": record.product_id.categ_id.display_name,
            "order_lines_quantity": record.qty,
            "order_lines_product_cost": record.product_id.standard_price,
            "order_lines_unit_price": record.price_unit,
            "call_center_agent_name": record.order_id.app_order_id.call_center_agent_name if record.order_id.app_order_id else None,
            "delivery_time": "{}".format(record.order_id.delivered_time) or None,
            "delivery_amount": record.order_id.delivery_amount or None,
            "app_order_id": record.order_id.app_order_id.id if record.order_id.app_order_id else None,
            "app_order_name": record.order_id.app_order_id.name if record.order_id.app_order_id else None,
            "app_order_status": record.order_id.app_order_id.state or None if record.order_id.app_order_id else None,
            "is_schedule": record.order_id.app_order_id.is_schedule if record.order_id.app_order_id else None,
            "discount_percentage": record.discount,
            "discount": (record.discount/100)*(record.price_unit*record.qty),
            "last_purchase_price": record.last_purchase_price,
            "offer_name": record.order_id.offer_name.name,
            "free_delivery": record.order_id.free_delivery,
            "is_gift": record.is_gift,
            "return_reason": record.order_id.return_reason,
            "pos_coupon": record.order_id.coupon_id.name,
            "is_combo": record.is_combo,
            "is_promotion": record.is_promotion,
            "promotion_cost": record.promotion_cost,
            "combo_name": record.combo_name,
            "combo_price": record.combo_price,
            "combo_cost": record.combo_cost,
            "combo_line_cost": record.combo_line_cost,
            "combo_line_price": record.combo_line_price,
            "main_combo": record.main_combo,
            "cancel_reason": record.order_id.cancel_reason,
            "cancel_time": "{}".format(record.order_id.cancel_time + relativedelta(hours=2)) if record.order_id.cancel_time else None,
            "payment_method": record.order_id.statement_ids[0].journal_id.name if record.order_id.statement_ids  else "" ,
            "sub_total":record.price_subtotal_incl,
            "sales_represtiative_id": record.order_id.employee_id.id,
            "sales_represtiative_name": record.order_id.employee_id.name,

        }


    def get_order_ids(self,date):
        query="""
        select pos_order.id from pos_order_line
        join pos_order on pos_order.id=pos_order_line.order_id
        where date(pos_order.date_order)=\'{date}\'
         and pos_order.state in ( 'paid', 'done', 'cancel', 'invoiced')
        """.format(date=date)
        request.env.cr.execute(query)
        lines = request.env.cr.dictfetchall()

        return [line.get('id') for line in lines]

    @http.route('/api/v1/bi_get_pos_order_lines_by_date', type='json', auth='public', methods=['POST'])
    def bi_get_pos_order_lines_by_date(self, *kw, **args):
        response = {}
        relational_fields = {}
        required_parameter = ['token', 'date']
        data = http.request.jsonrequest
        response = _validate_data(data=data, relational_fields=relational_fields, required_parameter=required_parameter)
        model_data = []
        if not response.get('message', False):
            domian = self.search_domian2(data)
            order_ids = self.get_order_ids(data.get('date'))
            domian.append(('order_id','in',order_ids))
            if domian:
                if data.get('limit'):

                    model_data = request.env['pos.order.line'].sudo().search(domian, limit=data.get('limit'),order='id')
                else:
                    model_data = request.env['pos.order.line'].sudo().search(domian, order='id')
            final_data_list = []
            if model_data:
                for record in model_data:
                    final_data_list.append(self.get_data(record))
            response['results'] = final_data_list
            pprint(final_data_list)
        return json.loads(json.dumps(response))



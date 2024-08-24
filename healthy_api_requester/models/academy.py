import json
import logging

import requests

from odoo import models, api
from .settings import chec_ip_is_live
from  dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HttpCustomers(models.Model):
    _inherit = 'res.partner'
    academy_customer_url = "http://academy.e3melbusiness.com/healthyandtastydemo/webservice/new_contact.php"

    @api.model
    def create(self, vals):
        res = super(HttpCustomers, self).create(vals)
        if res and chec_ip_is_live():
            data = self.mapping_create_data_academy(res)
            if data and data.get('customer_odoo_id'):
                try:
                    json_data = json.dumps(data)
                    response = requests.post(self.academy_customer_url, json_data)
                    print('data', json_data)
                    print("Response: %s , status: %s" % (response.text, response.status_code))
                    _logger.info("Response: %s , status: %s" % (response.text, response.status_code))
                except Exception as e:
                    print(e)
        return res

    def mapping_create_data_academy(self, res):
        if not res:
            return {}
        data = {
            "name": res.name,
            "email": res.email,
            "customer_odoo_id": res.id,
            "branch_odoo_id": res.branch_id,
            "mobile": res.phone,
            "register_date": str(res.create_date),
            "date_of_birth": "",
            "address": self.get_academy_address(res),
            "description": ""
        }
        return data

    def get_academy_address(self, object):
        if object.street and object.street2:
            address = "{} {}".format(object.street, object.street2)
        elif object.street and not object.street2:
            address = object.street
        elif not object.street and object.street2:
            address = object.street2
        else:
            address = None
        return address

#
# class HttpPosOrder(models.Model):
#     _inherit = 'pos.order'
#     update_academy_customer_url = "http://academy.e3melbusiness.com/healthyandtastydemo/webservice/update_contact.php"
#
#     # @api.model
#     def write(self, vals):
#         res = super(HttpPosOrder, self).write(vals)
#         if res and 'state' in vals.keys()  and chec_ip_is_live():
#             for order in self:
#                 if order.state not in ['draft', 'cancel']:
#                     data = order.mapping_update_data_academy()
#                     print(">>>C>C>C>>",data)
#                     if data and data.get('customer_odoo_id'):
#                         try:
#                             response = requests.put(self.update_academy_customer_url, json.dumps(data))
#                             print("Response: %s , status: %s" % (response.text, response.status_code))
#                         except Exception as e:
#                             print(e)
#         return res
#
#     def mapping_update_data_academy(self):
#         if not self:
#             return {}
#         data = {
#             "last_order_date": str(self.date_order),
#             "last_order_date": "{}".format(self.date_order + relativedelta(hours=2)) if self.date_order else None,
#             "total_amount": self.amount_total,
#             "customer_odoo_id": self.partner_id.id,
#             "last_branch_id": self.branch_id.id,
#             "mobile": self.partner_id.phone,
#             "total_orders": self.partner_id.pos_order_count,
#             # "last_order_channel": str(self.order_platform),
#             "number_of_pieces": len(self.lines)
#
#         }
#         return data

"""
Description: This module acts as http reuqester and listner on ERP customers and product actions
"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import requests, json

_logger = logging.getLogger(__name__)
from .settings import get_domain_for_host_by_ip_address, LIVE_DOMAIN, TEST_DOMAIN


# class HttpCustomers(models.Model):
#     _inherit = 'res.partner'
#     """ This url which we will send data to it from odoo """
#     crm_customer_url = "http://academy.e3melbusiness.com/healthyCrm/web_crm/new_contact.php"
#     """Listens to creation method and sends http request"""
#
#     @api.model
#     def create(self, vals):
#         res = super(HttpCustomers, self).create(vals)
#         if res:
#             data = self.mapping_create_data(res)
#             if data and data.get('odoo_id'):
#                 try:
#                     json_data = json.dumps(data)
#                     response = requests.post(self.crm_customer_url, json_data)
#                     print('data', json_data)
#                     print("Response: %s , status: %s" % (response.text, response.status_code))
#                     _logger.info("Response: %s , status: %s" % (response.text, response.status_code))
#                 except Exception as e:
#                     print(e)
#         return res
#
#     """Listens to write method and sends http request"""
#
#     # @api.model
#     def write(self, vals):
#         res = super(HttpCustomers, self).write(vals)
#         if res:
#             data = self.mapping_create_data(res)
#             if data and data.get('odoo_id'):
#                 try:
#                     json_data = json.dumps(data)
#                     response = requests.post(self.crm_customer_url, json_data)
#                     # print('data', json_data)
#                     # print("Response: %s , status: %s" % (response.text, response.status_code))
#                     _logger.info("Response: %s , status: %s" % (response.text, response.status_code))
#                 except Exception as e:
#                     print(e)
#         return res
#
#     """Returns an object of the changed data for the product"""
#     # def mapping_update_data(self, vals):
#     # 	if not self:
#     # 		return {}
#     # 	data = {}
#     # 	payload = {
#     # 		"name": ["name", self.name],
#     # 		"mobile": ["mobile", self.mobile],
#     # 		"email": ["email", self.email],
#     # 		"phone": ["phone", self.phone],
#     # 		"register_date": ["create_date", self.create_date],
#     # 		"street": ["street", self.street],
#     # 		"last_order_date": ["last_order_date", self.last_order_date],
#     # 		"pos_order_count": ["pos_order_count", self.pos_order_count],
#     # 		"company_name": ["company_id", self.company_id.name],
#     # 		"how_know_us": ["how_know_us", self.how_know_us],
#     # 	}
#     # 	for line in payload:
#     # 		if payload[line][0] in vals and payload[line][1]:
#     # 			data[line] = payload[line][1]
#     # 	if data:
#     # 		data['odoo_id'] = self.id
#     # 	return data
#
#     """Returns an object of the needed data for the product"""
#
#     def mapping_create_data(self, res):
#         if not res:
#             return {}
#         data = {
#             "name": self.name,
#             "mobile": self.mobile,
#             "email": self.email,
#             "test": 'test' if get_domain_for_host_by_ip_address != LIVE_DOMAIN else '',
#             "odoo_id": self.id,
#             "phone": self.phone,
#             "register_date": str(self.create_date),
#             "street": self.street,
#             # "last_order_date": self.last_order_date if self.last_order_date else '',
#             # "pos_order_count": self.pos_order_count if self.pos_order_count else '',
#             "branch_name": self.branch_id.name,
#             # "how_know_us": self.how_know_us if self.how_know_us else '',
#         }
#         return data

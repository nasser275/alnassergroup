from odoo import fields, models, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import requests
from datetime import timezone
from datetime import datetime, timedelta, date
import calendar
from .settings import get_domain_for_host_by_ip_address,LIVE_DOMAIN,TEST_DOMAIN

class HttpAppOrder(models.Model):
	_inherit = 'app.order'
	""" This url which we will send data to it from odoo """
	url_send_sms = '{}/odooApi/v1/sendSms'.format(get_domain_for_host_by_ip_address())
	update_status_url = "{}/api/v1/update_order_status".format(get_domain_for_host_by_ip_address())
	url_verify_user = '{}/api/v1/verify_user'.format(get_domain_for_host_by_ip_address())

	"""Listens to creation method and sends http request"""
	def _send_user_verify_on_state_payment_and_delivery(self,order):
		data = {
			'odoo_id': order.partner_id.id,
			'phone': order.partner_id.phone,
			'token': 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg'
		}
		# print('data verfiy user ===============================>', data)
		if self.url_verify_user:
			try:
				response = requests.post(self.url_verify_user,data)
				print("Response: %s , status: %s" % (response.text,response.status_code))
			except Exception as e:
				print(e)
		return True


	def send_sms_message(self):
		try:
			domain = [
				('created_from_schedule', '=', False),('order_date', '=', fields.Date.today()),
				('deleted', '=', False), ('schedule_time', '!=', False),
				('schedule_time', '!=', '0'), ('state', 'in', ['draft', 'received']),
				('pos_created_time', '=', False)
			]
			app_orders = self.env['app.order'].search(domain)
			# print('search late app_orders =============================>', len(app_orders))
			late_orders = []
			if len(app_orders) >= 1:
				for order in app_orders:
					if order.due_date:
						check_due_plus_15_minute = order.due_date + timedelta(minutes=15)
						if fields.Datetime.now() > check_due_plus_15_minute:
							late_orders.append(order)
			# print('search late_orders after adding 15 min =============================>', len(late_orders))
			company_ids = set([x.company_id for x in late_orders])
			if len(late_orders) >= 1:
				for company_id in company_ids:
					order_count = [order.id for order in late_orders if order.company_id.id == company_id.id]
					datetime_list = [order.due_date for order in late_orders if order.company_id.id == company_id.id]
					print(datetime_list, min(datetime_list))
					if order_count:
						if company_id.manager_id and company_id.manager_phone:
							self.send_sms_helper(company_id,company_id.manager_id,company_id.manager_phone,order_count,min(datetime_list))
						if company_id.area_manager_id and company_id.area_manager_phone:
							self.send_sms_helper(company_id,company_id.area_manager_id,company_id.area_manager_phone,order_count,min(datetime_list))
						if company_id.retail_manager_id and company_id.retail_manager_phone:
							self.send_sms_helper(company_id,company_id.retail_manager_id,company_id.retail_manager_phone,order_count,min(datetime_list))
		except Exception as e:
			print(e)

	def send_sms_helper(self, company_id,manager_id,manager_phone,order_count,min_order_date):
		try:
			# fmt = '%Y-%m-%d %H:%M:%S'
			fmt = '%Y-%m-%d %H:%M'
			current_time = datetime.now() + timedelta(hours=2)
			if manager_id and manager_phone:
				message = "السيد {} يرجي الانتباه هناك عدد ({}) اوردر متاخر في تمام الساعه {} خاصه بفرع ({}) من فضلك اتخذ اجراء.".format(
					manager_id.name,
					len(order_count),
					min_order_date.strftime(fmt),
					company_id.name
				)
				print(message)
				data = {
					'message': message,
					'mobile': manager_phone,
					'token': 'PPJUfNaPjArU85LWa8gXL44Y9R6veUEUTPudxYMUZEXHpVkaSpxuXEv5RnXAXYk4DkT6YFhbDh9MVhTqYGVv26r6KqDcKueWJ3ftG2GdRQ24uGByQZDDnXwHsMsEWveh'
				}
				response = requests.post(self.url_send_sms, data)
				print("Response: %s , status: %s" % (response.text, response.status_code))
				return True
			return False
		except Exception as e:
			print(e)

	def write(self, vals):
		# print("=========================>", self.state)
		res = super(HttpAppOrder, self).write(vals)
		if 'state' in vals:
			data = {
				'odoo_id': self.id,
				'cancel_reason': False,
				'status': vals.get('state'),
				'token': 'ay5t9Xh4hmAXSUEBby9j9dSAxjNCtnrFKp6x9YqG43JaXbpHESvHsP9G4vCg',
			}
			if vals.get('state') == 'cancel':
				data['cancel_reason'] = self.cancel_reason
			if data and self.update_status_url:
				try:
					request_response = requests.post(self.update_status_url, data)
					print("Response: %s , status: %s" % (request_response.text, request_response.status_code))
				except Exception as e:
					print(e)
		return res
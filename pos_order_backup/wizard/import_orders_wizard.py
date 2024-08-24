# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
import base64
import json

class PosDetails(models.TransientModel):
    _name = 'pos.import.orders.wizard'
    _description = 'Open Sales Details Report'

    order_json = fields.Binary(string="Order's JSON File", required=True)

    def import_data(self):
        for obj in self:
            if obj.order_json:
                data = None
                content = base64.decodestring(obj.order_json)
                try:
                    data = json.loads(content.decode('utf8'))
                except Exception as e:
                    raise UserError("File should be a valid JSON objects!")

                if data:
                    data_records = []
                    for order_json in data:
                        vals = {
                            'name': order_json['data']['name'],
                            'order_json': order_json,
                        }

                        # CHECK IF THE ORDER IS ALREADY PRESENT OR NOT
                        orders_obj =  self.env['pos.order.backup'].search([('name','=',vals['name'])])
                        if len(orders_obj):
                            raise ValidationError('Order already Imported.')
                        else:
                            backup_obj = self.env['pos.order.backup'].create(vals)
                            data_records.append(backup_obj)

                    ts_view_tree_id = self.env.ref('pos_order_backup.order_data_tree_view').id
                    ts_view_form_id = self.env.ref('pos_order_backup.order_data_form_view').id
                    return {
                        'name': 'Orders Data',
                        'type': 'ir.actions.act_window',
                        'res_model': 'pos.order.backup',
                        'view_mode': 'tree,form',
                        'view_type': 'tree',
                        'views': [[ts_view_tree_id, 'list'], [ts_view_form_id, 'form']],
                    }
            else:
                raise UserError("Please select a JSON file!")

    def import_and_create_orders(self):
        for obj in self:
            if obj.order_json:
                data = None
                content = base64.decodestring(obj.order_json)
                try:
                    data = json.loads(content.decode('utf8'))
                except Exception as e:
                    raise UserError("File should be a valid JSON objects!")

                if data:
                    data_record_ids = []
                    for order_json in data:
                        vals = {
                            'name': order_json['data']['name'],
                            'order_json': order_json,
                        }

                        #   CHECK IF ORDER IS ALREADY PRESENT OR NOT 
                        orders_obj =  self.env['pos.order.backup'].search([('name','=',vals['name'])])
                        if len(orders_obj):
                            raise ValidationError('Order already Imported.')
                        else:
                            backup_obj = self.env['pos.order.backup'].create(vals)
                            data_record_ids.append(backup_obj.id)

                    try:
                        self.env['pos.order.backup'].browse(data_record_ids).create_order_from_data()
                    except Exception as ex:
                        for order_json in data:
                            data_vals = {
                                'name': order_json['data']['name'],
                                'order_json': order_json,
                            }
                            self.env['pos.order.backup'].create(data_vals)

                        message=_("<h3>Data has been imported but orders could not be created successfully due to some error in the JSON(s)!</h3> <p> We recommend you to create the orders individually from the <b>Imported Order Data</b> list.</p>")
                        return self._order_restore_message(message)

                    ts_view_tree_id = self.env.ref('pos_order_backup.order_data_tree_view').id
                    ts_view_form_id = self.env.ref('pos_order_backup.order_data_form_view').id
                    return {
                        'name': 'Orders Data',
                        'type': 'ir.actions.act_window',
                        'res_model': 'pos.order.backup',
                        'view_mode': 'tree,form',
                        'view_type': 'tree',
                        'views': [[ts_view_tree_id, 'list'], [ts_view_form_id, 'form']],
                    }
            else:
                raise UserError("Please select a JSON file!")

    def _order_restore_message(self,message):
        message_id = self.env['wk.wizard.message'].create(dict(text=message))
        return {
            'name':"Order Backup/Restore!",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wk.wizard.message',
            'res_id': message_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
        }
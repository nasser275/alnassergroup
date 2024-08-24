# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################

import json
import ast
from odoo import api, fields, models

class PosOrderBackup(models.Model):
    _name = 'pos.order.backup'

    name = fields.Char("Name")
    order_json = fields.Text(string="Order JSON")
    results = fields.Text(string="Results")
    state = fields.Selection([
        ('open', 'Open'), 
        ('error', 'Error'), 
        ('cancel', 'Cancel'), 
        ('done', 'Done')], 
        default='open')

    def create_order_from_data(self):
        for obj in self:
            error = False
            cached_json = ast.literal_eval(obj.order_json)
            try:
                order_id = self.env['pos.order'].create_from_ui([cached_json])
            except Exception as e:
                error = e
            finally:
                if error:
                    self._cr.rollback()
                    new_vals = {'state': 'error','results': 'ERROR:' +  str(error) + '\n' + (obj.results or '')}
                else:
                    new_vals = {'state': 'done','results': 'ORDER CREATED SUCCESSFULLY' + '\n\n' + (obj.results or '')}
                obj.write(new_vals)


    def create_cancel(self):
        for obj in self:
            obj.write({'state': 'cancel'})
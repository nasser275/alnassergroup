# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.osv import expression


class InterWarehouseTransferLine(models.Model):
	_name = 'inter.transfer.line'
	_description = 'Inter Warehouse Transfer Line'	
	_rec_name = 'product_id'

	iwt_id = fields.Many2one('inter.warehouse.transfer',string="Inter Warehouse Transfer")
	product_id = fields.Many2one('product.product',string="Product",domain = [('type', '!=', 'service')])
	qty = fields.Float("Quantity" ,default=1.0)
	delivered_qty = fields.Float("Delivered Quantity" ,readonly=True)
	received_qty = fields.Float("Received Quantity" ,readonly=True)


class StockMove(models.Model):
	_inherit = 'stock.move.line'
	iwt_line_id = fields.Many2one('inter.transfer.line')



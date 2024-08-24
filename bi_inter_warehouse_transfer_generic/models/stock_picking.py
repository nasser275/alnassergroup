# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta ,date
from odoo import api, fields, models,tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.osv import expression



class StockPicking(models.Model):
	_inherit = 'stock.picking'

	inter_trans_id = fields.Many2one("inter.warehouse.transfer",string="Inter Warehouse Transfer",readonly=True)

	def _action_done(self):
		res = super(StockPicking, self)._action_done()
		if self.inter_trans_id and self.state == 'done':
			pickings = self.env['stock.picking'].search([('inter_trans_id', '=', self.inter_trans_id.id)])
			if all(pick.state == 'done' for pick in pickings):
				self.inter_trans_id.write({'state': 'done', 'from_loc_id': self.location_id.id, 'dest_loc_id': self.location_dest_id.id})
			for pick in pickings:
				for move in pick.move_line_ids_without_package:
					move.iwt_line_id.write({'delivered_qty':move.qty_done})
		return res

	def set_to_draft(self) :
		self.write({'state':'draft'})
		for move in self.move_ids_without_package :
			move.write({'state':'draft'})
		return



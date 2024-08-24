# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta,date,datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ChangeLocation(models.TransientModel):

	_name='change.location.wiz'
	_description = 'Change location wiz'

	company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company, index=True)
	from_loc_id = fields.Many2one('stock.location',string="From (Pick up) Location",
		domain = "[('usage', '=', 'internal'),('company_id', 'in', [company_id,False])]")
	dest_loc_id = fields.Many2one('stock.location',string="To (Drop down) Location",
		domain = "[('usage', '=', 'internal'),('company_id', 'in', [company_id,False])]")
	
	iwt_id = fields.Many2one('inter.warehouse.transfer',string="Inter Warehouse Transfer")
	picking_id = fields.Many2one('stock.picking',string="Stock Picking")
	picking_type_code = fields.Selection([('internal','Internal'),('incoming','Receipt'),
	('outgoing','Delivery')],string='Picking Type Code', default='internal',readonly=True)

	@api.model
	def default_get(self, fields):
		res = super(ChangeLocation, self).default_get(fields)
		sp = self.env['stock.picking'].sudo().browse(self._context.get('active_id'))
		if sp :
			pt = sp.picking_type_id
			src = sp.location_id.id if sp.location_id else False
			dest = sp.location_dest_id.id if sp.location_dest_id else False
			res.update({
				'from_loc_id':src,
				'dest_loc_id' : dest,
				'picking_id' : sp.id,
				'iwt_id' : sp.inter_trans_id.id if sp.inter_trans_id else False,
				'picking_type_code' : sp.picking_type_code,
			})
		return res

	def change_picking_type(self,pck_type):
		if self.picking_id.state != 'draft' :
			self.picking_id.action_cancel()
			self.picking_id.set_to_draft()

		self.picking_id.sudo().write({
			'picking_type_id': pck_type.id,
			'location_id': self.from_loc_id.id,
			'location_dest_id' : self.dest_loc_id.id,
		})
		for line in self.picking_id.move_line_ids_without_package:
			line.write({'location_id' : self.from_loc_id.id, 'location_dest_id' : self.dest_loc_id.id})
			
		self.picking_id.sudo().action_confirm()
		self.picking_id.sudo().action_assign()

	def update_locations(self):
		picking_type_code = self.picking_type_code

		if picking_type_code == 'internal':
			pck_type = self.env['stock.picking.type'].sudo().search([
				('default_location_src_id','=',self.from_loc_id.id),
				('default_location_dest_id','=',self.dest_loc_id.id)
			],limit=1)
		elif picking_type_code == 'incoming':
			pck_type = self.env['stock.picking.type'].sudo().search([
				('default_location_dest_id','=',self.dest_loc_id.id),
				('code','=','incoming')
			],limit=1)

		elif picking_type_code == 'outgoing':
			pck_type = self.env['stock.picking.type'].sudo().search([
				('default_location_src_id','=',self.from_loc_id.id),
				('code','=','outgoing')
			],limit=1)

		else:
			pass

		if pck_type :
			self.change_picking_type(pck_type)
			
		else:
			if picking_type_code == 'internal':
				pick_type_obj = self.env['stock.picking.type']
				s_code = 'INT'+'/'+str(self.from_loc_id.id)+'/'+str(self.dest_loc_id.id)+'/'
				src_name = self.sudo().from_loc_id.complete_name
				dest_name = self.sudo().dest_loc_id.complete_name
				pck_type = pick_type_obj.sudo().create({
					'name' : 'Internal Warehouse Transfer '+'/'+str(src_name)+'->'+str(dest_name),
					'code' : 'internal',
					'default_location_src_id' : self.from_loc_id.id,
					'default_location_dest_id' : self.dest_loc_id.id,
					'sequence_code' : s_code,
					'warehouse_id': False,
				})
				self.change_picking_type(pck_type)
			else:
				raise ValidationError(_("No Picking type found for this locations.Please select valid locations or create new picking type."))


	
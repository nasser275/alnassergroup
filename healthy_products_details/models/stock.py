from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Operation(models.Model):
    _inherit = 'stock.picking.type'

    enable_filter_products = fields.Boolean(string="Enable Filter Products By Supplier", default=True)


class Picking(models.Model):
    _inherit = 'stock.picking'
    supplier_ids = fields.Many2many(comodel_name="res.partner", relation="filter_suppliers",
                                    compute='_calc_supplier_ids')

    @api.depends('picking_type_id', 'partner_id')
    def _calc_supplier_ids(self):
        for rec in self:
            if rec.picking_type_id.enable_filter_products and self.partner_id:
                rec.supplier_ids = [(4, self.partner_id.id)]
            else:
                rec.supplier_ids = [(4, id) for id in
                                    self.env['product.product'].search([('supplier_id', '!=', False)]).mapped(
                                        'supplier_id.id')]

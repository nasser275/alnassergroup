from odoo import models, fields, api


class AlfaStock(models.Model):
    _inherit = 'stock.move'
    source_qty = fields.Integer(compute='product_in_location',
                                string='Source_qty', store=True)
    destination_qty = fields.Integer(compute='product_in_location',
                                     string='Destination_qty', store=True)

    @api.onchange('product_id')
    def product_in_location(self):
        source = []
        source_total = 0
        destination = []
        destination_total = 0

        for location_id in self.picking_id.location_id:
            for product_id in self.product_id:
                x = self.env['stock.quant'].search(
                    [('location_id', '=', location_id.id),
                     ('product_id', '=', product_id.id)])
                # print(x.id)
                for rec in x:
                    source.append(rec.id)
        # print(source)
        for ele in range(0, len(source)):
            source_total = source_total + source[ele]
        self.source_qty = source_total

        for dest_id in self.picking_id.location_dest_id:
            for dist_product_id in self.product_id:
                y = self.env['stock.quant'].search(
                    [('location_id', '=', dest_id.id),
                     ('product_id', '=', dist_product_id.id)])
                # print(y.id)
                for rec in x:
                    destination.append(rec.id)
        # print(destination)
        for ele in range(0, len(destination)):
            destination_total = destination_total + destination[ele]
        self.destination_qty = destination_total


class AlfaStockquant(models.Model):
    _inherit = 'stock.quant'
    _order = 'category_id desc, product_id'

    category_id = fields.Many2one(related='product_id.product_tmpl_id.categ_id',
                                  string='Category', index=True, store=True)

class AlfaStocklocation(models.Model):
    _inherit = 'stock.location'

    is_trans = fields.Boolean(string='Is Transit Location')


class AlfaStockpicking(models.Model):
    _inherit = 'stock.picking.type'

    pos_branch_allow = fields.Char(compute='_get_allows_branch')
    is_allow = fields.Boolean()

    def _get_allows_branch(self):
        for rec in self:
            print(rec.env.user)
            print(rec.env.user.branch_ids.ids)
            if rec.branch_id.id in rec.env.user.branch_ids.ids:
                rec.pos_branch_allow = 'allow'
                rec.is_allow = True
            else:
                rec.pos_branch_allow = 'disable'
                rec.is_allow = False

# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class stock_inventory(models.Model):
    _inherit = 'stock.inventory'


    @api.model
    def default_get(self,fields):
        res = super(stock_inventory, self).default_get(fields)
        if res.get('location_id'):
            location_branch = self.env['stock.location'].browse(res.get('location_id')).branch_id.id
            if location_branch:
                res['branch_id'] = location_branch 
        else:
            user_branch = self.env['res.users'].browse(self.env.uid).branch_id
            if user_branch:
                res['branch_id'] = user_branch.id
        return res

    branch_id = fields.Many2one('res.branch')



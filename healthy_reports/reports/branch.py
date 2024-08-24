from odoo import api, fields, models



from odoo import fields, models


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    branch_id = fields.Many2one('res.branch')



    def _select(self):
        return super(PosOrderReport, self)._select() + ", s.branch_id"

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ",s.branch_id"


# class StockValuationLayer(models.Model):
#     """Stock Valuation Layer"""
#
#     _inherit = 'stock.valuation.layer'
#     branch_id = fields.Many2one('res.branch',related='stock_move_id.branch_id',store=True)
class StockQuant(models.Model):

    _inherit = 'stock.quant'
    branch_id = fields.Many2one('res.branch',related='location_id.branch_id',store=True)

class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""
    _inherit = 'stock.valuation.layer'
    custom_location_id = fields.Many2one('stock.location',related='stock_move_id.location_id',store=True,string="Location")
    custom_branch_id = fields.Many2one('res.branch',related='custom_location_id.branch_id',store=True)


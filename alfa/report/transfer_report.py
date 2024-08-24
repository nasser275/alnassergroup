# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class TransferOrderReport(models.Model):
    _name = "report.transfer"
    _auto = False
    _order = 'date desc'

    date = fields.Datetime(string='Order Date', readonly=True)
    transfer_id = fields.Many2one('alfa.replanishment', string='Order', readonly=True)

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('request', 'Requested'), ('approve', 'Approved'), ('confirm', 'Confirmed'),
         ('cancel', 'Cancel')],
        string='State', readonly=True)

    warehouse_from = fields.Many2one('stock.location', string='From', readonly=True)
    warehouse_to = fields.Many2one('stock.location', string='To', readonly=True)
    nbr_lines = fields.Integer(string='Sale Line Count', readonly=True)

    product_categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    # transfer_ref_approve = fields.Char('Transfer Approve Reference', readonly=True)
    # transfer_ref_confirm = fields.Char('Transfer Confirm Reference', readonly=True)
    requested_qty = fields.Float(string='Requested quantity', readonly=True)
    approved_qty = fields.Float(string='Approved quantity', readonly=True)
    confirmed_qty = fields.Float(string='Confirmed quantity', readonly=True)
    sequence_num = fields.Char(string='Reference Sequence', readonly=True)
    sequence_confirm = fields.Char('Sequence Confirm', readonly=True)
    reference = fields.Char('Reference', readonly=True)
    difference = fields.Float('Diff', readonly=True)

    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                COUNT(*) AS nbr_lines,
                s.date_action AS date,
                s.id AS transfer_id,
                s.warehouse_from as warehouse_from,
                s.warehouse_to as warehouse_to,
                s.sequence_num as sequence_num,
                s.sequence_confirm as sequence_confirm,
                s.state AS state,
                l.product AS product_id,
                p.product_tmpl_id,
                pt.categ_id AS product_categ_id,
                SUM(l.requested_qty) AS requested_qty,
                SUM(l.confirmed_qty) AS confirmed_qty,
                SUM(l.approved_qty) AS approved_qty,
                s.reference AS reference,
                l.difference AS difference
                 
        """

    def _from(self):
        return """
            FROM alfa_replenishment_line AS l
                INNER JOIN alfa_replanishment s ON (s.id=l.replenishment_id)
                LEFT JOIN product_product p ON (l.product=p.id)
                LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
        """

    def _group_by(self):
        return """
            GROUP BY
                s.id,
                s.state, 
                pt.categ_id,
                l.product,
                p.product_tmpl_id,
                l.difference
        """

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._group_by())
                         )

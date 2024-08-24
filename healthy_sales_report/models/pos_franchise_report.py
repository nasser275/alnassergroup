# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PosfranshiseWPReport(models.Model):
    _name = "report.pos.sales.wp"
    _auto = False
    _order = 'branch_id'

    date = fields.Datetime(string='Order Date', readonly=True)
    order_id = fields.Many2one('pos.order', string='Order', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    state = fields.Selection(
        [('draft', 'New'), ('paid', 'Paid'), ('done', 'Posted'),
         ('invoiced', 'Invoiced'), ('cancel', 'Cancelled')],
        string='Status')
    user_id = fields.Many2one('res.users', string='User', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    nbr_lines = fields.Integer(string='Sale Line Count', readonly=True)
    product_qty = fields.Integer(string='Product Quantity', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    product_categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    invoiced = fields.Boolean(readonly=True)
    config_id = fields.Many2one('pos.config', string='Point of Sale', readonly=True)
    pos_categ_id = fields.Many2one('pos.category', string='PoS Category', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True)
    session_id = fields.Many2one('pos.session', string='Session', readonly=True)
    branch_id = fields.Many2one('res.branch', string='Branch', readonly=True)
    total_untaxed = fields.Float("Sales Amount", readonlyF=True)

    def _select(self):
        return """
            SELECT
                CASE WHEN l.disable_show_in_franchise = false THEN MIN(l.id) END AS id,
                COUNT(*) AS nbr_lines,
                s.date_order AS date,

                Case WHEN l.disable_show_in_franchise = false THEN SUM(l.qty) END AS product_qty,
                Case
                   WHEN  SUM(l.qty * l.price_unit ) <= 0 AND SUM(l.qty) >= 0 THEN 0
                   ELSE SUM((l.price_subtotal_incl + (l.qty * l.price_unit) * (l.discount/100)) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)
                END AS price_sub_total,
                CASE WHEN l.disable_show_in_franchise = false THEN SUM(l.price_subtotal) END AS total_untaxed,
                SUM(l.price_subtotal_incl / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS price_total,
                CASE
                 WHEN  SUM(l.qty * l.price_unit ) <= 0 AND SUM(l.qty) >= 0 THEN SUM(l.qty * l.price_unit )  * -1
                 ELSE  SUM((l.qty * l.price_unit) * (l.discount/100) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)
                 END   AS total_discount,
                CASE
                    WHEN SUM(l.qty * u.factor) = 0 THEN NULL
                    ELSE (SUM(l.qty*l.price_unit / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)/SUM(l.qty * u.factor))::decimal
                END AS average_price,
                SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
                Case
                   WHEN  SUM(l.qty) = 0 THEN NULL
                   ELSE SUM((l.total_cost / coalesce  (l.qty,1)) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)
                END AS unitcost,
                s.id as order_id,
                s.partner_id AS partner_id,
                s.state AS state,
                s.user_id AS user_id,
                s.company_id AS company_id,
                s.sale_journal AS journal_id,

                CASE
                    WHEN l.disable_show_in_franchise = false THEN l.product_id

                END AS product_id,
                pt.categ_id AS product_categ_id,
                p.product_tmpl_id,
                ps.config_id,
                pt.pos_categ_id,
                s.pricelist_id,
                s.session_id,
                s.branch_id,
                s.account_move IS NOT NULL AS invoiced,
                CASE
                 WHEN  SUM(l.price_subtotal - coalesce  (l.total_cost,0)) <= 0 AND SUM(l.price_subtotal) = 0 THEN 0
                 ELSE  SUM(l.price_subtotal - coalesce  (l.total_cost,0)  / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)
                END   AS margin
        """

    def _from(self):
        return """
                FROM pos_order_line AS l
                    INNER JOIN pos_order s ON (s.id=l.order_id)
                    LEFT JOIN product_product p ON (l.product_id=p.id)
                    LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
                    LEFT JOIN uom_uom u ON (u.id=pt.uom_id)
                    LEFT JOIN pos_session ps ON (s.session_id=ps.id)
                    LEFT JOIN res_company co ON (s.company_id=co.id)
                    LEFT JOIN res_currency cu ON (co.currency_id=cu.id)
                    WHERE l.disable_show_in_franchise = false
            """

    def _group_by(self):
        return """
                GROUP BY
                    s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id, s.company_id, s.sale_journal,
                    s.pricelist_id, s.account_move, s.create_date, s.session_id,
                    l.product_id,l.disable_show_in_franchise,
                    pt.categ_id, pt.pos_categ_id,
                    p.product_tmpl_id,
                    ps.config_id,
                    s.branch_id
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

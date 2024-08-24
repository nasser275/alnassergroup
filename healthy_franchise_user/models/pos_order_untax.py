from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    pos_order_id = fields.Integer(string='Order ID', compute='_get_order_id', store=True)

    @api.depends('order_id')
    def _get_order_id(self):
        for rec in self:
            rec.pos_order_id = rec.order_id.id


class Order(models.Model):
    _inherit = 'report.pos.order'
    _order = 'branch_id'

    total_untaxed = fields.Float("Sales Amount", readonly=True)
    unitcost = fields.Float(string='Unit Cost', readonly=True)

    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                COUNT(*) AS nbr_lines,
                s.date_order AS date,
                SUM(l.qty) AS product_qty,
                Case
                   WHEN  SUM(l.qty * l.price_unit ) <= 0 AND SUM(l.qty) >= 0 THEN 0
                   ELSE SUM((l.price_subtotal_incl + (l.qty * l.price_unit) * (l.discount/100)) / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)
                END AS price_sub_total,
                SUM(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS total_untaxed,
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
                l.product_id AS product_id,
                pt.categ_id AS product_categ_id,
                p.product_tmpl_id,
                ps.config_id,
                pt.pos_categ_id,
                s.pricelist_id,
                s.session_id,
                s.account_move IS NOT NULL AS invoiced,
                CASE
                 WHEN  SUM(l.price_subtotal - coalesce  (l.total_cost,0)) <= 0 AND SUM(l.price_subtotal) = 0 THEN 0
                 ELSE  SUM(l.price_subtotal - coalesce  (l.total_cost,0)  / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)
                END   AS margin
        """

# SUM(l.price_subtotal - l.total_cost / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS margin

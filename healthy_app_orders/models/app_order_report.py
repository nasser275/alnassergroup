# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class AppOrderReport(models.Model):
    _name = "app.order.report"
    _description = "APP Orders Analysis Report"
    _auto = False
    # _rec_name = 'due_date'
    # _order = 'due_date desc'

    name = fields.Char('Order Reference', readonly=True)
    order_date = fields.Date('Order Date', readonly=True)
    product_id = fields.Many2one('product.product', 'Product Variant', readonly=True)
    qty = fields.Float('Qty', readonly=True)
    price = fields.Float('Price', readonly=True)
    subtotal = fields.Float('Subtotal', readonly=True)
    # amount_total = fields.Float('Amount Total', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    due_date = fields.Datetime('Due Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('delivery', 'Delivery'),
        ('payment', 'Payment')],
        string='Status', readonly=True)
    discount = fields.Float('Discount %', readonly=True)
    order_id = fields.Many2one('app.order', 'Order #', readonly=True)
    external_app_id = fields.Integer(string='App ID', readonly=True)
    synced = fields.Boolean(string='Is Synced', readonly=True)
    deleted = fields.Boolean(string='Is Deleted', readonly=True)
    sales_person = fields.Many2one('res.users', string='Sales Person', readonly=True)
    pos_categ_id = fields.Many2one('pos.category', string='Pos Category', readonly=True)
    is_schedule = fields.Boolean(string="Is Schedule", readonly=True)
    saturday = fields.Boolean(string="Saturday", readonly=True)
    sunday = fields.Boolean(string="Sunday", readonly=True)
    monday = fields.Boolean(string="Monday", readonly=True)
    tuesday = fields.Boolean(string="Tuesday", readonly=True)
    wednesday = fields.Boolean(string="Wednesday", readonly=True)
    thursday = fields.Boolean(string="Thursday", readonly=True)
    friday = fields.Boolean(string="Friday", readonly=True)
    schedule_start_date = fields.Date(copy=False, required=False)
    schedule_end_date = fields.Date(copy=False, required=False)
    schedule_time = fields.Selection([
        ('0', '00'),
        ('1', '1:00'),
        ('2', '2:00'),
        ('3', '3:00'),
        ('4', '4:00'),
        ('5', '5:00'),
        ('6', '6:00'),
        ('7', '7:00'),
        ('8', '8:00'),
        ('9', '9:00'),
        ('11', '11:00'),
        ('12', '12:00'),
        ('13', '13:00'),
        ('14', '14:00'),
        ('15', '15:00'),
        ('16', '16:00'),
        ('17', '17:00'),
        ('18', '18:00'),
        ('19', '19:00'),
        ('20', '20:00'),
        ('21', '21:00'),
        ('22', '22:00'),
        ('23', '23:00'),
        ('24', '24:00'),
    ], string='Schedule Time',readonly=True)
    # schedule_time = fields.Integer(copy=False, required=False)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            min(l.id) as id,
            l.product_id as product_id,
            count(*) as nbr,
            ap.due_date as due_date,
            ap.name as name,
            ap.order_date as order_date,
            ap.state as state,
            ap.partner_id as partner_id,
            ap.company_id as company_id,
            ap.external_app_id as external_app_id,
            ap.synced as synced,
            ap.deleted as deleted,
            ap.sales_person as sales_person,
            t.pos_categ_id as pos_categ_id,
            ap.is_schedule as is_schedule,
            ap.saturday as saturday,
            ap.sunday as sunday,
            ap.monday as monday,
            ap.tuesday as tuesday,
            ap.wednesday as wednesday,
            ap.thursday as thursday,
            ap.friday as friday,
            ap.schedule_start_date as schedule_start_date,
            ap.schedule_end_date as schedule_end_date,
            ap.schedule_time as schedule_time,
            sum(l.qty) qty,
            sum(l.price) as price,
            sum(l.subtotal) as subtotal,
            sum(l.discount) as discount,
            ap.id as order_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                app_order_lines l
                      join app_order ap on (l.app_order_id=ap.id)
                      join res_partner partner on ap.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                %s
        """ % from_clause

        groupby_ = """
            l.product_id,
            ap.order_date,
            ap.due_date,
            ap.partner_id,
            ap.company_id,
            ap.state,
            ap.sales_person,
            ap.external_app_id,
            ap.synced,
            ap.deleted,
            ap.sales_person,
            t.pos_categ_id,
            ap.name,
            ap.is_schedule,
            ap.saturday,
            ap.sunday,
            ap.monday,
            ap.tuesday,
            ap.wednesday,
            ap.thursday,
            ap.friday,
            ap.schedule_start_date,
            ap.schedule_end_date,
            ap.schedule_time,
            ap.id %s
        """ % (groupby)


        # print('%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_))
        return '%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL AND ap.deleted = False GROUP BY %s)' % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

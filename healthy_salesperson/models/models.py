# -*- coding: utf-8 -*-

from odoo import models, fields, api



class Employee(models.Model):
    _inherit = 'hr.employee'
    is_sales_person = fields.Boolean(string="Sales Person",  )

class PosOrder(models.Model):
    _inherit='pos.order'
    sales_person = fields.Many2one(comodel_name='hr.employee',string="Sales Represtiative")

    def _order_fields(self, ui_order):
        order = super(PosOrder, self)._order_fields(ui_order)
        order['sales_person'] = ui_order.get('sales_person')
        return order


    def _prepare_refund_values(self, current_session):
        data = super(PosOrder, self)._prepare_refund_values(current_session)
        data['sales_person']=self.sales_person.id
        return data

    def _export_for_ui(self, order):
        for rec in self:
            data = super(PosOrder, rec)._export_for_ui(order)
            data['sales_person'] = rec.sales_person.id
        return data




class PosConfig(models.Model):
    _inherit = 'pos.config'
    show_sales_represtiative = fields.Boolean(string='Show Sales Represtiative', default=False)

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    sales_person = fields.Many2one(comodel_name='hr.employee',string="Sales Represtiative")

    def _select(self):
        return super(PosOrderReport, self)._select() + ',s.sales_person AS sales_person'

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ',s.sales_person'

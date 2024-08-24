# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api
from datetime import datetime
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero

import phonenumbers

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_gift = fields.Boolean(string="Is a Gift")
    gift_discount = fields.Float(string="Gift Discount", required=False)
    extra_margin = fields.Boolean(string="Extra Margin", required=False)


class Employee(models.Model):
    _inherit = 'hr.employee'

    is_delivery_person = fields.Boolean(string="Delivery Person", )
    branch_id = fields.Many2one('res.branch', string='Branch', required=True, index=True,
                                default=lambda self: self.env.user.branch_id.id)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    delivery_person_id = fields.Many2one(comodel_name="hr.employee", string="Delivery Person")
    delivery_amount = fields.Float(string="Delivery Amount")
    free_delivery = fields.Boolean(string="Free Delivery")
    is_delivery = fields.Boolean()
    send_to_tayar = fields.Boolean()
    progress_date = fields.Datetime(string="Progress Date")
    paid_date = fields.Datetime(string="Paid Date")
    cancel_date = fields.Datetime(string="Cancel Date")
    is_point_converted = fields.Boolean(string='Points Converted')
    state = fields.Selection(
        [('draft', 'New'), ('in_prgress', 'In Prgress'), ('cancel', 'Cancelled'), ('paid', 'Paid'), ('done', 'Posted'),
         ('invoiced', 'Invoiced')],
        'Status', readonly=True, copy=False, default='draft')

    cancel_reason_id = fields.Many2one(comodel_name="pos.cancel.reasons", string="Cancel Reason", required=False)
    return_reason = fields.Many2one(comodel_name="pos.return.reasons", string="Return Reason", required=False)

    def _create_order_picking2(self):
        self.ensure_one()
        if self.to_ship:
            self.lines._launch_stock_rule_from_pos_order_lines()
        else:
            _logger.info("Orders: %s,State: %s, Picking: %s, Refunded: %s" % (
                self.id, self.state, self.picking_ids, self.refunded_orders_count))
            if self._should_create_picking_real_time():
                picking_type = self.config_id.picking_type_id
                if self.partner_id.property_stock_customer:
                    destination_id = self.partner_id.property_stock_customer.id
                elif not picking_type or not picking_type.default_location_dest_id:
                    destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
                else:
                    destination_id = picking_type.default_location_dest_id.id

                pickings = self.env['stock.picking']._create_picking_from_pos_order_lines(destination_id, self.lines,
                                                                                          picking_type, self.partner_id)
                pickings.write({'pos_session_id': self.session_id.id, 'pos_order_id': self.id, 'origin': self.name})

                self.env['pos.order.create.picking'].sudo().search([('order_id', '=', self.id)]).unlink()

                # if pickings.id:
                #     _logger.info("Picking: %s" % pickings)
                #     stock_move = self.env['stock.move'].sudo().search(
                #         [('picking_id', '=', pickings.id)])
                #
                #     # _logger.info("Moves: %s" % stock_move)
                #     # _logger.info("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTE")
                #     # self.set_all_analytic()
                #     for move in stock_move:
                #         accounts = self.env['account.move'].sudo().search(
                #             [('stock_move_id', '=', move.id)],
                #             limit=1)
                #         # _logger.info("Accounts: %s , Branch: %s" % (accounts.id, accounts.branch_id))
                #         accounts.write({'branch_id': self.session_id.config_id.branch_id.id})
                #         accounts.line_ids.write({
                #             'analytic_account_id': pickings.pos_session_id.config_id.account_analytic_id.id})
                #         # _logger.info("Accounts: %s , Branch: %s" % (accounts.id, accounts.branch_id))
                #         # _logger.info("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTE")

#    def _create_order_picking(self):
  #      if not self.env['pos.order.create.picking'].sudo().search([('order_id', '=', self.id)]):
 #           self.env['pos.order.create.picking'].sudo().create({
   #             'order_id': self.id
    #        })

    def refund(self):
        return {
            'name': "POS Password",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.password.return.wiz',
            'view_id': self.env.ref('ks_pos_low_stock_alert.pos_password_return_wiz').id,
            'target': 'new'
        }

    def validated_refund(self):
        for rec in self:
            if not rec.return_reason:
                raise ValidationError("Add Return Reason")
            else:
                res = super(PosOrder, self).refund()
                return res

    # def write(self, values):
    #     if values.get('state') == 'in_prgress':
    #         values['progress_date'] = datetime.now()
    #     if values.get('state') == 'paid':
    #         values['paid_date'] = datetime.now()
    #     if values.get('state') == 'cancel':
    #         values['cancel_date'] = datetime.now()
    #     res = super(PosOrder, self).write(values)
    #     return res

    def action_pos_order_in_prgress(self):
        for order in self:
            order.write({'state': 'in_prgress'})

    def _order_fields(self, ui_order):
        order = super(PosOrder, self)._order_fields(ui_order)
        order['delivery_person_id'] = ui_order.get('delivery_person_id')
        order['delivery_amount'] = ui_order.get('delivery_amount')
        order['free_delivery'] = ui_order.get('free_delivery')
        order['is_delivery'] = ui_order.get('is_delivery')
        order['return_reason'] = ui_order.get('return_reason')
        return order

    @api.depends('lines.margin', 'lines.extra_margin_value', 'is_total_cost_computed')
    def _compute_margin(self):
        for order in self:
            if order.is_total_cost_computed:
                order.margin = sum(order.lines.mapped('margin')) + sum(order.lines.mapped('extra_margin_value'))
                amount_untaxed = order.currency_id.round(sum(line.price_subtotal for line in order.lines))
                order.margin_percent = not float_is_zero(amount_untaxed,
                                                         order.currency_id.rounding) and order.margin / amount_untaxed or 0
            else:
                order.margin = 0
                order.margin_percent = 0

    def create_all_picking(self):
        _logger.info("Start in POS/////////")

        for rec in self.env['pos.order.create.picking'].sudo().search([], order='id desc', limit=10):
            _logger.info("in in in POS/////////")
            _logger.info(rec.order_id.id)
            if rec.order_id:
                if rec.order_id.picking_ids:
                    self.env['pos.order.create.picking'].sudo().search([('order_id', '=', rec.order_id.id)]).unlink()
                else:
                    if rec.order_id.state in ['paid', 'invoiced', 'done'] and not (rec.order_id.picking_ids):
                        rec.order_id._create_order_picking2()

    def create_all_picking_desc(self, reclimit=10):
        _logger.info("Start in POS/////////")

        for rec in self.env['pos.order.create.picking'].sudo().search([], order='id desc', limit=reclimit):
            _logger.info("in in in POS/////////")
            _logger.info(rec.order_id.id)
            if rec.order_id:
                if rec.order_id.picking_ids:
                    self.env['pos.order.create.picking'].sudo().search([('order_id', '=', rec.order_id.id)]).unlink()
                else:
                    if rec.order_id.state in ['paid', 'invoiced', 'done'] and not (rec.order_id.picking_ids):
                        rec.order_id._create_order_picking2()

    def create_all_picking_asc(self, reclimit=10, branch_id=False):
        _logger.info("Start in POS/////////")
        domain = [('order_id.state', 'in', ['paid', 'invoiced', 'done'])]
        if branch_id:
            domain.append(('order_id.branch_id', '=', branch_id))
        for rec in self.env['pos.order.create.picking'].sudo().search(domain, order='id asc', limit=reclimit):
            _logger.info("in in in POS/////////")
            _logger.info(rec.order_id.id)
            if rec.order_id:
                if rec.order_id.picking_ids:
                    self.env['pos.order.create.picking'].sudo().search([('order_id', '=', rec.order_id.id)]).unlink()
                else:
                    if rec.order_id.state in ['paid', 'invoiced', 'done'] and not (rec.order_id.picking_ids):
                        rec.order_id._create_order_picking2()

    def set_all_analytic(self):
        for record in self.env['account.move'].sudo().search(
                [('branch_id', '=', False), ('create_date', '>', datetime.now() - timedelta(days=60))]):
            if not record.branch_id:
                config_id = self.env['pos.session'].sudo().search(
                    [('id', '=', record.stock_move_id.picking_id.pos_session_id.id)],
                    limit=1)
                if config_id:
                    record.write({'branch_id': config_id.branch_id.id})
                    record.line_ids.write({
                        'analytic_account_id': record.stock_move_id.picking_id.pos_session_id.config_id.account_analytic_id.id})


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    is_gift = fields.Boolean(string="Is a Gift")
    extra_margin = fields.Boolean(store=True, related='product_id.extra_margin')
    extra_margin_value = fields.Float(compute='_compute_margin', string="Extra Margin")

    @api.depends('price_subtotal', 'total_cost', 'extra_margin')
    def _compute_margin(self):
        for line in self:
            if line.extra_margin:
                line.margin = 0
                line.margin_percent = 0
                line.extra_margin_value = line.price_subtotal - line.total_cost
            else:
                line.margin = line.price_subtotal - line.total_cost
                line.extra_margin_value = 0
                line.margin_percent = not float_is_zero(line.price_subtotal,
                                                        line.currency_id.rounding) and line.margin / line.price_subtotal or 0


class PosConfig(models.Model):
    _inherit = 'pos.config'
    enable_delivery_service = fields.Boolean(string='Enable Delivery Service', default=False)
    delivery_service_product_id = fields.Many2one('product.product', string='Delivery Service Product',
                                                  domain="[('is_delivery_charge','=',True)]", )
    enable_gift = fields.Boolean(string="Enable Gift")


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def get_product(self, product, location):
        res = []
        pro = self.env['product.product'].browse(product)
        quants = self.env['stock.quant'].search(
            [('product_id', '=', pro.id), ('location_id', '=', location)])
        if len(quants) > 1:
            quantity = 0.0
            for quant in quants:
                quantity += quant.quantity
            res.append([pro.id, quantity])
        else:
            res.append([pro.id, quants.quantity])
        return res


class ProductDeliveryCharge(models.Model):
    _inherit = 'product.product'

    is_delivery_charge = fields.Boolean('Delivery Charge')


class PosPickingAfter(models.Model):
    _name = 'pos.order.create.picking'
    order_id = fields.Many2one(comodel_name="pos.order")


class PosMainCombo(models.Model):
    _name = 'pos.order.main.combo'
    order_id = fields.Many2one(comodel_name="pos.order")


class JournalsTodraft(models.Model):
    _name = 'account.move.journal.draft'
    journal_id = fields.Many2one(comodel_name="account.move")


class Journalsitemsadjust(models.Model):
    _name = 'account.move.line.byjournal'
    journal_id = fields.Many2one(comodel_name="account.move")


class JournalsBranchset(models.Model):
    _name = 'journals.branch.analytic'
    journal_id = fields.Many2one(comodel_name="account.move")


class setjournalitemadjust(models.Model):
    _inherit = 'account.move.line'

    def removecogs(self, limitnumbers=1, orderby='id desc'):
        _logger.info("Start in journal/////////")
        for rec in self.env['account.move.line.byjournal'].sudo().search([], order=orderby, limit=limitnumbers):
            _logger.info("in in in journal/////////")
            _logger.info(rec.journal_id.id)
            if rec.journal_id:
                self.env['account.move.line'].sudo().search(
                    [('move_id', '=', rec.journal_id.id), ('account_id', 'in', [1098, 26])]).unlink()
                self.env['account.move.line.byjournal'].sudo().search([('id', '=', rec.id)]).unlink()
                _logger.info("Start in itemmmmm/////////")


class setjournaltodraft(models.Model):
    _inherit = 'account.move'

    def setjtodraft(self):
        _logger.info("Start in journal/////////")

        for rec in self.env['account.move.journal.draft'].sudo().search([], order='id desc', limit=3):
            _logger.info("in in in journal/////////")
            _logger.info(rec.journal_id.id)
            if rec.journal_id:
                self.env['account.move'].sudo().search([('id', '=', rec.journal_id.id)]).button_draft()
                self.env['account.move.journal.draft'].sudo().search([('id', '=', rec.id)]).unlink()

    def setBranchandAnalyticAccount(self, limitnumbers=1, orderby='id desc'):
        _logger.info("Start in journal/////////")
        for rec in self.env['journals.branch.analytic'].sudo().search([], order=orderby, limit=limitnumbers):
            _logger.info("in in in journal/////////")
            if rec.journal_id:
                move = self.env['account.move'].sudo().search([('id', '=', rec.journal_id.id)])
                branch_id = move.stock_move_id.picking_id.pos_session_id.branch_id.id
                analytic_id = move.stock_move_id.picking_id.pos_session_id.config_id.account_analytic_id.id
                _logger.info(branch_id)
                _logger.info(analytic_id)

                move.write({'branch_id': branch_id})
                move.line_ids.write({'analytic_account_id': analytic_id})

                # self.env['journals.branch.analytic'].sudo().search([('id', '=', rec.id)]).unlink()

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res=super(StockQuant, self)._get_inventory_move_values(qty, location_id, location_dest_id, out)
        res['branch_id']=self.branch_id.id
        return res

class PosMoves(models.Model):
    _inherit = 'account.move'

    def prepare_all_moves(self):
        for record in self:
            config_id = record.env['pos.session'].search([('move_id', '=', record.id)], limit=1).config_id
            if config_id:
                record.write({'branch_id': config_id.branch_id.id})
            record.line_ids.write({'analytic_account_id': config_id.account_analytic_id.id})


class StockMove(models.Model):
    _inherit = 'stock.move'



    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                   cost):
        self.ensure_one()
        # self = self.sudo()

        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        date = self._context.get('force_period_date', fields.Date.context_today(self))
        session = self.env['pos.session'].sudo().search(
            [('branch_id', '=', self.picking_id.picking_type_id.branch_id.id)], limit=1)
        if session:
            for line in move_lines:
                line[2]['branch_id'] = self.picking_id.picking_type_id.branch_id.id
                line[2]['analytic_account_id'] = session.config_id.account_analytic_id.id
        else :
            for line in move_lines:
                line[2]['branch_id'] =  self.branch_id.id
                line[2]['analytic_account_id'] =self.env['account.analytic.account'].sudo().search([('name','=',self.branch_id.name)],limit=1).id

        branch_id=False
        if self.branch_id:
            branch_id= self.branch_id.id
        else:
            branch_id = self.picking_id.picking_type_id.branch_id.id

        return {
            'journal_id': journal_id,
            'line_ids': move_lines,
            'date': date,
            'ref': description,
            'stock_move_id': self.id,
            'stock_valuation_layer_ids': [(6, None, [svl_id])],
            'move_type': 'entry',
            'branch_id':branch_id,
        }


class OrderLine(models.Model):
    _inherit = 'pos.order'
    account_analytic_id = fields.Many2one(comodel_name="account.analytic.account", string="Analytic Accounts",
                                          related='config_id.account_analytic_id', store=True)

    def _prepare_invoice_line(self, order_line):
        res = super(OrderLine, self)._prepare_invoice_line(order_line)
        res['analytic_account_id'] = self.config_id.account_analytic_id.id
        res['branch_id'] = self.config_id.branch_id.id
        return res


class Session(models.Model):
    _inherit = 'pos.session'

    def _create_account_move(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        data = super(Session, self)._create_account_move(balancing_account=False, amount_to_balance=0,
                                                         bank_payment_method_diffs=None)
        for move in self.move_id:
            for line in move.line_ids:
                line.write({'analytic_account_id': self.config_id.account_analytic_id.id})
        self.move_id.write({'branch_id': self.config_id.branch_id.id})
        self.move_id.mapped('line_ids').create_analytic_lines()

        return data

# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.http import Controller, route, request, Response


class res_users(models.Model):
    _inherit = 'res.users'

    # branch_id = fields.Many2one('res.branch', 'Current Branch')
    # branch_ids = fields.Many2many('res.branch', id1='user_id', id2='branch_id',string='Allowed Branches')

    is_branch_user = fields.Boolean("Is branch user", compute="_compute_branch_user")

    def _compute_branch_user(self):
        for user in self:

            b_usr = user.has_group('pos_branch.group_branch_user')
            b_mngr = user.has_group('pos_branch.group_branch_user_manager')
            non_user_group = self.env.ref('pos_branch.group_no_branch_user')
            if not b_usr and not b_mngr:
                non_user_group.write({
                    'users': [(4, user.id)]
                })
            else:
                non_user_group.write({
                    'users': [(3, user.id)]
                })
            user.is_branch_user = False


# class res_branch(models.Model):
# 	_name = 'res.branch'
# 	_description = "Res Branch"
#
# 	name = fields.Char('Name', required=True)
# 	address = fields.Text('Address', size=252)
# 	telephone_no = fields.Char("Telephone No")
# 	company_id =  fields.Many2one('res.company', 'Company', required=True)


class pos_session(models.Model):
    _inherit = 'pos.session'

    branch_id = fields.Many2one('res.branch', readonly=True)
    pos_branch = fields.Char(string='Telephone No', related='branch_id.telephone', store=True)
    pos_branch_allow = fields.Char(compute='_get_allows_branch')
    is_allow = fields.Boolean()

    def _get_allows_branch(self):
        for rec in self:
            if rec.branch_id.id in rec.user_id.branch_ids.ids:
                rec.pos_branch_allow = 'allow'
                rec.is_allow = True
            else:
                rec.pos_branch_allow = 'disable'
                rec.is_allow = False

    @api.model
    def create(self, vals):
        res = super(pos_session, self).create(vals)
        res.write({
            'branch_id': res.config_id.branch_id.id
        })
        return res


class pos_config(models.Model):
    _inherit = 'pos.config'

    branch_id = fields.Many2one('res.branch', string='Branch')


class POSOrder(models.Model):
    _inherit = 'pos.order'

    branch_id = fields.Many2one('res.branch', 'Branch', readonly=True)

    @api.model
    def _process_order(self, order, draft, existing_order):
        res = super(POSOrder, self)._process_order(order, draft, existing_order)
        pos_order = self.browse(res)
        if pos_order:
            pos_order.write({
                'branch_id': pos_order.config_id.branch_id.id
            })

            if not pos_order.session_id.branch_id:
                pos_order.session_id.write({
                    'branch_id': pos_order.config_id.branch_id.id
                })
        return res


class pos_payment(models.Model):
    _inherit = 'pos.payment'

    branch_id = fields.Many2one('res.branch', related='pos_order_id.branch_id')


class account_bank_statement(models.Model):
    _inherit = 'account.bank.statement'

    branch_id = fields.Many2one('res.branch', 'Branch', related='pos_session_id.branch_id')


class account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'

    branch_id = fields.Many2one('res.branch', 'Branch', related='statement_id.branch_id')


class ResBranchIn(models.Model):
    _inherit = "res.branch"
    _order = 'sequence,id'

    sequence = fields.Integer('seq')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

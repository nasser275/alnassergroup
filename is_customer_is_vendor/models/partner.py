# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit='res.partner'
    customer= fields.Boolean(string="Customer?")
    supplier= fields.Boolean(string="Vendor?")




class Invoice(models.Model):
    _inherit='account.move'

    @api.onchange('move_type')
    def onchange_type33(self):
        print("DLLLLLLLLLLL")
        if self.move_type=='out_invoice':
            domain = [('customer','=',True),'|',('company_id','=',False),('company_id','=',self.env.user.company_id.id)]
            return {
                'domain': {'partner_id': domain}
            }
        if self.move_type=='in_invoice':
            domain = [('supplier','=',True),'|',('company_id','=',False),('company_id','=',self.env.user.company_id.id)]
            return {
                'domain': {'partner_id': domain}
            }
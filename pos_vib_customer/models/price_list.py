# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Pricelist(models.Model):
    _inherit='product.pricelist'
    is_vib = fields.Boolean(string="IS VIB?")


    @api.constrains('is_vib')
    def _check_one_pricelist(self):
        res=self.search([('is_vib','=',True)])-self
        if res:
            raise ValidationError("Dont Allow Found More VIB PriceList !")

class PosConfig(models.Model):
    _inherit = 'pos.config'
    show_price_list = fields.Boolean(string='Show Price Lists', default=True)






# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product_custom(models.Model):
    _inherit = 'product.product'

    general_classification = fields.Selection([('medicine','Medicine'),('lab','Lab')
                                               ,('beautifying','Beautifying')],string='General Classification')
    shape_classification = fields.Selection([('cones', 'Cones'), ('accessories', 'Accessories')
                                                  , ('ampoules', 'Ampoules')], string='Shape Classification')
    medicine_shape = fields.Selection([('tablets', 'Tablets'), ('suppository', 'Suppository')], string='Medicine Shape')
    department = fields.Selection([('milk', 'Milk'), ('healthy', 'Healthy'),('perfumes','Perfumes')], string='Department')
    use = fields.Char( string='Use')
    refrigerator = fields.Boolean( string='Refrigerator')
    world_barcode = fields.Char( string='World Barcode')
    effective_material = fields.Char( string='Effective Material')
    production_company = fields.Char( string='Production Company')
    code = fields.Char("Code")
    calculation_type = fields.Selection([('manual','Manual'),('automatic','Automatic')],default='manual',string="Type")
    minimum = fields.Float("Minimum",compute='calcuate_maximum_mi' )
    minimum_days = fields.Float("Minimum Of Days")
    maximum = fields.Float("Maximum",compute='calcuate_maximum_mi' )
    maximum_days = fields.Float("Maximum of Days")
    consumption_daily = fields.Float("For daily consumption")
    minimum_manual = fields.Float("Minimum")
    maximum_manual = fields.Float("Maximum")




    @api.depends('consumption_daily', 'maximum_days', 'minimum_days','calculation_type')
    def calcuate_maximum_mi(self):
         for rec in self:
             rec.minimum = 0
             rec.maximum = 0
             if rec.minimum_days > 0 and rec.consumption_daily > 0 and rec.calculation_type == 'automatic':
                rec.minimum = rec.consumption_daily * rec.minimum_days

             if rec.maximum_days > 0 and rec.consumption_daily > 0 and rec.calculation_type == 'automatic':
                    rec.maximum = rec.consumption_daily * rec.maximum_days





    def action_sales_ok(self):
        if self.sale_ok == False:
            self.sale_ok=True
        elif self.sale_ok == True:
            self.sale_ok=False
    def action_purchase_ok(self):
        if self.purchase_ok == False:
            self.purchase_ok=True
        elif self.purchase_ok == True:
            self.purchase_ok=False



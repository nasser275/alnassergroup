# -*- coding: utf-8 -*-
from odoo import models, fields
from lxml import etree

class ResUsers(models.Model):
    
    _inherit = 'res.groups'
    
    hide_create_objects = fields.Many2many('ir.model',string="Hide Button Objects")
    is_hide_create_group = fields.Boolean("Is hide Create group",default=False)

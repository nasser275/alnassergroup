# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit='res.partner'
    wasfah = fields.Char(string='الوصفه')


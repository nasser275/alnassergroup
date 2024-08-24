# -*- coding: utf-8 -*-

from odoo import models, fields, api

class User(models.Model):
    _inherit = 'res.users'
    user_position = fields.Many2one(comodel_name="user.position", string="Position", required=False)



class position(models.Model):
    _name='user.position'
    name = fields.Char(string="Name", required=True)

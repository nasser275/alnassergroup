# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class healthy_accounting(models.Model):
#     _name = 'healthy_accounting.healthy_accounting'
#     _description = 'healthy_accounting.healthy_accounting'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

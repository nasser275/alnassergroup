from odoo import api, fields, models

class Common(models.Model):
    _name='common.questions'
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description", required=False)

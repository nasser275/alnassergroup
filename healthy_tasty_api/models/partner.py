from odoo import api, fields, models, SUPERUSER_ID


class Partner(models.Model):
    _inherit = 'res.partner'

    def create_partner(self, vals):
        with self.pool.cursor() as cr:
            res = self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).create(vals)
            return res


class User(models.Model):
    _inherit = 'res.users'

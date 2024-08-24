import werkzeug

from odoo.exceptions import AccessDenied
from odoo import api, models, fields,SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    access_token_ids = fields.One2many(
        string='Access Tokens',
        comodel_name='jwt_provider.access_token',
        inverse_name='user_id',
    )

    def create_user(self,vals):
        with self.pool.cursor() as cr:
            res = self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).create(vals)
            return res

    def update_user(self,vals):
        with self.pool.cursor() as cr:
            res = self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).write(vals)
            return res


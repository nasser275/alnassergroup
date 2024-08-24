# from odoo import api, fields, models
# from odoo.exceptions import ValidationError
# from odoo import SUPERUSER_ID
# class Location(models.Model):
#     _inherit='stock.location'
#
#
#     @api.model
#     def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
#         new_args=[('id', '=', 24)]
#         return super(Location, self)._search(new_args, offset=offset, limit=limit, order=order, count=count,
#                                                access_rights_uid=SUPERUSER_ID)
#

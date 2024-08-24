# -*- coding: utf-8 -*-


from odoo import fields, models, api
from odoo.exceptions import ValidationError

import phonenumbers
import re


class Partner(models.Model):
    _inherit = 'res.partner'
    ise_user = fields.Boolean()




    @api.constrains('mobile', 'phone', 'name')
    @api.model
    def check_phone_no(self):
        default_ise_user = self._context.get('default_ise_user', False)
        if default_ise_user == False:
            for partner in self:
                if partner.phone or partner.mobile:
                    pass
                else:
                    raise ValidationError('يجب اضافة رقم الهاتف او المحمول')
                if not (partner.name):
                    raise ValidationError('يجب اضافة الاسم ')

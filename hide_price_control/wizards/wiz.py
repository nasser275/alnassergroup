# -*- coding: utf-8 -*-


from odoo import fields, models, _
from odoo.exceptions import ValidationError




class ChangePaword(models.TransientModel):
    _name = 'healthy.pos.password'
    old_password = fields.Char(string="Old Password", required=True)
    new_password = fields.Char(string="New Password", required=True)

    def change_pws(self):
        if self.env.user.use_pos_password:
            if self.env.user.user_password:
                if self.old_password==self.env.user.user_password:
                   self.env.user.sudo().write({'user_password':self.new_password})
                else:
                    raise ValidationError("كلمة السر القديمة غير صحيحة")



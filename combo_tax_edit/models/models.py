from odoo import models, fields, api


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    tax_computed = fields.Boolean('')
    price_recomputed = fields.Boolean('')

    def _modify_combo_tax(self):
        for rec in self.env['pos.order'].sudo().search([('tax_computed', '=', False)], limit=20):
            for line in rec.lines:
                if line.is_combo:
                    line.sudo().write({'tax_ids': [(6, 0, [x.id for x in line.product_id.taxes_id])]})
            rec.tax_computed = True

    def _modify_combo_price(self):
        for rec in self.env['pos.order.main.combo'].sudo().search([],
                                                                  limit=20):
            for line in rec.order_id.lines:

                if line.is_combo and line.main_combo and len(rec.env['pos.order.line'].sudo().search(
                        [('order_id', '=', rec.order_id.id), ('combo_name', '=', line.combo_name),
                         ('product_id', '!=', line.product_id.id)])) >= 1:
                    line.sudo().write({'price_subtotal': 0, 'price_subtotal_incl': 0})

            rec.order_id._onchange_amount_all()
            rec.unlink()


from odoo import models, fields, api
import itertools


class Order(models.Model):
    _name = 'purchase.talabayat'
    type = fields.Selection([('minimum', 'Minimum'), ('maximum', 'Maximum')], string="Type", defualt="minimum")
    product_ids = fields.Many2many("product.product", "pro_id", "id", string="Product")
    line_ids = fields.One2many("purchase.talabayat.line", "order_id", string="Lines")
    purchase_count = fields.Integer("Orders")
    name = fields.Char("Name")

    def get_lines(self):
        order_line = self.env['purchase.talabayat.line']
        for rec in self.line_ids:
            rec.unlink()
        for rec in self.product_ids:
            if rec.calculation_type == 'automatic':

                if self.type == 'minimum' and rec.qty_available < rec.minimum:
                    order_line.create({
                        'product_id': rec.id,
                        'partner_ids': [(4, record.name.id) for record in
                                        rec.seller_ids],
                        'order_id': self.id,
                        'qty': rec.maximum - rec.qty_available,
                    })
                elif self.type == 'maximum' and rec.qty_available < rec.maximum:
                    order_line.create({
                        'product_id': rec.id,
                        'partner_ids': [(4, record.name.id) for record in
                                        rec.seller_ids],
                        'order_id': self.id,
                        'qty': rec.maximum - rec.qty_available,
                    })

    def create_purchase_order(self):
        partner_id = []
        data = []
        for rec in self.line_ids:
            partner_id.append(rec.partner_ids[0])
            data.append({
                'partner_id': rec.partner_ids[0].id,
                'product_id': rec.product_id.id,
                'qty': rec.qty,
                'product_tmpl_id': rec.product_id.product_tmpl_id.id

            })
        docs = sorted(data, key=lambda i: (i['partner_id']))
        count = 0
        for key, group in itertools.groupby(docs, key=lambda x: (x['partner_id'])):
            purchase_lines = []
            vendor_id = ''
            for item in group:
                vendor_id = item['partner_id']
                purchase_lines.append((0, 0, {
                    'product_id': item['product_id'],
                    'product_qty': item['qty'],
                    'price_unit': self.env['product.supplierinfo'].search([('name', '=', item['partner_id']),
                                                                           ('product_tmpl_id', '=',
                                                                            item['product_tmpl_id'])], limit=1).price
                }))
            self.env['purchase.order'].create({
                'partner_id': vendor_id,
                'order_line': purchase_lines,
                'talabayat_id': self.id
            })
            count += 1
        self.purchase_count = count

    def view_purchase_order(self):

        return {
            'name': ('RFQ'),
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',

            'context': self.env.context,
            'domain': [('talabayat_id', '=', self.id)],
            'target': 'current',
        }


class Orderlines(models.Model):
    _name = 'purchase.talabayat.line'
    product_id = fields.Many2one("product.product", string="Product")
    partner_ids = fields.Many2many("res.partner", "partner_id", "id", string="Vendors")
    order_id = fields.Many2one("purchase.talabayat")
    qty = fields.Float("Quantity")


class Purchase(models.Model):
    _inherit = 'purchase.order'
    talabayat_id = fields.Many2one("purchase.talabayat")

    def button_confirm(self):
        res = super(Purchase, self).button_confirm()
        receipts = self.env['stock.picking'].search([('origin', '=', self.name)], limit=1)
        for line in receipts.move_ids_without_package:
            line.write({'quantity_done': line.product_uom_qty})
        # receipts.button_validate()
        # self.action_create_invoice()
        return res

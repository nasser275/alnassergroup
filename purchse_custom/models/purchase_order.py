from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Purchase(models.Model):
    _inherit = 'purchase.order.line'
    code = fields.Char(related="product_id.code", string="Code")
    barcode = fields.Char("Barcode")
    bonous = fields.Float("Bonous")
    main_discount = fields.Float("Main Discount")
    additional_discount = fields.Float("Additional Discount")
    private_discount = fields.Float("Private Discount")
    qty_purchase = fields.Float("purchase Quantity")
    qty_available = fields.Float(related="product_id.qty_available")
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price',copy=False)


    def _prepare_account_move_line(self, move=False):
        res = super(Purchase, self)._prepare_account_move_line(move)

        res.update({'barcode': self.barcode,
                    'bonous': self.bonous,
                    'main_discount': self.main_discount,
                    'additional_discount': self.additional_discount,
                    'private_discount': self.private_discount,
                    'qty_purchase': self.qty_purchase
                    })
        return res

    # @api.depends('product_qty', 'price_unit', 'taxes_id', 'main_discount', 'additional_discount', 'private_discount')
    # def _compute_amount(self):
    #     res = super(Purchase, self)._compute_amount()
    #     subtotal = self.product_qty * self.price_unit
    #     if self.main_discount > 0:
    #         subtotal = subtotal - (subtotal * (self.main_discount / 100))
    #     if self.additional_discount > 0:
    #         subtotal = subtotal - (subtotal * (self.additional_discount / 100))
    #     if self.private_discount > 0:
    #         subtotal = subtotal - (subtotal * (self.private_discount / 100))
    #     self.price_subtotal = subtotal

    @api.onchange("qty_purchase", "bonous")
    def get_total_quantity(self):
        # if self.bonous:
        #     self.product_qty+=self.bonous
        # if self.qty_purchase:
        self.product_qty = self.qty_purchase + self.bonous

    @api.onchange("barcode")
    def get_barcode(self):
        if self.barcode:
            product_id = self.env['product.product'].search([('barcode', '=', self.barcode)], limit=1)
            if product_id:
                self.product_id = product_id



    # @api.depends('product_qty', 'price_unit', 'taxes_id')
    # def _compute_amount(self):
    #     for line in self:
    #         vals = line._prepare_compute_all_values()
    #
    #         taxes = line.taxes_id.compute_all(
    #             vals['price_unit'],
    #             vals['currency'],
    #             vals['quantity'],
    #             vals['product'],
    #             vals['partner'])
    #         line.update({
    #             'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #             'price_total': taxes['total_included'],
    #             'price_subtotal': taxes['total_excluded'],
    #         })

    # def _prepare_compute_all_values(self):
    #     # Hook method to returns the different argument values for the
    #     # compute_all method, due to the fact that discounts mechanism
    #     # is not implemented yet on the purchase orders.
    #     # This method should disappear as soon as this feature is
    #     # also introduced like in the sales module.
    #     self.ensure_one()
    #     return {
    #         'price_unit': self.price_unit,
    #         'currency': self.order_id.currency_id,
    #         'quantity': self.product_qty - self.bonous,
    #         'product': self.product_id,
    #         'partner': self.order_id.partner_id,
    #     }

    # @api.constrains('price_unit')
    # def _onchange_price_unit(self):
    #     """ Warn if the price updated  is more than 0.99 or less than 0.99"""
    #     if self.product_id.seller_ids:
    #         new_price = self.product_id.seller_ids[0].price
    #         print(new_price)
    #         for lines in self:
    #             if (lines.price_unit > (new_price + 0.99)):
    #                 raise ValidationError(_("you can't update the unit price with more than + 0.99  "))
    #             elif (lines.price_unit < (new_price - 0.99)):
    #                 raise ValidationError(_("you can't update the unit price with more than - 0.99 "))
    #             elif (lines.price_unit > (new_price + 0.99) and lines.price_unit < (new_price - 0.99)):
    #                 raise ValidationError(_("you can't update the unit price , you must update with +0.99 or -0.99"))

from odoo import models, fields, api

#_get_price_total_and_subtotal
class Ivoice(models.Model):
    _inherit = 'account.move.line'
    code = fields.Char(related="product_id.code",string="Code")
    barcode = fields.Char("Barcode")
    bonous = fields.Float("Bonous")
    main_discount = fields.Float("Main Discount")
    additional_discount = fields.Float("Additional Discount")
    private_discount = fields.Float("Private Discount")
    qty_purchase = fields.Float("purchase Quantity")
    qty_available = fields.Float(related="product_id.qty_available")



    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):

        res = {}

        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        quantity = quantity - self.bonous
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids',
                  'main_discount','additional_discount','private_discount','qty_purchase','bonous')
    def _onchange_price_subtotal(self):
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_price_total_and_subtotal())
            line.update(line._get_fields_onchange_subtotal())
    # def  write(self, vals):
    #     res = super(Ivoice, self).write(vals)
    #     print(">>>>>>>>>>>>>>>>>>>>>..",res)
    #     return res
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        res = super(Ivoice, self)._get_price_total_and_subtotal()
        subtotal = res['price_subtotal']
        print(">>>>>>>>>>>.", subtotal)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..TOTAL", res['price_total'])
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..TOTAL", self.barcode)
        if self.main_discount > 0:
            subtotal = subtotal - (subtotal * (self.main_discount / 100))
        if self.additional_discount > 0:
            subtotal = subtotal - (subtotal * (self.additional_discount / 100))
        if self.private_discount > 0:
            subtotal = subtotal - (subtotal * (self.private_discount / 100))
        res['price_subtotal'] = subtotal


        return res




    @api.onchange("qty_purchase","bonous")
    def get_total_quantity(self):
        if self.bonous:
            self.quantity+=self.bonous
        if self.qty_purchase:
            self.quantity+=self.qty_purchase
    @api.onchange("barcode")
    def get_barcode(self):
        if self.barcode:
            product_id = self.env['product.product'].search([('barcode','=',self.barcode)],limit=1)
            if product_id:
                self.product_id = product_id

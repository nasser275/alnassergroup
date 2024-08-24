from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    order_source_id = fields.Many2one(comodel_name="pos.order.source", string="Order Source", required=False)
    discount_type = fields.Selection(string="Discount Type",
                                     selection=[('fixed', 'Fixed'), ('percentage', 'Percentage'), ], required=False)
    discount_by = fields.Selection(string="Discount By", selection=[('offer', 'Offer'), ('code', 'Code'), ],
                                   required=False)
    discount_code = fields.Char(string="Discount Code")
    discount_reason_id = fields.Many2one(comodel_name="pos.discount.reasons", string="Pos Discount Application",
                                         required=False)
    discount_offer_id = fields.Many2one(comodel_name="pos.discount.reasons", string="Pos Discount Offer",
                                        required=False)


    def _select(self):
        return super(PosOrderReport, self)._select() + ',s.order_source_id AS order_source_id,' \
                                                       's.discount_type AS discount_type,' \
                                                       's.discount_by AS discount_by,' \
                                                       's.discount_code AS discount_code,' \
                                                       's.discount_reason_id AS discount_reason_id,' \
                                                       's.discount_offer_id AS discount_offer_id'

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ',s.order_source_id,s.discount_type,s.discount_by,s.discount_code,s.discount_reason_id,s.discount_offer_id'\


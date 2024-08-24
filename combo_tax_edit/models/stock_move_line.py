from odoo import models, fields, api


class AlfaReplanishmentInherit(models.Model):
    _inherit = 'alfa.replanishment'

    is_transfer_cal = fields.Boolean('Transfer Computed')


class AlfaReplanishmentLineInherit(models.Model):
    _inherit = 'alfa.replenishment.line'

    product_cost = fields.Float('Cost', related='product.standard_price')


class AlfaReturnReplanishmentLineInherit(models.Model):
    _inherit = 'return.replenishment.line'

    product_cost = fields.Float('Cost', related='product.standard_price')


class StockMoveLineInherit(models.Model):
    _inherit = 'stock.move.line'

    transfer_to_location = fields.Many2one('stock.location', string='Transfer To Location ')
    transfer_from_location = fields.Many2one('stock.location', string='Transfer From Location ')
    transfer_seq = fields.Char('Transfer Sequence')
    ref_to_seq = fields.Char('Stock Ref Sequence')

    def _get_transfer_location(self, reclimit=200):
        for rec in self.env['alfa.replanishment'].sudo().search(
                [('is_transfer_cal', '=', False)], limit=reclimit):
            print('alfa replanishment ID', rec.id)
            if rec.sequence_num or rec.sequence_confirm:
                source_seq = rec.env['stock.picking'].sudo().search(
                    ['|', ('origin', '=', rec.sequence_num), ('origin', '=', rec.sequence_confirm),
                     ('origin', '!=', False)])
                print('source_seq', source_seq)
                for s in source_seq:
                    if s.move_line_ids_without_package:
                        print('move_line_ids_without_package', s.move_line_ids_without_package)
                        for seq in s.move_line_ids_without_package:
                            seq.transfer_to_location = rec.warehouse_to.id
                            seq.transfer_from_location = rec.warehouse_from.id
                            seq.transfer_seq = rec.sequence_num
                            seq.ref_to_seq = s.name
                            print('transfer_to_location', seq.transfer_to_location)
                            print('transfer_from_location', seq.transfer_from_location)
                            print('transfer_seq', seq.transfer_seq)
                            print('ref_to_seq', seq.ref_to_seq)

                rec.is_transfer_cal = True

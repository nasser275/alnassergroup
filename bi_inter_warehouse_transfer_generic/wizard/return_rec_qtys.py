from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ReturnReceivedQty(models.TransientModel):
    _name='received.qty.return.wiz'
    inter_trans_id = fields.Many2one("return.inter.warehouse.transfer", string="Inter Warehouse Transfer", readonly=True)
    lines = fields.One2many(comodel_name="inter.transfer.line.return.wiz", inverse_name="wiz_iwt_id")

    def make(self):
        for line in self.lines:
            line.iwt_line_id.write({'received_qty':line.received_qty});
        self.inter_trans_id.make_received()

    @api.model
    def default_get(self, fields):
        result = super(ReturnReceivedQty, self).default_get(fields)
        lines=[]
        res=self.env['return.inter.warehouse.transfer'].browse(self._context.get('active_ids'))
        for line in res.transfer_lines:
            lines.append((0,0,{
                'product_id':line.product_id.id,
                'qty':line.qty,
                'received_qty':line.received_qty,
                'iwt_line_id':line.id,
            }))
        print("res",lines)
        result['lines']=lines
        return result

class ReturnInterWarehouseTransferLineWiz(models.TransientModel):
	_name = 'inter.transfer.line.return.wiz'
	_rec_name = 'product_id'

	wiz_iwt_id = fields.Many2one('received.qty.return.wiz',readonly=True)
	iwt_line_id = fields.Many2one('return.inter.transfer.line',readonly=True,required=True)
	product_id = fields.Many2one('product.product',string="Product",readonly=True)
	qty = fields.Float("Quantity" ,readonly=True)
	received_qty = fields.Float("Received Quantity" ,default=0)


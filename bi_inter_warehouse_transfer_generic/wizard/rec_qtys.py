from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ReceivedQty(models.TransientModel):
    _name='received.qty.wiz'
    inter_trans_id = fields.Many2one("inter.warehouse.transfer", string="Inter Warehouse Transfer", readonly=True)
    lines = fields.One2many(comodel_name="inter.transfer.line.wiz", inverse_name="wiz_iwt_id")

    def make(self):
        for line in self.lines:
            line.iwt_line_id.write({'received_qty':line.received_qty});
        self.inter_trans_id.make_received()

    @api.model
    def default_get(self, fields):
        result = super(ReceivedQty, self).default_get(fields)
        lines=[]
        res=self.env['inter.warehouse.transfer'].browse(self._context.get('active_ids'))
        for line in res.transfer_lines:
            lines.append((0,0,{
                'product_id':line.product_id.id,
                'qty':line.qty,
                'delivered_qty':line.delivered_qty,
                'received_qty':line.received_qty,
                'iwt_line_id':line.id,
            }))
        print("res",lines)
        result['lines']=lines
        return result

class InterWarehouseTransferLineWiz(models.TransientModel):
	_name = 'inter.transfer.line.wiz'
	_rec_name = 'product_id'

	wiz_iwt_id = fields.Many2one('received.qty.wiz',readonly=True)
	iwt_line_id = fields.Many2one('inter.transfer.line',readonly=True,required=True)
	product_id = fields.Many2one('product.product',string="Product",readonly=True)
	qty = fields.Float("Quantity" ,readonly=True)
	delivered_qty = fields.Float("Delivered Quantity" ,readonly=True)
	received_qty = fields.Float("Received Quantity" ,default=0)


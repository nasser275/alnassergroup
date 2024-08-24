from odoo import models, api, fields, _
from odoo.exceptions import AccessError, UserError, ValidationError


class productreturnreplanishment(models.Model):
    _name = 'return.replanishment'
    _rec_name = 'sequence_num'
    _inherit = ["portal.mixin", "mail.thread",
                "mail.activity.mixin", "utm.mixin"]

    warehouse_from = fields.Many2one('stock.location', string='From', domain="[('usage', '=', 'internal')]",
                                     default=lambda self: self.env['stock.location'].sudo().search(
                                         [('branch_id', '=', self.env.user.branch_id.id)], limit=1),
                                     track_visibility='always')
    warehouse_to = fields.Many2one('stock.location', string='To', domain="[('usage', '=', 'internal')]",
                                   default=lambda self: self.env['stock.warehouse'].sudo().search(
                                       [('is_main_return', '=', True)]).lot_stock_id, track_visibility='always')

    state = fields.Selection(
        [('draft', 'Draft'), ('request', 'Requested'), ('confirm', 'Confirmed'),
         ('cancel', 'Cancel')],
        string='State', default='draft', track_visibility='always')
    provided_products = fields.One2many('return.replenishment.line', 'return_replenishment_id', readonly=False,
                                        ondelete='cascade', track_visibility='always')
    sequence_num = fields.Char(string='Reference Sequence', compute='_get_sequence', store=True,
                               track_visibility='always')
    date_action = fields.Date('Date', required=True
                              , default=fields.Date.today())

    branch_available_to = fields.Boolean(string='Allowed Branches', compute='_get_available_branchto')
    branch_available_from = fields.Boolean(string='Allowed Branches', compute='_get_available_branchfrom')

    sequence_confirm = fields.Char('Sequence Confirm', track_visibility='always')
    reference = fields.Char('Reference', compute='_get_ref', store=True, track_visibility='always')

    def _get_ref(self):
        for rec in self:
            if rec.date_action and rec.warehouse_to and rec.warehouse_from:
                rec.reference = rec.warehouse_from.name + '/' + rec.warehouse_to.name + '/' + str(rec.date_action)

    def _get_available_branchto(self):

        if self.warehouse_to.branch_id.id in self.env.user.branch_ids.ids:
            self.branch_available_to = True
        else:
            self.branch_available_to = False

    def _get_available_branchfrom(self):

        if self.warehouse_from.branch_id.id in self.env.user.branch_ids.ids:
            self.branch_available_from = True
        else:
            self.branch_available_from = False

    @api.model
    def create(self, vals):
        res = super(productreturnreplanishment, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('stock.request')
        res.sequence_num = seq
        product_provide = self.provided_products
        exist_product_list = []
        for p in product_provide:
            if p.product.id in exist_product_list:
                raise ValidationError(_('Product should be one per line.'))
            exist_product_list.append(p.product.id)
        return res

    # def _get_sequence(self):
    #     for rec in self:
    #         if not rec.sequence_num:
    #             seq = self.env['ir.sequence'].next_by_code('return.stock.request')
    #             rec.sequence_num = seq
    #         else:
    #             rec.sequence_num = 'order ' + str(self.id)
    #         print(rec.sequence_num)

    def set_request(self):
        flag = 0
        if not self.sequence_num:
            seq = self.env['ir.sequence'].next_by_code('return.stock.request')
            self.sequence_num = seq

        location_transit = self.env['stock.location'].sudo().search([('is_trans', '=', True)], limit=1)
        print(location_transit.name)

        if not location_transit:
            raise ValidationError(_("""لا يوجد مخزن للنقل 
                                                            """))
        warehouse = self.env['stock.picking.type'].sudo().search(
            [('name', '=', 'Return Replenishment Internal Transfers')])
        # warehouse.warehouse_id = self.warehouse_from.id
        for rec in self.provided_products:
            if rec.requested_qty > rec.available_qty:
                flag += 0
                raise ValidationError(
                    _("The Quantity from '%s' requested not available the available is '%s'", rec.product.name,
                      rec.available_qty))
            else:
                flag = 0
                rec.confirmed_qty = rec.requested_qty
        if flag == 0:
            product_provide = self.provided_products
            qn = self.env['stock.picking'].sudo().create({'partner_id': self.env.user.partner_id.id,
                                                          'picking_type_id': warehouse.id,
                                                          'location_id': self.warehouse_from.id,
                                                          'location_dest_id': location_transit.id,
                                                          'move_type': 'direct',
                                                          'origin': self.sequence_num})
            for p in product_provide:
                if p.requested_qty:
                    qn.move_ids_without_package += qn.move_ids_without_package.sudo().new({
                        'company_id': self.env.user.company_id.id,
                        'date': qn.scheduled_date,
                        'location_dest_id': qn.location_dest_id,
                        'location_id': qn.location_id,
                        'name': qn.name,
                        'product_id': p.product.id,
                        'product_uom_qty': p.requested_qty,
                        'product_uom': p.uom
                    })
            qn.action_confirm()
            check_availabiity = qn.action_assign()

            if check_availabiity:
                check_qn = self.env['stock.picking'].sudo().search([('origin', '=', self.sequence_num)])

                qn.action_set_quantities_to_reservation()
                validated = qn.button_validate()
                if validated and check_qn.state == 'done':

                    # for rec in self.provided_products:
                    #     rec.confirmed_qty = rec.approved_qty
                    self.write(
                        {'state': 'request'})
                else:
                    raise ValidationError(_("""لم يتم تنقيذ الأمر برجاء مراجعة الكميات في حركة المخزن  
                                                                                                            """))

    def set_confirm(self):
        if self.state == 'confirm':
            raise ValidationError("Transfer Confirmed Please Refresh !")
        flag = 0
        location_transit = self.env['stock.location'].sudo().search([('is_trans', '=', True)], limit=1)
        for rec in self.provided_products:
            if rec.confirmed_qty > rec.requested_qty:
                flag += 1
                raise ValidationError(
                    _("The Quantity from '%s' requested not available the available is '%s'", rec.product.name,
                      rec.requested_qty))
            valid_stocks = self.env['stock.quant'].search(
                [('location_id', '=', location_transit.id),
                 ('product_id', '=', rec.product.id)], limit=1)
            if rec.confirmed_qty > valid_stocks.available_quantity:
                flag += 1
                raise ValidationError(
                    _("The Quantity from '%s' Confirmed more than the Available please Contact To System Admin ",
                      rec.product.name))
            else:
                flag = 0
        if flag == 0:
            sequence_next = self.env['ir.sequence'].next_by_code('stock.request')
            warehouse = self.env['stock.picking.type'].sudo().search(
                [('name', '=', 'Return Replenishment Internal Transfers')])

            # warehouse.warehouse_id = self.warehouse_from.id
            product_provide = self.provided_products
            qn = self.env['stock.picking'].sudo().create({'partner_id': self.env.user.partner_id.id,
                                                          'picking_type_id': warehouse.id,
                                                          'location_id': location_transit.id,
                                                          # 'location_dest_id': location_transit.id,
                                                          'location_dest_id': self.warehouse_to.id,
                                                          'move_type': 'direct',
                                                          'origin': sequence_next})
            for p in product_provide:
                if p.confirmed_qty > 0:
                    qn.move_ids_without_package += qn.move_ids_without_package.sudo().new({
                        'company_id': self.env.user.company_id.id,
                        'date': qn.scheduled_date,
                        'location_dest_id': qn.location_dest_id,
                        'location_id': qn.location_id,
                        'name': qn.name,
                        'product_id': p.product.id,
                        'product_uom_qty': p.confirmed_qty,
                        'product_uom': p.uom
                    })
            qn.action_confirm()
            check_availabiity = qn.action_assign()
            if check_availabiity:
                check_qn = self.env['stock.picking'].sudo().search([('origin', '=', sequence_next)])
                # qn = self.env['stock.picking'].sudo().search([('origin', '=', self.sequence_num)])
                wizard = self.env['stock.immediate.transfer'].with_context(
                    dict(self.env.context, default_show_transfers=False,
                         default_pick_ids=[(4, qn.id)])).create({})
                wizard.process()
                validated = qn.with_context(skip_backorder=True).button_validate()
                # self.write(
                #     {'state': 'confirm'})
                # qn.action_set_quantities_to_reservation()
                # validated = qn.sudo().button_validate()
                if validated:
                    # check_qn.sudo().button_validate()
                    self.write(
                        {'state': 'confirm'})
                else:
                    raise ValidationError(_("""لم يتم تنقيذ الأمر برجاء مراجعة الكميات في حركة المخزن  
                                                                                        """))
            else:

                raise ValidationError(_("""الكمية المطلوبة غير متوفرة 
                                                                                       """))

    def set_cancel(self):
        qn = self.env['stock.picking'].sudo().search([('origin', '=', self.sequence_num)])
        qn.action_cancel()
        self.write(
            {'state': 'cancel'})

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'provided_products' not in default:
            default['provided_products'] = [(0, 0, line.copy_data()[0]) for line in
                                            self.provided_products]
        return super(productreturnreplanishment, self).copy_data(default)

    @api.constrains('provided_products')
    def _constrains_bill_ids(self):
        if not self.provided_products or len(self.provided_products) == 0:
            raise ValidationError("You must add at least one Product to the Transfer")

    @api.constrains('provided_products')
    def _check_exist_product_in_line(self):
        for line in self:
            exist_product_list = []
            for p in line.provided_products:
                if p.product.id in exist_product_list:
                    raise ValidationError(_('يجب أن يكون المنتج واحدًا في كل سطر'))
                if p.product.id:
                    exist_product_list.append(p.product.id)


class productreturnreplanishmentlist(models.Model):
    _name = 'return.replenishment.line'
    _inherit = ["portal.mixin", "mail.thread",
                "mail.activity.mixin", "utm.mixin"]

    return_replenishment_id = fields.Many2one('return.replanishment')
    state = fields.Selection(related='return_replenishment_id.state', track_visibility='always')
    product = fields.Many2one('product.product', string='Product', track_visibility='always')
    uom = fields.Many2one(related='product.uom_id', string='Unit of measure')
    product_category = fields.Many2one(related='product.categ_id', string='Product category')
    available_qty = fields.Float(string='Available quantity', compute='_get_available_qty', store=True)
    requested_qty = fields.Float(string='Requested quantity', default=0.0)
    approved_qty = fields.Float(string='Approved quantity', default=0.0, track_visibility='always', copy=False)
    confirmed_qty = fields.Float(string='Confirmed quantity', default=0.0, track_visibility='always', copy=False)
    difference = fields.Float('Diff', compute='_get_diff', store=True)

    _sql_constraints = [('returnorder_product_uniq', 'unique (return_replenishment_id,product)',
                         'Duplicate products in Transfer line not allowed !')]

    @api.depends('approved_qty', 'confirmed_qty')
    def _get_diff(self):
        for rec in self:
            rec.difference = rec.confirmed_qty - rec.approved_qty

    def write(self, vals):
        res = super(productreturnreplanishmentlist, self).write(vals)

        #content = ""
        if vals.get("product") :
            raise ValidationError(_("you can not Change products After Save !"))
        #if vals.get("requested_qty"):
        #    content = content + "  \u2022 Requested: " + str(vals.get("requested_qty")) + "<br/>"

        #self.return_replenishment_id.message_post(body=content)

        return res

    @api.constrains('requested_qty')
    def _check_requested_qty(self):
        for rec in self:
            if rec.requested_qty < 0:
                raise ValidationError(_("you can not request products by negative (-)  !"))
        return True;

    @api.constrains('approved_qty')
    def _check_approved_qty(self):
        for rec in self:
            if rec.approved_qty < 0:
                raise ValidationError(_("you can not aprroved products by negative (-)  !"))
        return True;

    @api.constrains('confirmed_qty')
    def _check_confirmed_qty(self):
        for rec in self:
            if rec.confirmed_qty < 0:
                raise ValidationError(_("you can not confirm products by negative (-)  !"))
        return True;

    @api.depends('product')
    def _get_available_qty(self):
        for rec in self:
            if rec.return_replenishment_id.warehouse_from:
                if not rec.available_qty:
                    valid_stocks = rec.env['stock.quant'].search(
                        [('location_id', 'child_of', rec.return_replenishment_id.warehouse_from.id),
                         ('location_id.usage', '=', 'internal'),
                         ('product_id', '=', rec.product.id)])

                    if valid_stocks.available_quantity > 0:
                        # rec.available_qty = valid_stocks.available_quantity
                        rec.available_qty = valid_stocks.quantity - valid_stocks.reserved_quantity
                    else:
                        rec.available_qty = 0

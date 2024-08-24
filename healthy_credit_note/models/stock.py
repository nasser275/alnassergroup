# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Operation(models.Model):
    _inherit = 'stock.picking.type'

    enable_create_credit_note = fields.Boolean(string="Enable Create Credit Note")
    enable_required_attachment = fields.Boolean(string="Required Attachment")
    credit_note_type = fields.Selection(string="Create Credit Note Type",
                                        selection=[('out_refund', 'Customer Credit Note'),
                                                   ('in_refund', 'Vendor Credit Note'), ], required=False)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False)

    transfer_to_e3melbusiness = fields.Boolean(string="Transfer To E3melbusiness")
    enable_filter_vendors = fields.Boolean(string="Enable Filter Vendors")
    vendor_ids = fields.Many2many(comodel_name="res.partner", relation="stock_venodr", string="Vendors", )
    enable_notes = fields.Boolean(string="Enable Notes")

    disenable_add_lines = fields.Boolean(string="Disenable Add Lines")


class Picking(models.Model):
    _inherit = 'stock.picking'


    @api.onchange('picking_type_id')
    def onchange_picking_type_id_domain(self):
        if self.enable_filter_vendors:
            return {
                'domain': {'partner_id': [('id', '=', self.picking_type_id.vendor_ids.ids)]}
            }
        else:
            return {
                'domain': {'partner_id': []}
            }

    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        check_company=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    enable_required_attachment = fields.Boolean(string="Required Attachment",related='picking_type_id.enable_required_attachment', store=True)
    required_attachment= fields.Binary(string="Required Attachment File",  )
    required_attachment_name= fields.Char(string="Required Attachment File Name",  )
    enable_filter_vendors = fields.Boolean(string="Enable Filter Vendors",related='picking_type_id.enable_filter_vendors', store=True)
    disenable_add_lines = fields.Boolean(string="Disenable Add Lines", related='picking_type_id.disenable_add_lines',
                                         store=True)
    enable_notes = fields.Boolean(string="Enable Create Credit Note",
                                  related='picking_type_id.enable_notes', store=True)
    enable_create_credit_note = fields.Boolean(string="Enable Create Credit Note",
                                               related='picking_type_id.enable_create_credit_note', store=True)
    credit_note_type = fields.Selection(string="Create Credit Note Type",
                                        selection=[('out_refund', 'Customer Credit Note'),
                                                   ('in_refund', 'Vendor Credit Note'), ],
                                        related='picking_type_id.credit_note_type', store=True,
                                        required=False)
    refund_type = fields.Selection(string="Refund Type", selection=[('expird', 'Expird'),
                                                                    ('waset', 'Waset'),
                                                                    ('redistributed', 'Redistributed')
        , ('repacking', 'Repacking'), ('industrial', 'Industrial Defects')], required=False)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False,
                                 related='picking_type_id.journal_id', store=True, )

    credit_note_id = fields.Many2one(comodel_name="account.move", string="Credit Note", copy=False)

    def create_creditnote(self):
        self.make_credit_note()

    def make_credit_note(self):
        if self.sudo().credit_note_id:
            return
            # raise ValidationError("Credit Note Created!")
        lines = []
        for line in self.move_ids_without_package:
            lines.append((0, 0, {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'account_id': line.product_id.categ_id.property_stock_account_input_categ_id.id if self.credit_note_type == 'in_refund' else line.product_id.categ_id.property_stock_account_output_categ_id.id,
                'quantity': line.quantity_done,
                'price_unit': line.product_id.standard_price,
                'product_uom_id': line.product_uom.id,
            }))
        ref = self.env['account.move'].sudo().create({
            'partner_id': self.partner_id.id,
            'ref': self.name,
            'invoice_date': self.scheduled_date.date() if self.scheduled_date else False,
            'refund_type': self.refund_type,
            'move_type': self.credit_note_type,
            'invoice_line_ids': lines,
            'company_id': self.env.user.company_id.id,
            'journal_id': self.journal_id.id,

        })
        self.credit_note_id = ref.id
        self.credit_note_id.action_post()

    def button_validate(self):
        if self.enable_required_attachment:
            if not self.required_attachment:
                raise ValidationError("Add Required Attachment ")
        res = super(Picking, self).button_validate()
        if self.enable_create_credit_note:
            self.make_credit_note()
        return res

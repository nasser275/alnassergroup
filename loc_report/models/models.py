# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime
import xlsxwriter
import base64
import os

class UomReport(models.TransientModel):
    _name = "uom.report.wiz"

    prods = fields.Many2many(comodel_name="product.product", string="Products")
    location_ids = fields.Many2many(comodel_name="stock.location", string="Locations",
                                    domain="[('usage','=','internal')]" )
    report_by_ids = fields.Boolean(string="Report By Ids")

    def print_excel(self):
        self.ensure_one()
        # current_comp = self.env.user.company_id
        wiz_id = self.export_data()
        # self.env.user.company_id=current_comp.id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Download Excel'),
            'res_model': 'excel.download',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }
    def export_data(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        file_name = path + '/temp'
        workbook = xlsxwriter.Workbook(file_name, {'in_memory': True})
        bold1 = workbook.add_format(
            {'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,
             'bg_color': '#FFF58C'})
        bold = workbook.add_format(
            {'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12})
        report_name = "تقرير المخازن"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.write(0, 0, 'Name', bold1)
        sheet.write(0, 1, 'Product Category/Name', bold1)
        sheet.write(0, 2, 'Supplier', bold1)
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 30)
        cloumns = []
        locs = []
        product_lst = []
        domain = [('type', '=', 'product')]
        if self.prods:
            domain.append(('id', 'in', self.prods.ids))

        products = self.env['product.product'].search(domain)
        for product in products:
            temp = {}
            temp['product_id'] = product.id
            temp['product_name'] = product.display_name
            temp['product_categ'] = product.categ_id.name
            temp['product_barcode'] = product.barcode or ""
            temp['product_supplier'] = product.supplier_id.name
            for loc in self.location_ids or self.env['stock.location'].search([('usage','=','internal')]):
                if loc.id not in locs:
                    locs.append(loc.id)
                if 1==1:
                    product_lst.append(product.id)
                    temp[loc.id] = self.get_qty(loc.id, product.id)  or 0
            cloumns.append(temp)

        col=3
        for loc in self.location_ids or self.env['stock.location'].search([('usage','=','internal')]):
            if self.report_by_ids:
                sheet.write(0, col, loc.branch_id.id, bold1)
            else:
                sheet.write(0, col, loc.branch_id.name, bold1)
            sheet.set_column(col,col,20)
            col+=1
        col = 0
        row = 1
        for cloumn in cloumns:
            if cloumn.get('product_id') in product_lst:
                if self.report_by_ids:
                    sheet.write(row, col, cloumn.get('product_id'), bold)
                else:
                    sheet.write(row, col, cloumn.get('product_name'), bold)
                col+=1
                sheet.write(row, col, cloumn.get('product_categ'), bold)
                col += 1
                sheet.write(row, col, cloumn.get('product_supplier'), bold)
                col += 1
                for loc in self.location_ids or self.env['stock.location'].search([('usage','=','internal')]):
                    sheet.write(row, col, cloumn.get(loc.id), bold)
                    col+=1
                col = 0
                row+=1




        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'تقرير المخازن'
        })
        return wiz_id


    def get_qty(self,loc,product_id):
        quant_groups = self.env['stock.quant'].read_group(
                [
                    ('location_id', 'child_of', [loc]),
                    ('product_id', '=', product_id),
                ],
                ['quantity', 'product_id'],
                ['product_id'])
        if quant_groups:
            return quant_groups[0]['quantity']
        else:
            return 0








    def dynamic_view(self):
        cloumns = []
        locs = []
        domain = [('type', '=', 'product')]
        if self.prods:
            domain.append(('id', 'in', self.prods.ids))

        products = self.env['product.product'].search(domain)
        for product in products:
            temp = {}
            temp['product_name'] = product.display_name
            temp['product_barcode'] = product.barcode or ""
            for loc in self.env['stock.location'].search([('id', 'in', self.location_ids.ids)]) or self.env['stock.location'].search([('usage','=','internal')]):
                if loc.name not in locs:
                    locs.append(loc.name)
                temp[loc.name] =  self.get_qty(loc.id,product.id) or 0
            cloumns.append(temp)

        print('cloumns',cloumns)

        return {
            'name': "Unit Of Measure Report",
            'type': 'ir.actions.client',
            'tag': 'uom_report_view',
            'cloumns': cloumns,
            'locs': locs,
        }

    def print_pdf(self):
        data = {'prods': self.prods.ids, 'location_ids': self.location_ids.ids}
        return self.env.ref('loc_report.uom_report_action').report_action(self, data=data, config=False)


class UomReport(models.AbstractModel):
    _name = 'report.loc_report.loc_report'

    def get_qty(self,loc,product_id):
        quant_groups = self.env['stock.quant'].read_group(
                [
                    ('location_id', 'child_of', [loc]),
                    ('product_id', '=', product_id),
                ],
                ['quantity', 'product_id'],
                ['product_id'])
        if quant_groups:
            return quant_groups[0]['quantity']
        else:
            return 0

    @api.model
    def _get_report_values(self, docids, data=None):
        location_ids = data.get('location_ids')
        prods = data.get('prods')
        cloumns = []
        locs = []
        domain = [('type', '=', 'product')]
        if prods:
            domain.append(('id', 'in', prods))

        products = self.env['product.product'].search(domain)
        for product in products:
            temp = {}
            temp['product_name'] = product.display_name
            temp['product_barcode'] = product.barcode
            for loc in self.env['stock.location'].search([('id', 'in', location_ids)]) or self.env[
                'stock.location'].search([('usage','=','internal')]):
                if loc.name not in locs:
                    locs.append(loc.name)
                temp[loc.name] = self.get_qty(loc.id, product.id)  or 0
            cloumns.append(temp)
        docargs = {
            'cloumns': cloumns,
            'locs': locs,
        }


        return docargs

# -*- coding: utf-8 -*-

from odoo import fields, models, _
import xlsxwriter
import base64
import os


class Inventory(models.TransientModel):
    _name = 'healthy.inventory.wiz'
    # company_id = fields.Many2one(comodel_name="res.company", string="الفرع", required=False)
    branch_id = fields.Many2one(comodel_name="res.branch", string="الفرع", required=False)

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
        report_name = "تقرير المبيعات اليومية"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.merge_range('A1:A2', _('Branch Name'), bold1)
        sheet.write(1, 1, _('Price'), bold1)
        sheet.write(1, 2, _('Cost'), bold1)
        sheet.merge_range('B1:C1', "Inventory Valuation", bold1)
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 25)
        sheet.set_column('C:C', 25)

        row = 2

        # lines
        if self.branch_id:
            # self.env.user.company_id = self.company_id.id
            prods = self.env['product.product'].with_context({'branch_id': self.branch_id.id}).search(
                [])
            price = sum(prods.filtered(lambda prod:prod.type=='product' and prod.qty_available!=0).mapped('standard_price'))
            cost = sum(map(lambda prod: prod.lst_price * prod.qty_available, prods.filtered(lambda prod:prod.type=='product' and prod.qty_available!=0)))
            sheet.write(row, 0, self.branch_id.name, bold)
            sheet.write(row, 1, price, bold)
            sheet.write(row, 2, cost, bold)
        else:
            branch_ids = self.env.user.branch_ids
            for branch in branch_ids:
                # self.env.user.branch_id = comp.id
                prods = self.env['product.product'].with_context({'branch_id': branch.id}).search([])
                price = sum(prods.filtered(lambda prod:prod.type=='product' and prod.qty_available!=0).mapped('standard_price'))
                cost = sum(map(lambda prod: prod.lst_price * prod.qty_available, prods.filtered(lambda prod:prod.type=='product' and prod.qty_available!=0)))
                sheet.write(row, 0, branch.name, bold)
                sheet.write(row, 1, cost, bold)
                sheet.write(row, 2, price, bold)
                row += 1

        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'تقرير بأرصدة المخزون بالفروع'
        })
        return wiz_id




class ExcelDownload(models.TransientModel):
    _name = "excel.download"
    _description = "Partners Report Download"

    """file_data Field this is the field which contain the result of Excels function to download
     this data as a file Excel"""
    file_data = fields.Binary('Download report Excel')
    """filename Field this is the field which contain name of Excel file that we will download"""
    filename = fields.Char('Excel File', size=64)

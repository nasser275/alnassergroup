# -*- coding: utf-8 -*-

from odoo import fields, models, _
import xlsxwriter
import base64
import os
from datetime import datetime

class Pricelist(models.TransientModel):
    _name = 'healthy.pricelist.wiz'
    pricelist_id = fields.Many2one(comodel_name="product.pricelist", string="قائمة الأسعار", required=True)

    def print_excel(self):
        self.ensure_one()
        wiz_id = self.export_data()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Download Excel'),
            'res_model': 'excel.download',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': wiz_id.id,
            'target': 'new'
        }

    # journal_user
    def export_data(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        file_name = path + '/temp'
        workbook = xlsxwriter.Workbook(file_name, {'in_memory': True})
        bold1 = workbook.add_format(
            {'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,
             'bg_color': '#FFF58C'})

        bold = workbook.add_format(
            {'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12})
        date_fromat = workbook.add_format(
            {'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12,
             'num_format': 'd-m-yyyy'})

        report_name = "تقرير قائمة الأسعار%s"%self.pricelist_id.name
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.merge_range('A1:I1', _('قائمة أسعار %s'%self.pricelist_id.name), bold1)
        sheet.write(2, 0, _('Product Name'), bold1)
        sheet.write(2, 1, _('Order Date'), bold1)
        sheet.write(2, 2, _('Quantity'), bold1)
        sheet.write(2, 3, _('Original Price'), bold1)
        sheet.write(2, 4, _('Sales Price'), bold1)
        sheet.write(2, 5, _('Cost'), bold1)
        sheet.write(2, 6, _('Total Sales'), bold1)
        sheet.write(2, 7, _('Total Cost'), bold1)
        row = 4
        for item in self.pricelist_id.item_ids:
            lines=[]
            if item.product_tmpl_id.id and item.date_start and item.date_end:
                lines = self.get_lines(item.product_tmpl_id.id, item.date_start, item.date_end)
            if lines:
                date_start=str(datetime.strptime(str(item.date_start),"%Y-%m-%d").date())
                date_end=str(datetime.strptime(str(item.date_end),"%Y-%m-%d").date())
                print(">>",date_start,date_end)
                sheet.merge_range(row, 0, row, 7, item.product_tmpl_id.name+" "+date_start+" "+date_end, bold1)
                row += 1
                # if item.product_tmpl_id.id and item.date_start and item.date_end:
                # lines = self.get_lines(item.product_tmpl_id.id, item.date_start, item.date_end)
                for line in lines:
                    sheet.write(row, 0,  item.product_tmpl_id.name, date_fromat)
                    sheet.write(row, 1, line.get('date_order'), date_fromat)
                    sheet.write(row, 2, line.get('qty'), bold)
                    sheet.write(row, 3, item.price, bold)
                    sheet.write(row, 4, line.get('price_unit'), bold)
                    cost = self.get_cost_from_picking(line.get('product_id'), line.get('picking_id'))
                    sheet.write(row, 5, cost, bold)
                    sheet.write(row, 6, line.get('price_unit') * line.get('qty'), bold)
                    sheet.write(row, 7, cost * line.get('qty'), bold)
                    row += 1
        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'تقرير قائمة الأسعار%s'%self.pricelist_id.name
        })
        return wiz_id

    def get_lines(self, product_tmpl_id, date_start, date_end):
        query = """select pos_order.id,pos_order.picking_id,pos_order_line.product_id,pos_order.date_order,qty,price_unit from pos_order_line 
                join product_product on product_product.id=pos_order_line.product_id
                join product_template on product_template.id=product_product.product_tmpl_id
                join pos_order on pos_order.id=pos_order_line.order_id
                where product_template.id={product_tmpl_id} and pos_order.date_order>=\'{date_start}\' and pos_order.date_order>=\'{date_end}\' and pos_order.company_id={company_id} 
                """.format(product_tmpl_id=product_tmpl_id, date_start=date_start, date_end=date_end,
                           company_id=self.env.user.company_id.id)
        self.env.cr.execute(query)
        lines = self.env.cr.dictfetchall()
        return lines

    def get_cost_from_picking(self, product_id, picking_id):
        cost = 0
        if picking_id:
            query = """select price_unit from stock_move where product_id={product_id} and picking_id={picking_id}""".format(
                product_id=product_id, picking_id=picking_id)
            self.env.cr.execute(query)
            lines = self.env.cr.dictfetchall()
            if lines:
                if lines[0].get('price_unit'):
                    cost = lines[0].get('price_unit')
        return abs(float(cost))

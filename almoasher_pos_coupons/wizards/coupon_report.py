# -*- coding: utf-8 -*-

from odoo import fields, models, _
import xlsxwriter
import base64
import os


class Coupon(models.TransientModel):
    _name = 'pos.coupon.reports'
    coupon_ids = fields.Many2many(comodel_name="pos.coupon", relation="pos_coupon_wiz",string="Coupons")

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

        bold2 = workbook.add_format(
            {'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,
             'bg_color': 'red'})

        bold = workbook.add_format({'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12})
        report_name = "Coupon Report"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 30)
        sheet.write(0, 0, _('Order Ref'), bold1)
        sheet.write(0, 1, _('Order Total'), bold1)
        sheet.write(0, 2, _('Coupon Value'), bold1)
        row=1
        if self.coupon_ids:
            for cop in self.coupon_ids:
                sheet.merge_range(row,0,row,2, _(str(cop.name)), bold2)
                row+=1
                lines=self.get_orders(cop.id)
                for line in lines:
                    sheet.write(row, 0, line.get('name'),  bold)
                    sheet.write(row, 1, line.get('amount_total'),  bold)
                    sheet.write(row, 2, line.get('price_unit'),  bold)
                    row += 1
        else:
            for cop in self.env['pos.coupon'].sudo().search([('used_times','>',0)]):

                sheet.merge_range(row,0,row,2, _(str(cop.name)), bold2)
                row += 1
                lines = self.get_orders(cop.id)
                for line in lines:
                    sheet.write(row, 0, line.get('name'), bold)
                    sheet.write(row, 1, line.get('amount_total'), bold)
                    sheet.write(row, 2, line.get('price_unit'), bold)
                    row += 1



        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'Coupon Report'
        })
        return wiz_id

    def get_orders(self,coupon_id):
        query="""select pos_order.name,pos_order.amount_total,pos_order_line.price_unit from pos_order_line
                    join  pos_order on pos_order.id=pos_order_line.order_id
                    join  product_product on product_product.id=pos_order_line.product_id
                    join  product_template on product_template.id=product_product.product_tmpl_id
                     where coupon_id={coupon_id} and product_template.name='POS-Coupon-Product'""".format(coupon_id=coupon_id)
        self.env.cr.execute(query)
        lines = self.env.cr.dictfetchall()
        return lines













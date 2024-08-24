# -*- coding: utf-8 -*-

from odoo import fields, models, _
import xlsxwriter
import base64
import os
import datetime


class Sales(models.TransientModel):
    _name = 'healthy.sales.wiz'
    date_from = fields.Datetime(string="Date From", required=False)
    date_to = fields.Datetime(string="Date To", required=False)
    # company_id = fields.Many2one(comodel_name="res.company", string="الفرع", required=False)
    branch_id = fields.Many2one(comodel_name="res.branch", string="الفرع", required=False)

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
        report_name = "تقرير المبيعات اليومية"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.write(0, 0, _('Company Name'), bold1)
        sheet.write(0, 1, _('Journal Name'), bold1)
        sheet.write(0, 2, _('Total'), bold1)
        col = 1
        row = 3
        print('Date from B TESTTT', self.date_from)
        print('Date to B TESTTT', self.date_to)

        print('Date from B', datetime.datetime.strptime(str(self.date_from), "%Y-%m-%d %H:%M:%S"))
        print('Date TOT B', datetime.datetime.strptime(str(self.date_to), "%Y-%m-%d %H:%M:%S"))
        datetime_from = datetime.datetime.strptime(str(self.date_from), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
            hours=2,
            minutes=0,
            seconds=0)

        datetime_to = datetime.datetime.strptime(str(self.date_to), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=2,
                                                                                                              minutes=0,
                                                                                                              seconds=0)
        print('Date from', datetime_from)
        print('Date TOT', datetime_to)
        if self.branch_id:
            # sheet.merge_range('A2:B2', _(str(self.company_id.name)), bold1)

            methods = self.env['pos.payment.method'].search(
                [('journal_id.branch_id', '=', self.branch_id.id)])

            for method in methods:
                sheet.write(row, 0, _(str(self.branch_id.name)), bold)
                sheet.write(row, 1, _(str(method.name)), bold)
                sheet.write(row, 2,
                            str(self.get_payment_method_total(method.id, datetime.datetime.strptime(str(self.date_from),
                                                                                                    "%Y-%m-%d %H:%M:%S"),
                                                              datetime.datetime.strptime(str(self.date_to),
                                                                                         "%Y-%m-%d %H:%M:%S"))),
                            bold)
                row += 1

        else:
            row = 2
            for branch in self.env['res.branch'].sudo().search([]):
                methods = self.env['pos.payment.method'].search(
                    [('journal_id.branch_id', '=', branch.id)])
                for method in methods:
                    sheet.write(row, 0, _(str(branch.name)), bold)
                    sheet.write(row, 1, _(str(method.name)), bold)
                    sheet.write(row, 2,
                                str(self.get_payment_method_total(method.id,
                                                                  datetime.datetime.strptime(str(self.date_from),
                                                                                             "%Y-%m-%d %H:%M:%S"),
                                                                  datetime.datetime.strptime(str(self.date_to),
                                                                                             "%Y-%m-%d %H:%M:%S"))),
                                bold)
                    row += 1

        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'تقرير المبيعات اليومية'
        })
        return wiz_id

    def get_payment_method_total(self, payment_method_id, date_from, date_to):
        query = """select  pos_payment.payment_method_id,sum(pos_payment.amount) as total from pos_payment
                          join pos_order on pos_order.id=pos_payment.pos_order_id
                          join pos_session on pos_session.id=pos_order.session_id
                          where pos_payment.payment_method_id ={payment_method_id}  and pos_order.state in ('done','paid','invoiced') 
                          and pos_order.date_order>=\'{date_from}\'  and pos_order.date_order<=\'{date_to}\'
                          group by pos_payment.payment_method_id
                          """.format(payment_method_id=payment_method_id, date_from=date_from, date_to=date_to)
        print("D>DD>", query)
        self.env.cr.execute(query)
        lines = self.env.cr.dictfetchall()
        print("D>DD> Lines", lines)
        amoun = 0.0
        if lines:
            amoun = float(lines[0].get('total'))
        return amoun


class SalesDetails(models.TransientModel):
    _name = 'healthy.sales.details.wiz'
    date_from = fields.Datetime(string="Date From", required=False)
    date_to = fields.Datetime(string="Date To", required=False)
    # company_id = fields.Many2one(comodel_name="res.company", string="الفرع", required=False)
    branch_id = fields.Many2one(comodel_name="res.branch", string="الفرع", required=False)

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
        report_name = "تقرير المبيعات اليومية بالتفصيل"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.write(0, 0, _('Journal Name'), bold1)
        sheet.write(0, 1, _('Total Before Tax'), bold1)
        sheet.write(0, 2, _('Tax amount'), bold1)
        sheet.write(0, 3, _('Total'), bold1)
        col = 1
        row = 3
        print('Date from B TESTTT', self.date_from)
        print('Date to B TESTTT', self.date_to)

        print('Date from B', datetime.datetime.strptime(str(self.date_from), "%Y-%m-%d %H:%M:%S"))
        print('Date TOT B', datetime.datetime.strptime(str(self.date_to), "%Y-%m-%d %H:%M:%S"))
        datetime_from = datetime.datetime.strptime(str(self.date_from), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(
            hours=2,
            minutes=0,
            seconds=0)

        datetime_to = datetime.datetime.strptime(str(self.date_to), "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=2,
                                                                                                              minutes=0,
                                                                                                              seconds=0)
        print('Date from', datetime_from)
        print('Date TOT', datetime_to)
        if self.branch_id:
            # sheet.merge_range('A2:B2', _(str(self.company_id.name)), bold1)

            methods = self.env['pos.payment.method'].search(
                [('journal_id.branch_id', '=', self.branch_id.id)])

            for method in methods:
                # sheet.write(row, 0, _(str(self.branch_id.name)), bold)
                sheet.write(row, 0, _(str(method.name)), bold)

                sheet.write(row, 1,
                            str(self.get_payment_method_total(1, method.id,
                                                              datetime.datetime.strptime(str(self.date_from),
                                                                                         "%Y-%m-%d %H:%M:%S"),
                                                              datetime.datetime.strptime(str(self.date_to),
                                                                                         "%Y-%m-%d %H:%M:%S"))),
                            bold)
                sheet.write(row, 2,
                            str(self.get_payment_method_total(2, method.id,
                                                              datetime.datetime.strptime(str(self.date_from),
                                                                                         "%Y-%m-%d %H:%M:%S"),
                                                              datetime.datetime.strptime(str(self.date_to),
                                                                                         "%Y-%m-%d %H:%M:%S"))),
                            bold)
                sheet.write(row, 3,
                            str(self.get_payment_method_total(3, method.id,
                                                              datetime.datetime.strptime(str(self.date_from),
                                                                                         "%Y-%m-%d %H:%M:%S"),
                                                              datetime.datetime.strptime(str(self.date_to),
                                                                                         "%Y-%m-%d %H:%M:%S"))),
                            bold)
                row += 1

        else:
            row = 2
            for branch in self.env['res.branch'].sudo().search([]):
                methods = self.env['pos.payment.method'].search(
                    [('journal_id.branch_id', '=', branch.id)])
                for method in methods:
                    # sheet.write(row, 0, _(str(branch.name)), bold)
                    sheet.write(row, 0, _(str(method.name)), bold)
                    sheet.write(row, 1,
                                str(self.get_payment_method_total(1, method.id,
                                                                  datetime.datetime.strptime(str(self.date_from),
                                                                                             "%Y-%m-%d %H:%M:%S"),
                                                                  datetime.datetime.strptime(str(self.date_to),
                                                                                             "%Y-%m-%d %H:%M:%S"))),
                                bold)
                    sheet.write(row, 2,
                                str(self.get_payment_method_total(2, method.id,
                                                                  datetime.datetime.strptime(str(self.date_from),
                                                                                             "%Y-%m-%d %H:%M:%S"),
                                                                  datetime.datetime.strptime(str(self.date_to),
                                                                                             "%Y-%m-%d %H:%M:%S"))),
                                bold)
                    sheet.write(row, 3,
                                str(self.get_payment_method_total(3, method.id,
                                                                  datetime.datetime.strptime(str(self.date_from),
                                                                                             "%Y-%m-%d %H:%M:%S"),
                                                                  datetime.datetime.strptime(str(self.date_to),
                                                                                             "%Y-%m-%d %H:%M:%S"))),
                                bold)
                    row += 1

        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'تقرير المبيعات اليومية'
        })
        return wiz_id

    def get_payment_method_total(self, type, payment_method_id, date_from, date_to):
        if type == 1:
            query = """select  pos_payment.payment_method_id,sum(pos_payment.total_without_tax) as total from pos_payment
                              join pos_order on pos_order.id=pos_payment.pos_order_id
                              join pos_session on pos_session.id=pos_order.session_id
                              where pos_payment.payment_method_id ={payment_method_id}  and pos_order.state in ('done','paid','invoiced') 
                              and pos_order.date_order>=\'{date_from}\'  and pos_order.date_order<=\'{date_to}\'
                              and pos_payment.total_without_tax IS NOT NULL
                              group by pos_payment.payment_method_id
                              """.format(payment_method_id=payment_method_id, date_from=date_from, date_to=date_to)

        if type == 2:
            query = """select  pos_payment.payment_method_id,sum(pos_payment.total_tax)
            as total from pos_payment join pos_order on pos_order.id=pos_payment.pos_order_id join pos_session on 
            pos_session.id=pos_order.session_id where pos_payment.payment_method_id ={payment_method_id}  and 
            pos_order.state in ('done','paid','invoiced') and pos_order.date_order>=\'{date_from}\'  and 
            pos_order.date_order<=\'{date_to}\' and pos_payment.total_without_tax IS NOT NULL
                              
                              group by pos_payment.payment_method_id
                              """.format(payment_method_id=payment_method_id, date_from=date_from, date_to=date_to)
        if type == 3:
            query = """select  pos_payment.payment_method_id,sum(pos_payment.amount) as total from pos_payment
                              join pos_order on pos_order.id=pos_payment.pos_order_id
                              join pos_session on pos_session.id=pos_order.session_id
                              where pos_payment.payment_method_id ={payment_method_id}  and pos_order.state in ('done','paid','invoiced') 
                              and pos_order.date_order>=\'{date_from}\'  and pos_order.date_order<=\'{date_to}\' and pos_payment.total_without_tax IS NOT NULL
                              group by pos_payment.payment_method_id
                              """.format(payment_method_id=payment_method_id, date_from=date_from, date_to=date_to)
        print("D>DD>", query)
        self.env.cr.execute(query)
        lines = self.env.cr.dictfetchall()
        print("D>DD> Lines", lines)
        amoun = 0.0
        if lines:
            amoun = round(float(lines[0].get('total')), 2)
        return amoun

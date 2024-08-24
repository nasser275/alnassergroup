# -*- coding: utf-8 -*-

from odoo import fields, models, _
import xlsxwriter
import base64
import os


class balances(models.TransientModel):
    _name = 'healthy.balances.wiz'
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
        report_name = "تقرير بأرصدة خزائن الفروع"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 30)
        sheet.write(0, 0, _('Branch Name'), bold1)
        sheet.write(0, 1, _('Opening Cash Balance'), bold1)
        sheet.write(0, 2, _('Current Cash Balance'), bold1)
        sheet.write(0, 3, _('Sales In This Time In Session'), bold1)
        sheet.write(0, 4, _('Total Cash'), bold1)
        col = 1
        if self.branch_id:
            sheet.write(1, 0, _(str(self.branch_id.name)), bold)
            balance_start, balance_end_real, balance_end, total_sales = self.get_last_cash_statement(self.branch_id.id)
            sheet.write(1, 1, balance_start, bold)
            sheet.write(1, 2, balance_end, bold)
            sheet.write(1, 3, total_sales, bold)
            sheet.write(1, 4, float(balance_end + total_sales), bold)

        else:
            row = 1
            for branch in self.env['res.branch'].sudo().search([]):
                sheet.write(row, 0, _(str(branch.name)), bold)
                balance_start, balance_end_real, balance_end, total_sales = self.get_last_cash_statement(branch.id)
                sheet.write(row, 1, balance_start, bold)
                sheet.write(row, 2, balance_end, bold)
                sheet.write(row, 3, total_sales, bold)
                sheet.write(row, 4, float(balance_end + total_sales), bold)
                row += 1

        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'تقرير بأرصدة خزائن الفروع'
        })
        return wiz_id

    def get_last_cash_statement(self, branch_id):
        balance_start = balance_end_real = balance_end = total_sales = 0
        cash_journal = self.env['account.journal'].sudo().search([('branch_id', '=', branch_id), ('type', '=', 'cash')],
                                                                 limit=1)
        if cash_journal:
            query = """select balance_start,balance_end_real,balance_end,pos_session_id from account_bank_statement 
            where id in( select max (id) from account_bank_statement where  journal_id={journal_id})""".format(
                journal_id=cash_journal.id)
            print(",", query)
            self.env.cr.execute(query)
            lines = self.env.cr.dictfetchall()
            if lines:
                balance_start = lines[0].get('balance_start')
                balance_end_real = lines[0].get('balance_end_real')
                balance_end = lines[0].get('balance_end')
                session_id = lines[0].get('pos_session_id')

                cash_sales_trans = self.env['pos.payment'].sudo().search(
                    [('session_id', '=', int(session_id)), ('payment_method_id.journal_id.type', '=', 'cash')]).mapped(
                    'amount')
                total_sales = sum(cash_sales_trans)

        return balance_start, balance_end_real, balance_end, total_sales

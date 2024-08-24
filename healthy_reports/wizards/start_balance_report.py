# -*- coding: utf-8 -*-

from odoo import fields, models, _
import xlsxwriter
import base64
import os


class StartBalace(models.TransientModel):
    _name = 'healthy.start.balances.wiz'
    # company_ids = fields.Many2many(comodel_name="res.company", relation="start_branchs",  string="Companies",required=True)
    branch_ids = fields.Many2many(comodel_name="res.branch", relation="branch_start",  string="Branchs",required=True)
    date_from = fields.Date(string="Date From", required=False)
    date_to = fields.Date(string="Date To", required=False)
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
        report_name = "تقرير  رصيد اول المدة"
        sheet = workbook.add_worksheet(report_name[:31])
        sheet.right_to_left()
        sheet.set_column('A:A', 30)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 30)
        sheet.set_column('G:G', 30)
        sheet.set_column('H:H', 30)
        sheet.write(0, 0, _('الفرع'), bold1)
        sheet.write(0, 1, _('رصيد الكاش اول المدة'), bold1)
        sheet.write(0, 2, _('المبيعات النقدية خلال فترة التقرير'), bold1)
        sheet.write(0, 3, _('اجمالى الكاش المتاح بالفرع'), bold1)
        sheet.write(0, 4, _('تحويلات للخزينة الرئيسية'), bold1)
        sheet.write(0, 5, _('مصروفات الفرع'), bold1)
        sheet.write(0, 6, _('الرصيد المتاح للتحصيل'), bold1)
        row = 1
        for branch in self.branch_ids:
            sheet.write(row, 0, branch.name, bold)
            start=self.get_sessio_start(branch.id)
            cash=self.sales(branch.id)
            trans,exp=self.get_trasfer_exp(branch.id)
            print("start",cash)
            sheet.write(row, 1, abs(start if start else 0), bold)
            sheet.write(row, 2, abs(cash if cash else 0), bold)
            sheet.write(row, 3, abs(start if start else 0)+abs(cash if cash else 0), bold)
            sheet.write(row, 4, abs(trans if trans else 0), bold)
            sheet.write(row, 5, abs(exp if exp else 0), bold)
            sheet.write(row, 6, abs(start if start else 0)+abs(cash if cash else 0)-abs(trans if trans else 0)-abs(exp if exp else 0), bold)
            row+=1

        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'تقرير  رصيد اول المدة'
        })
        return wiz_id


    def get_sessio_start(self,branch_id):
        session=self.env['pos.session'].sudo().search([('config_id.branch_id','=',branch_id),('start_at','>=',self.date_from),('start_at','<',self.date_to)
                                                ],order='id DESC',limit=1)
        print(">>F",session.id,session.start_at)
        if session:
            balance_start=sum(session.statement_ids.filtered(lambda stat:stat.journal_id.type=='cash').mapped('balance_start'))
            return balance_start
        else:
            return 0


    def get_trasfer_exp(self,branch_id):
        trans=exp=0
        query1="""
        select sum(balance) as total from account_move_line
            join account_move on account_move.id=account_move_line.move_id
            join account_account on account_account.id=account_move_line.account_id
            where account_move.state='posted'  and account_account.is_transfers and account_move.date>=\'{date_from}\'
             and account_move.date<\'{date_to}\' and account_move.branch_id={branch_id}
            group by account_id 
           """.format(branch_id=branch_id,date_from=self.date_from,date_to=self.date_to)
        query2="""
        select sum(balance) as total from account_move_line
            join account_move on account_move.id=account_move_line.move_id
            join account_account on account_account.id=account_move_line.account_id
            where account_move.state='posted'  and account_account.is_expenses and account_move.date>=\'{date_from}\'
             and account_move.date<\'{date_to}\' and account_move.branch_id={branch_id}
            group by account_id 
           """.format(branch_id=branch_id,date_from=self.date_from,date_to=self.date_to)
        self.env.cr.execute(query1)
        lines1 = self.env.cr.dictfetchall()
        self.env.cr.execute(query2)
        lines2 = self.env.cr.dictfetchall()
        if lines1:
            trans = lines1[0].get('total')
        if lines2:
            exp = lines2[0].get('total')
        return trans,exp

    def sales(self,branch_id):
        sales=0
        query="""
            select sum(amount) as amount  from account_bank_statement_line
            join pos_order on pos_order.account_move=account_bank_statement_line.move_id
    join account_journal on account_journal.id=account_bank_statement_line.used_journal
        where date(pos_order.date_order)>='{date_from}' 
        and date(pos_order.date_order)<= '{date_to}'
        and account_bank_statement_line.branch_id={branch_id}
            and account_journal.type='cash'
        """.format(branch_id=branch_id,date_from=self.date_from,date_to=self.date_to)
        self.env.cr.execute(query)
        lines = self.env.cr.dictfetchall()
        if lines:
            sales = lines[0].get('amount')

        return sales
class account_bank_statement_line(models.Model):
    _inherit='account.bank.statement.line'

    used_journal = fields.Many2one(comodel_name="account.journal", related='move_id.journal_id',store=True)

class Account(models.Model):
    _inherit='account.account'
    is_transfers = fields.Boolean(string="تحويلات للخزينة الرئيسية")
    is_expenses = fields.Boolean(string="مصروفات الفرع")

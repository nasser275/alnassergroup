# -*- coding: utf-8 -*-

import base64
import os

import xlsxwriter
from odoo import fields, models, _
from odoo.exceptions import ValidationError




class Tool(models.TransientModel):
    _name = 'healthy.survey.tool'

    customers = fields.Integer(string="Customers", required=True)
    date_from = fields.Date(string="Date From", required=False)
    date_to = fields.Date(string="Date To", required=False)
    show_products = fields.Boolean(string="Show Products")
    order_platforms = fields.One2many(comodel_name="healthy.survey.tool.line", inverse_name="tool_id")
    except_products = fields.Many2many(comodel_name="product.product", relation="tools_prods",  string="Except Products")

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

    def export_data(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        file_name = path + '/temp'
        workbook = xlsxwriter.Workbook(file_name, {'in_memory': True})
        bold1 = workbook.add_format(
            {'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 14,
             'bg_color': '#FFF58C'})

        bold = workbook.add_format({'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12})
        bold_color = workbook.add_format({'bold': True, 'locked': True, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_size': 12,'bg_color':'#E0FFFF'})
        date_format = workbook.add_format({'border': True, 'align': 'center', 'valign': 'vcenter', 'num_format': 'd-m-yyyy'})
        date_format_color = workbook.add_format({'border': True, 'align': 'center', 'valign': 'vcenter', 'num_format': 'd-m-yyyy','bg_color':'#E0FFFF'})
        report_name = "H&T Survey Data Tool"
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
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        if self.show_products:
            sheet.write(0, 0, _('Product Name'), bold1)
        sheet.write(0, 1, _('Customer Id'), bold1)
        sheet.write(0, 2, _('Customer Name'), bold1)
        sheet.write(0, 3, _('Customer Phone'), bold1)
        sheet.write(0, 4, _('Store'), bold1)
        sheet.write(0, 5, _('Order Source'), bold1)
        sheet.write(0, 6, _('Order Date'), bold1)
        sheet.write(0, 7, _('Delivery time'), bold1)
        sheet.write(0, 8, _('Number of Orders'), bold1)
        sheet.write(0, 9, _('First order date'), bold1)
        sheet.write(0, 10, _('Last order date'), bold1)

        # Data
        if self.customers > 0:
            branchs = self.env['res.branch'].sudo().search([])
            row = 1
            for branch in branchs:
                query4 = ""
                order_source_limit = int(self.get_customers_limit_for_company())
                for source in self.order_platforms:
                    order_source_limit-=int(order_source_limit * ( source.percentage / 100))
                    query3 = self.order_source_query(branch.id,source.is_new,source.lines or 1, source.order_source_id.id,order_source_limit)
                    query4 += """({query3})""".format(query3=query3)
                    if source.id!=self.order_platforms[-1].id:
                        query4+=" union "

                query5 = query4
                if not query5:
                    raise ValidationError("Add Order Source!")

                print(">>",query5)


                self.env.cr.execute(query5)
                lines = self.env.cr.dictfetchall()

                if self.show_products==False:
                    date_format_color=date_format
                    bold_color=bold
                for line in lines:
                    sheet.write(row, 1, line.get('customer_id'), bold_color)
                    sheet.write(row, 2, line.get('customer_name'), bold_color)
                    sheet.write(row, 3, line.get('customer_phone'), bold_color)
                    sheet.write(row, 4,self.env['res.branch'].browse(int(line.get('branch_id'))).name, bold_color)
                    sheet.write(row, 5,self.env['pos.order.source'].browse(int(line.get('order_source'))).name, bold_color)
                    sheet.write(row, 6, line.get('date_order'), date_format_color)
                    sheet.write(row, 7, self.get_count_order(line.get('customer_id')), bold_color)
                    order = self.env['pos.order'].sudo().browse(line.get('order_id'))
                    # if order.is_first_order:
                    #     sheet.write(row, 8, line.get('date_order'), date_format_color)
                    # else:
                    #     sheet.write(row, 8, "", bold)
                    sheet.write(row, 8, self.get_last_order(line.get('customer_id')), date_format_color)
                    row += 1
                    if self.show_products:
                        for product in order.lines:
                            sheet.write(row, 0, product.product_id.name, bold)
                            row += 1
                # row += 1


        workbook.close()
        with open(file_name, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        data_file = file_base64

        wiz_id = self.env['excel.download'].create({
            'file_data': data_file,
            'filename': 'H&T Survey Data Tool'
        })
        return wiz_id

    def where_st(self):
        st = "pos_order.state in ('paid', 'done', 'invoiced')"
        if self.date_from:
            st += """ and pos_order.date_order>=\'{date_from}\'""".format(date_from=self.date_from)
        if self.date_to:
            st += """ and pos_order.date_order<=\'{date_to}\'""".format(date_to=self.date_to)
        if self.except_products:
            if len(self.except_products)==1:
                st += """ and pos_order_line.product_id!={except_products}""".format(except_products=self.except_products[0].id)
            else:
                st += """ and pos_order_line.product_id not in {except_products}""".format(
                    except_products=tuple(self.except_products.ids))
        return st
    def where_st2(self):
        st = "pos_order.state in ('paid', 'done', 'invoiced')"
        if self.date_from:
            st += """ and pos_order.date_order>=\'{date_from}\'""".format(date_from=self.date_from)
        if self.date_to:
            st += """ and pos_order.date_order<=\'{date_to}\'""".format(date_to=self.date_to)

        return st

    def get_base_query(self, lines,where_st, limit=0):
        query = """
        select DISTINCT
         pos_order.id as order_id,
         COUNT(pos_order_line.id) AS lines,
         pos_order.partner_id as customer_id,
         res_partner.name as customer_name,
         res_partner.phone as customer_phone,
         res_company.name as store,
         pos_order.branch_id as branch_id,
         pos_order.order_source_id as order_source,
         pos_order.date_order as date_order
         from pos_order 
        join res_partner on res_partner.id=pos_order.partner_id
        join res_company on res_company.id=pos_order.company_id
        join pos_order_line on pos_order_line.order_id=pos_order.id
        where {where_st}
        GROUP BY pos_order.id ,pos_order.partner_id ,
         res_partner.name ,
         res_partner.phone ,
         res_company.name ,
         pos_order.order_source_id ,
         pos_order.date_order 
          HAVING COUNT(pos_order_line.id)={lines}
        limit {limit}
        """.format(where_st=where_st, limit=limit,lines=lines)
        print(">>",query)
        return query


    def order_source_query(self, branch_id, new,lines,order_source, order_source_limit):
        where_st = self.where_st()
        if new:
            where_st += " and pos_order.order_source_id=\'%s' and pos_order.branch_id=%s " % (order_source, branch_id)
        else:
            where_st += " and pos_order.order_source_id=\'%s' and pos_order.branch_id=%s " % (order_source, branch_id)
        query = self.get_base_query(lines,where_st, limit=order_source_limit or 0)
        return query

    def get_customers_limit_for_company(self):
        comps = self.env['res.company'].sudo().search_count([])
        comp_limit = self.customers / comps
        return comp_limit

    def get_count_order(self, customer_id):
        where_st = self.where_st2()
        where_st += """and partner_id ={partner_id}""".format(partner_id=customer_id)
        query = """select partner_id, count(id) as count_order from pos_order 
        where {where}
        group by partner_id
        """.format(where=where_st)
        print(">>D",query)
        self.env.cr.execute(query)
        count_order = 0
        lines = self.env.cr.dictfetchall()
        if lines:
            count_order = lines[0].get('count_order')
        return count_order

    def get_last_order(self, customer_id):
        where_st = self.where_st2()
        where_st += """and partner_id ={partner_id}""".format(partner_id=customer_id)
        query = """select date_order from pos_order
           where {where}
           order by id desc
           """.format(where=where_st)
        self.env.cr.execute(query)
        last_order = ""
        lines = self.env.cr.dictfetchall()
        if lines:
            last_order = lines[-1].get('date_order')
        return last_order


class ToolLine(models.TransientModel):
    _name = 'healthy.survey.tool.line'
    order_source_id = fields.Many2one(comodel_name="pos.order.source", string="Order Source", required=False)
    percentage = fields.Integer(string="Percentage", required=False)
    is_new = fields.Boolean(string="Is Customer New?")
    lines = fields.Integer(string="No Of Lines", required=False)
    tool_id = fields.Many2one(comodel_name="healthy.survey.tool")

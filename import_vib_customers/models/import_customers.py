# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.mimetypes import guess_mimetype
from itertools import islice
import base64
import os
from odoo.tools.mimetypes import guess_mimetype
import base64
from itertools import islice
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import datetime
try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

path = os.path.join(os.path.dirname(os.path.abspath(__file__)))

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

try:
    from . import odf_ods_reader
except ImportError:
    odf_ods_reader = None

FILE_TYPE_DICT = {
    'text/csv': ('csv', True, None),
    'application/vnd.ms-excel': ('xls', xlrd, 'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ('xlsx', xlsx, 'xlrd >= 1.0.0'),
    'application/vnd.oasis.opendocument.spreadsheet': ('ods', odf_ods_reader, 'odfpy')
}
EXTENSIONS = {
    '.' + ext: handler
    for mime, (ext, handler, req) in FILE_TYPE_DICT.items()
}


class Import(models.Model):
    _name = "import.customers"
    _rec_name='file_name'

    _inherit = ["base_import.import", 'mail.thread']
    supported_formats = ['xlsx', 'xls']
    data = {"sheet": [], "logs": []}
    file = fields.Binary(string='select %s file' % supported_formats)
    file_name = fields.Char('File Name')
    file_type = fields.Char('File Type')
    trash_btn = fields.Boolean(string="Trash")
    is_vib = fields.Boolean(string="IS VIB")
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('imported', 'Imported'), ], required=False,default='draft')


    def import_excel(self):
        self.ensure_one()
        self.data['sheet'] = []
        if self.file:
            file_content = base64.b64decode(self.file)
            mimetype = guess_mimetype(file_content)
            (file_extension, handler, req) = FILE_TYPE_DICT.get(
                mimetype, (None, None, None))
            if not file_extension in self.supported_formats:
                raise UserError(_("Unsupported format, please upload file in '{0}'".format(
                    self.supported_formats)))
            book = xlrd.open_workbook(file_contents=file_content)
            sheets = book.sheet_names()
            values = self._read_xls_book(book,sheets[0])
            header_list = []
            i = 0
            for sheet in book.sheets():
                for rownum in range(sheet.nrows):
                    if rownum == 0:
                        header_list = sheet.row_values(rownum)
                values = self._read_xls_book2(book, i)
                self.mapping_data(values, header_list)
                i += 1
            self.mapping_data(values, header_list)

    def mapping_data(self, content, header_list):
        company_id=self.env['res.company'].search([('name','=','Healthy&Tasty')],limit=1).id
        print("company_id",company_id)
        if content:
            rows = enumerate(islice(content, 1, None))
            lines = []
            if rows:
                for index, row in rows:
                    print(">>",row)
                    customer_name = row[header_list.index('Customer/Name')],
                    customer_phone = row[header_list.index('Customer/Phone')]
                    lines.append({
                        'name': customer_name[0],
                        'phone': customer_phone,
                    })


            for line in lines:
                if line.get('phone'):
                    res=self.env['res.partner'].sudo().search([('phone','=',line.get('phone')),
                                                               ('customer','=',True)

                                                               ])
                    if res:
                        for partner in res:
                            partner.sudo().write({'is_vib':self.is_vib,'company_id':company_id})
                    else:
                        print("created", line.get('phone'))
                        line['is_vib']=self.is_vib
                        line['company_id']=company_id
                        self.env['res.partner'].sudo().create(line)
        self.state='imported'


    def _read_xls_book2(self, book,sheet_index):
        sheet = book.sheet_by_index(sheet_index)
        # emulate Sheet.get_rows for pre-0.9.4
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value)
                        if is_float
                        else str(int(cell.value))
                    )
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        if is_datetime
                        else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    )
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s") % {
                            'row': rowx,
                            'col': colx,
                            'cell_value': xlrd.error_text_from_code.get(cell.value, _("unknown error code %s") % cell.value)
                        }
                    )
                else:
                    values.append(cell.value)
            if any(x for x in values if x.strip()):
                yield values





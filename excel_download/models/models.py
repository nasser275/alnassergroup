# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ExcelDownload(models.TransientModel):
    _name = "excel.download"
    _description = "Partners Report Download"

    """file_data Field this is the field which contain the result of Excels function to download
     this data as a file Excel"""
    file_data = fields.Binary('Download report Excel')
    """filename Field this is the field which contain name of Excel file that we will download"""
    filename = fields.Char('Excel File', size=64)

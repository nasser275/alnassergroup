# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class SearchDateRange(models.Model):

    _name = "search.date.range"
    _description = "Date Range"
    _rec_name = "label"
    _order = "sequence"

    sequence = fields.Integer()
    label = fields.Char(translate=True, required=True)
    domain2 = fields.Text(required=True)

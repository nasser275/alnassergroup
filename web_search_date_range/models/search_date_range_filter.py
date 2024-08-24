# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SearchDateRangeFilter(models.Model):

    _name = "search.date.range.filter"
    _description = "Date Filter"
    _order = "model_id, field_id"

    view_id = fields.Many2one("ir.ui.view", "View", )
    inherit_view_id = fields.Many2one("ir.ui.view", "Inherited View", )
    model_id = fields.Many2one("ir.model", "Model", ondelete="cascade", required=True)
    field_id = fields.Many2one(
        "ir.model.fields",
        "Field",
        ondelete="cascade",
        required=True,
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['date', 'datetime'])]",
    )
    range_id = fields.Many2one(
        "search.date.range",
        string="Date Range",
        required=True,
    )

    @api.onchange("model_id")
    def _onchange_model_id_empty_field_id(self):
        self.field_id = None

    def create_filter(self):
        domain=str(self.range_id.domain2)
        domain=domain.replace('&','&amp;')
        domain=domain.replace('>','&gt;')
        domain=domain.replace('<','&lt;')
        domain=domain.replace('field',"\'"+self.field_id.name+"\'")
        arch_base = """<?xml version="1.0"?>
                                        <data>
                                            <xpath expr="//search" position="inside">
                                            <filter string="{label}" name="{name}" domain="{domain}"/>


    </xpath>
                                        </data>
                                    """.format(label=self.range_id.label, domain=domain,
                                               name=str(self.range_id.label).lower().replace(" ", "_"))
        print("DD<D<D",arch_base)
        self.inherit_view_id = self.env['ir.ui.view'].create(
            {'name': "inherit.board_my_dash_view__%s" % (self.id),
             'type': 'search',
             'model': self.model_id.model,
             'mode': 'extension',
             'inherit_id': self.view_id.id,
             'arch_base': arch_base,
             'active': True})


    def delete_filter(self):
            self.inherit_view_id.unlink()


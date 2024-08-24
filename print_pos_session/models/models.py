# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Report(models.AbstractModel):
    _name = 'report.print_pos_session.pos_session_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        session_data={}
        if data.get('session_id'):
            session=self.env['pos.session'].browse(int(data.get('session_id')))
            if session:
                session_data=session.get_closing_control_data()
                print("DD>",session_data)
        docargs = {
            'session_data':session_data
        }
        return docargs





class PosOrder(models.Model):
    _inherit = 'pos.session'


    @api.model
    def print_pdf(self, session_id=False):
        if session_id:
            data={
                'session_id': session_id,
            }

            return self.env.ref('print_pos_session.session_report_action').report_action(self, data=data, config=False)

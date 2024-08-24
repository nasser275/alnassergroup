from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    api_token = fields.Char(string="API Token", required=False)
    category_fields = fields.Char(string='Category Fields')
    product_fields = fields.Char(string='Product Fields')
    branch_fields = fields.Char(string='Branch Fields')
    product_search_fields = fields.Char(string='Product Search Fields')
    order_fields = fields.Char(string='Order Fields')
    order_line_fields = fields.Char(string='Order Line Fields')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        with_user = self.env['ir.config_parameter'].sudo()
        with_user.set_param('healthy_tasty_api.api_token', self.api_token)
        with_user.set_param('healthy_tasty_api.category_fields', self.category_fields)
        with_user.set_param('healthy_tasty_api.product_fields', self.product_fields)
        with_user.set_param('healthy_tasty_api.product_search_fields', self.product_search_fields)
        with_user.set_param('healthy_tasty_api.branch_fields', self.branch_fields)
        with_user.set_param('healthy_tasty_api.order_fields', self.order_fields)
        with_user.set_param('healthy_tasty_api.order_line_fields', self.order_line_fields)
        return res

    @api.model
    def get_values(self):
        values = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        values['api_token'] = with_user.get_param('healthy_tasty_api.api_token')
        values['category_fields'] = with_user.get_param('healthy_tasty_api.category_fields')
        values['product_fields'] = with_user.get_param('healthy_tasty_api.product_fields')
        values['product_search_fields'] = with_user.get_param('healthy_tasty_api.product_search_fields')
        values['branch_fields'] = with_user.get_param('healthy_tasty_api.branch_fields')
        values['order_fields'] = with_user.get_param('healthy_tasty_api.order_fields')
        values['order_line_fields'] = with_user.get_param('healthy_tasty_api.order_line_fields')
        return values

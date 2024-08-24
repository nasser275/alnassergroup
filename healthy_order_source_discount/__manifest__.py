# -*- coding: utf-8 -*-
{
    'name': "healthy_order_source",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale','ks_pos_low_stock_alert'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/pos.xml',
        'views/pos_config.xml',
        'views/discount_reasons.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'healthy_order_source_discount/static/src/js/order_source_button.js',
            # 'healthy_order_source_discount/static/src/js/order_source_pop.js',
            'healthy_order_source_discount/static/src/js/models.js',
            'healthy_order_source_discount/static/src/js/payment.js',
            'healthy_order_source_discount/static/src/js/discount_button.js',
            'healthy_order_source_discount/static/src/js/fixeddiscount_button.js',
            'healthy_order_source_discount/static/src/js/precdiscount_button.js',
            'healthy_order_source_discount/static/src/js/discount_pop.js',
            'healthy_order_source_discount/static/src/js/TicketScreen.js',
        ],
        'web.assets_qweb': [
            'healthy_order_source_discount/static/src/xml/pos.xml',
        ],
    },

}

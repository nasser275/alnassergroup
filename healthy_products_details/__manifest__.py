# -*- coding: utf-8 -*-
{
    'name': "healthy_products_details",

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
    'depends': ['base','product','is_customer_is_vendor','point_of_sale','stock','purchase'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/purchase.xml',
        'views/stock.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'healthy_products_details/static/src/js/info.js',

        ],
        'web.assets_qweb': [
            'healthy_products_details/static/src/xml/**/*',
        ],
    },

}

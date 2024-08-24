# -*- coding: utf-8 -*-
{
    'name': "healthy_app_orders",

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
    'depends': ['base','point_of_sale','healthy_order_source_discount'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/app_orders.xml',
        'views/pos_order.xml',
        'views/app_order_report.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'healthy_app_orders/static/src/css/pos.css',
            # 'healthy_app_orders/static/src/js/apporder.js',
            'healthy_app_orders/static/src/js/models.js',
            # 'healthy_app_orders/static/src/js/order_list_screen.js',
            # 'healthy_app_orders/static/src/js/schedule_app_orders_button.js',
            'healthy_app_orders/static/src/js/schedule_app_orders_pop.js',
            'healthy_app_orders/static/src/css/pos_sale.css',
            'healthy_app_orders/static/src/js/SetAppOrderButton.js',
            'healthy_app_orders/static/src/js/OrderManagementScreen/MobileAppOrderManagementScreen.js',
            'healthy_app_orders/static/src/js/OrderManagementScreen/AppOrderFetcher.js',
            'healthy_app_orders/static/src/js/OrderManagementScreen/AppOrderList.js',
            'healthy_app_orders/static/src/js/OrderManagementScreen/AppOrderManagementControlPanel.js',
            'healthy_app_orders/static/src/js/OrderManagementScreen/AppOrderManagementScreen.js',
            'healthy_app_orders/static/src/js/OrderManagementScreen/AppOrderRow.js',
        ],
        'web.assets_qweb': [
            'healthy_app_orders/static/src/xml/**/*',
        ],
    },

}

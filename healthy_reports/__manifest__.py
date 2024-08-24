# -*- coding: utf-8 -*-
{
    'name': "healthy_reports",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','purchase_stock','stock','point_of_sale','account','sale','excel_download','branch'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'wizards/balances.xml',
        'wizards/pricelist.xml',
        'wizards/start_balance.xml',
        'wizards/healthy_inventory.xml',
        'wizards/healthy_sales.xml',
        'views/account_account.xml',
        'views/views.xml',
    ],

}
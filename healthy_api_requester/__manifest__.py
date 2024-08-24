# -*- coding: utf-8 -*-
{
    'name': "Healthy API Requester",

    'summary': """
        This module listens to some actions on ERP and sends HTTP request according to them.
        """,

    'description': """
        This module listens to some actions on ERP and sends HTTP request according to them.
    """,

    'author': "Salem Hassan",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','healthy_app_orders','point_of_sale','purchase','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
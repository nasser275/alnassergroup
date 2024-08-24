# -*- coding: utf-8 -*-
{
    'name': "healthy_survey_tool",

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
    'depends': ['base','healthy_order_source_discount','point_of_sale','excel_download','branch'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizards/survey.xml',
    ],

}
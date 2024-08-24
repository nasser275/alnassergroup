# -*- coding: utf-8 -*-
{
    'name': "POS Loyalty : exclude customer",

    'summary': """
        Exclude a customer from loyalty programs
        """,
    'description': """

    This module allows you to exclude a customer from loyalty programs.

    """,

    'author': "Phidias",
    'website': "http://www.phidias.fr",
    'images': ['static/description/icon.png'],
    'category': 'Sales/Point Of Sale',
    'version': '13.0.0.1',
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,

    'depends': [
        'pos_loyalty',
        'branch',
    ],

    'data': [
        'views/partner.xml',
        # 'views/assets.xml',
    ],
'assets': {
        'point_of_sale.assets': [
            'phi_pos_loyalty_exclude_customer/static/src/js/loyalty.js',


        ],

    },
}

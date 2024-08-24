# -*- coding: utf-8 -*-
{
    'name': "pos_service_fees",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_config.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_service_fees/static/src/js/pos.js',
        ],
    },

}

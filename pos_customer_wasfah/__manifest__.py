# -*- coding: utf-8 -*-
{
    'name': "pos_customer_wasfah",
    'depends': ['base','point_of_sale'],
    'data': [
        'views/views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_customer_wasfah/static/src/js/models.js',
        ],
        'web.assets_qweb': [
            'pos_customer_wasfah/static/src/xml/**/*',
        ],
    },

}

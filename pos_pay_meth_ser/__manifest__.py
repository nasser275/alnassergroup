# -*- coding: utf-8 -*-
{
    'name': "pos_pay_meth_ser",

    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
'assets': {
        'point_of_sale.assets': [
            'pos_pay_meth_ser/static/src/js/pay.js',
            'pos_pay_meth_ser/static/src/js/models.js',
        ],
'web.assets_qweb': [
            'pos_pay_meth_ser/static/src/xml/pos.xml',
        ],

    },

}

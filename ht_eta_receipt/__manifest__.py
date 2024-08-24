# -*- coding: utf-8 -*-
{
    'name': "ht_eta_receipt",
    'depends': ['base', 'point_of_sale', 'l10n_eg_edi_eta'],

    'data': [
        'views/pos_config.xml',
        'views/pos_order_view_changes.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'ht_eta_receipt/static/src/js/pos_order.js',
            'ht_eta_receipt/static/src/js/models.js',
            'ht_eta_receipt/static/src/js//qrcode.js'
        ],
        'web.assets_qweb': [
            'ht_eta_receipt/static/src/xml/pos.xml',
        ],

    }

}

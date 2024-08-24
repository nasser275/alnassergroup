# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'POS Combo',
    'category': 'Point of Sale',
    'summary': 'This module allows user to use combo feature in restaurant.',
    'description': """
This module allows user to use combo feature in restaurant
""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 10, 
    'currency': 'EUR',
    'version': '1.0.2',
    'depends': ['base', 'pos_restaurant','branch'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/point_of_sale.xml',
        # 'views/aspl_pos_combo.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'aspl_pos_combo/static/src/css/pos.css',
            'aspl_pos_combo/static/src/js/models.js',
            'aspl_pos_combo/static/src/js/OrderWidgetExtended.js',
            'aspl_pos_combo/static/src/js/combo.js',
            'aspl_pos_combo/static/src/js/orderdetails.js',
            'aspl_pos_combo/static/src/js/Ticket.js',
            'aspl_pos_combo/static/src/js/payment.js',
        ],
        'web.assets_qweb': [
            'aspl_pos_combo/static/src/xml/pos.xml',
        ],
    },

    # 'qweb': ['static/src/xml/pos.xml'],
}

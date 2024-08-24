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
    'name': 'POS Promotion (Community)',
    'category': 'Point of Sale',
    'summary': "Point of Sale Promotion",
    'description': """
User needs to create the promotion according to promotion, rules will be apply in POS.
""",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'depends': ['web', 'point_of_sale', 'sale_stock', 'branch', 'healthy_order_source_discount'],
    'price': 45.0,
    'currency': 'EUR',
    'version': '1.0.2',
    'images': ['static/description/main_screenshot.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_promotion_view.xml',
        'views/product.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'aspl_pos_promotion/static/src/js/models.js',
            'aspl_pos_promotion/static/src/js/Screens/ProductScreen/ProductScreen.js',
            'aspl_pos_promotion/static/src/js/promotion_button.js',
            'aspl_pos_promotion/static/src/js/promotion_popup.js',
        ],
        'web.assets_qweb': [
            'aspl_pos_promotion/static/src/xml/promotion.xml',
            'aspl_pos_promotion/static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
        ],
    },

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

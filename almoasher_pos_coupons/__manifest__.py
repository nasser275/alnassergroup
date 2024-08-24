# -*- coding: utf-8 -*-
{
    'name': 'Almoasher Coupons in Point of Sale',
    'version': '12.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Manage Point of Sale Vouchers & Coupon Codes',
    'author': 'Salem Hassan',
    'website': "http://www.almoasherbiz.com",
    'company': 'Almoasher',
    # i only depend on healthy_features just to add show_coupon field only to use it on pos and
    # the reason [there are some fields and page already declared there i dont need to re create a new page for one field]
    'depends': ['point_of_sale', 'excel_download'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'views/pos_voucher.xml',
        'views/pos_coupon.xml',
        'views/pos_order.xml',
        'views/pos_config.xml',
        'wizards/coupon_report.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'point_of_sale.assets': [
            'almoasher_pos_coupons/static/src/css/pos.css',
            'almoasher_pos_coupons/static/src/js/coupons_button.js',
            'almoasher_pos_coupons/static/src/js/coupons_popup.js',
            'almoasher_pos_coupons/static/src/js/models.js',

        ],
        'web.assets_qweb': [
            'almoasher_pos_coupons/static/src/xml/coupons.xml',
        ],
    },
}

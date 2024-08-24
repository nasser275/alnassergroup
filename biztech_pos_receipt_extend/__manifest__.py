
{
    'name': "Advanced POS Receipt",
    "description": """Advanced POS Receipt with Customer Details and Invoice Details""",
    "summary": "Advanced POS Receipt with Customer Details and Invoice Details",
    "category": "Point of Sale",
    "version": "15.0.1.0.0",
    'author': 'Biztech Computer',
    'maintainer': 'Biztech Computer',
    'website': 'https://biztechbh.biz',
    'depends': ['point_of_sale', 'sale', 'account'],
    'data': [
        'views/res_config_settings.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'biztech_pos_receipt_extend/static/src/xml/OrderReceipt.xml',
            'biztech_pos_receipt_extend/static/src/js/pos_order_receipt.js',
            'biztech_pos_receipt_extend/static/src/js/payment.js',
        ]
    },
    'images': ['static/description/icon.png' ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}

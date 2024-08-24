# -*- coding: utf-8 -*-
{
    'name': "alfa",
    'author': "Ebrahiem",
    'category': 'Customizations',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['branch', 'stock', 'point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/vw_warehouse.xml',
        'views/vw_stock_move.xml',
        'views/account_payment.xml',
        'views/pos_config_view.xml',
        'views/replanishment.xml',
        'views/return_replanishment.xml',
        'report/delivery_payslip.xml',
        'report/deivery_return_payslip.xml',
        'report/warchouse_deliverslip.xml',
        'report/transfer_report.xml',
        'report/return_report.xml',
        # 'views/pos_assets.xml',
        'demo/demo.xml',
        'views/custom_pos_config_view.xml',
        # 'views/vw_account_move_line_cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    # 'qweb': [
    #          'static/src/xml/Screens/PaymentScreen/PaymentScreen.xml',
    #          'static/src/xml/Chrome.xml',
    #          'static/src/xml/Screens/ChromeWidgets/SaleOrderMode.xml',
    #          'static/src/xml/Screens/InvoiceScreen/InvoiceScreen.xml',
    #          'static/src/xml/Screens/InvoiceScreen/InvoiceLine.xml',
    #          'static/src/xml/Popups/PopupProductLines.xml',
    #          'static/src/xml/alfa_pos_stock.xml',
    #          ],
    'application': True,
    "installable": True,
    "auto_install": False,
}

# -*- coding: utf-8 -*-
{
    'name': "Credit Card Payment Commissions",

    'summary': """
        Accounting, Payment, Journal, Commission
    """,

    'author': "Abdulrahman Warda",

    'category': 'Accounting',
    'version': '0.1',

    'depends': [
        'account',
    ],

    'data': [
        'views/account_journal_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}

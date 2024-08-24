# -*- coding: utf-8 -*-
{
    'name': "hide archive unarchive buttons based on model",
    'summary': """ This module will help you to Hide archive/unarchive buttons based on model """,
    'description': """ Hide archive/unarchive buttons based on model """,
    'author': "Jay Suthar",
    'category': 'Customise',
    'depends': ['base', 'web'],
    'license': 'AGPL-3',
    'images': ['static/images/banner.png', 'static/description/icon.png'],
    'data': [
        # 'views/assets.xml',
        'security/groups.xml'
    ],

    'assets': {
        'web.assets_backend': [
            'hide_archive_unarchive_buttons/static/js/hide_action_buttons.js',
        ]

    },
    'demo': [],
    'installable': True,
    'application': True,
}

# -*- coding: utf-8 -*-
{
    'name': "WhatsApp Integration Base",

    'summary': """Send WhatsApp Messages to your Contacts""",

    'description': """This module helps you to contact your customer using WhatsApp. Send message and documents""",

    'author': 'ErpMstar Solutions',
    'category': 'WhatsApp Chat',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['contacts', ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'application': True,
    'installable': True,
    'live_test_url': "https://www.youtube.com/watch?v=4zn5lqnEuyk&list=PL054IvUbtGqsUXINB3qj7jr2MXFbDambe",
    'images': ['static/description/banner.jpg'],
    'website': '',
    'auto_install': False,
    'price': 30,
    'currency': 'EUR',

}

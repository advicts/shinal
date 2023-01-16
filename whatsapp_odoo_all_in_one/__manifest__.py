# -*- coding: utf-8 -*-
{
    'name': "Whatsapp Odoo All In One Integration",

    'summary': """Send messages to your customers via WhatsApp messaging service Fully Automated System""",

    'description': """Send your Quotations, Sales Orders, RFQs, Purchase Orders, Invoices/Bills, Payment Receipts, 
    Delivery Orders to Customer's WhatsApp. All in one module.""",

    'author': 'ErpMstar Solutions',
    'category': 'WhatsApp Chat',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'account', 'purchase', 'stock', 'whatsapp_integration_base'],

    # always loaded
    'data': [
        'views/account_views.xml',
        'views/purchase_views.xml',
        'views/sale_views.xml',
        'views/stock_views.xml',
        'views/account_res_config_settings.xml',
        'views/purchase_res_config_settings.xml',
        'views/sale_res_config_settings.xml',
        'views/stock_res_config_settings.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
    'installable': True,
    'live_test_url': "https://www.youtube.com/playlist?list=PL054IvUbtGqv2FWg_zWZTYoobw1I3lPAA",
    'images': ['static/description/banner.jpg'],
    'website': '',
    'auto_install': False,
    'price': 30,
    'currency': 'EUR',

}

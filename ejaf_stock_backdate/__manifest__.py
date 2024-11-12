# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Inventory Force Date (backdate)',
    'category': 'Stock',
    'depends': ['stock_account','product_expiry','mrp'],
    'description': """
        This module will allow you to force moves and accounting entries to a given date.
        """,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'data': [
        'views/stock_view.xml',
    ],
    'installable': True,
}

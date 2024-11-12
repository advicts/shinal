# -*- coding: utf-8 -*-
{
    'name': 'Stock Move Lot Selector',
    'category': 'Operations/Inventory',
    'summary': 'Stock Move Lot Selector',
    'description': """
This module allows to select the lot numbers in the internal transfer stock moves.
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'stock'
    ],
    'data': [
        'views/stock_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Stock Customization',
    'author': "Ejaf Technology",
    'website': "http://www.ejaftech.com/",
    'category': 'stock',
    'depends': ['base','sale_stock'],
    'description': """
          Add new menu 'Free Product' with behaivor scrap functionality.
    """,
    'data': [
        'views/stock_picking.xml',
        'views/stock_scrap.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

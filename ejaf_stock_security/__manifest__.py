# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Stock Security',
    'author': "Ejaf Technology",
    'website': "http://www.ejaftech.com/",
    'category': 'stock',
    'depends': ['base', 'account','simple_readonly_user','stock'],
    'description': """
          Hide All buttons In Stock  Form For group readonly user .
    """,
    'data': [
        'views/stock_picking.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

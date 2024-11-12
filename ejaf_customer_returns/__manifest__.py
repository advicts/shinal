# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Customer Returns with credit notes',
    'category': 'Accounting',
    'description': """
        Create credit notes for customer returns""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['sale_stock'],
    'data': [

        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/setting.xml',
        'views/picking_views.xml',
        'views/invoice_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
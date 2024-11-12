# -*- coding: utf-8 -*-
{
    'name': 'Receipt Direct Payment',
    'category': 'Accounting/Accounting',
    'summary': 'Receipt Direct Payment',
    'description': """
        This module adds the direct payment to receipts.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'account_accountant',
    ],
    'data': [
        'views/account_move.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
}
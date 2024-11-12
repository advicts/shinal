# -*- coding: utf-8 -*-
{
    'name': "Ejaf Account Journal Access",
    'version': '14.0.1.0.0',
    'author': 'Ejaftech',
    'category': 'Accounting',
    'summary': 'add access  group  to Rest To Draft and Delete Journal',
    'description': """
    New type 'add access  group  to Rest To Draft and Delete Journal
    """,
    'depends': ['base','account_accountant'],
    'data': [
        'security/groups.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Account Reports Access',
    'summary': 'Account Reports Access ',
    'description': """
        Account Reports Access
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'base',
        'account_asset',
        'account_reports',
    ],
    'data': [

        'security/groups.xml',
        'views/account_reports_menu.xml',
    ],
    'application': False,
    'installable': True,
}

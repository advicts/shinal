# -*- coding: utf-8 -*-
{
    "name" : "Accounting Reports Customization",
    "category" : "Accounting",
    'summary': 'Accounting Reports Customization',
    "description": """
        Accounting Reports Customization
    """,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    "depends" : [
        'account',
        'account_accountant',
        'account_reports',
        'zom_dairy'
    ],
    "data": [
        'views/search_template_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    'license' : 'OPL-1',
}

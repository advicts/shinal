# -*- coding: utf-8 -*-
{
    'name': 'Partner Currency Restriction',
    'summary': 'Partner Currency Restriction',
    'depends': [
        'base',
        'account',
        'sale',
        'purchase'
    ],
    "description": """
    This module adds partner currency restrictions in transactions. 
   """,
    'author': "Ejaf Technology",
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}

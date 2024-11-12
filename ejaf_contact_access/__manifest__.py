# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Contacts Access',
    'depends': [
        'base',
        'contacts',

    ],
    "description": """ add security group for Contacts Module
   """,
    'author': "Ejaftech",

    'data': [
        'security/groups.xml',
        'views/menuitems.xml',

    ],
    'installable': True,
    'application': False,
}

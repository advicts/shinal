# -*- coding: utf-8 -*-
{
    'name': 'Ejaf MRP Access Rights',
    'summary': 'Ejaf MRP Access Rights',
    'description': """
        This module add new access rights:
        1-Group To can confirm MRP Order.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'mrp',
        'simple_readonly_user',
    ],
    'data': [
        'security/security.xml',
        'views/mrp_order.xml',
    ],
    'application': False,
    'installable': True,
}

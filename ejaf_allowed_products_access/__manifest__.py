# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Allowed Products Access',
    'summary': 'Ejaf Allowed Products Access',
    'description': """
        This module allows to put restriction on products access from user to do any kind of operation.\n
User can not see any products if not allowed by the Product Restriction Manager.\n
Product restriction manager group is used to access all products and can see allowed products tab under user.\n
Product restriction given by two ways By products & By product categories.\n
Restriction by Products: need to add products directly in below "Allowed Product" Section and only that products are accessible in back end to that User.\n
Restriction by Product Categories: need to add Categories directly in below "Allowed Category" Section. All products of given category and its child category are accessible in back end to that User.\n
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml'
    ],
    'application': False,
    'installable': True,
}

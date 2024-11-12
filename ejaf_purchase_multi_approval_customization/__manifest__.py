# -*- coding: utf-8 -*-
{
    'name': 'Purchase Multi Approval Customization',
    'summary': 'Purchase Multi Approval Customization',
    'description': """
        Purchase Multi Approval Customization.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'ejaf_purchase_multi_approval',
        'purchase_stock',
    ],
    'data': [
        'data/data.xml',
        'views/po_approval_level_views.xml',
        'views/purchase_views.xml',
    ],
    'application': False,
    'installable': True,
}

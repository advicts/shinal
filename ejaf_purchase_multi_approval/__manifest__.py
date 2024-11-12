# -*- coding: utf-8 -*-
{
    'name': 'Purchase Multi Approval',
    'category': 'Operations/Purchase',
    'summary': 'Purchase Multi Approval',
    'description': """
This module adds multi level approvals to purchase.
""",
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/group_security.xml',
        'views/po_approval_level_views.xml',
        'views/res_config_settings_views.xml',
        'views/purchase_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
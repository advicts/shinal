# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Payment Approvals',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': """ This modules enables approval feature in the payment.""",
    'description': """This modules enables approval feature in the payment. """,
    'author': 'EjafTech',
    'depends': ['account'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/account_payment_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}

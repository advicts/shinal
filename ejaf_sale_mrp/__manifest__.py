# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Sale MRP',
    'summary': 'Ejaf Sale MRP',
    'description': """
        This module add customer in mrp order if it created from sale order.
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'sale_management', 'sale_mrp',
    ],
    'data': [
        'views/mrp_production_inherit_view.xml',
        'views/menu_items_view.xml',
        'report/operation_report.xml',
    ],
    'application': False,
    'installable': True,
}

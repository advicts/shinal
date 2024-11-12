# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Production Monitoring',
    'summary': 'Ejaf Production Monitoring',
    'description': """
        This module add Production Monitoring .
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'base', 'mrp',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/monitoring_type.xml',
        'views/monitoring_stage.xml',
        'views/production_monitoring.xml',
        'wizard/production_monitoring_wizard.xml',
        'views/mrp_production.xml',
        'views/menu_items_view.xml',
        'data/seq.xml',
    ],
    'application': False,
    'installable': True,
}

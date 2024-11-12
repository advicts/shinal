# -*- coding: utf-8 -*-
{
    'name': 'Product Moves Report',
    'version': '15.0',
    'author': "Ejaftech",
    "description": """
    """,
    'depends': [
        'sale_stock',
        'ejaf_stock_customization',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/reports.xml',
        'wizard/product_moves_wizard.xml',

    ],

    'installable': True,
}

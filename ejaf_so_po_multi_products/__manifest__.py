{
    'name': 'SO & PO Multi Product Selection',
    'version': '15.0',
    'category': 'Sales',
    'summary': 'Sale order and Purchase order Multiple Product Selection',
    'description': """
        This module provide select multiple products
        Features includes managing
            * allow to choose multiple products at once in sale order
            * allow to choose multiple products at once in purchase order
    """,
    'author': "Ejaftech",
    'depends': ['base', 'product', 'sale_management', 'purchase'],
    'data': [
        'wizard/select_products_wizard_view.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'security/ir.model.access.csv'
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

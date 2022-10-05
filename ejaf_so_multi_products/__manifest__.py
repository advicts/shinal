{
    'name': 'SO Multi Product Selection',
    'summary': 'Sale order Multiple Product Selection',
    'description': """
        This module provide select multiple products
        Features includes managing
            * allow to choose multiple products at once in sale order
    """,
    'author': "Ejaftech",
    'depends': ['base', 'product', 'sale_management'],
    'data': [
        'wizard/select_products_wizard_view.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv'
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

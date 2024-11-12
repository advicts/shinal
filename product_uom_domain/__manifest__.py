# -*- coding: utf-8 -*-
{
    'name': "product_uom_domain",
    'summary': """
        add field Unit Volume to product template form""",

    'author': "Ejaftech",

    'version': '0.1',
    'depends': ['base', 'product', 'sale'],

    'data': [
        'views/product_template.xml',
        'views/product_product.xml',
    ],

    'installable': True,
    'application': True,

}

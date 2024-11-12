# -*- coding: utf-8 -*-
{
    'name':
    "Vansales",
    'summary':
    """
     Automation should improve business results. EJAF Technology helps companies make sure it does""",
    'description':
    """
        Automation should improve business results. EJAF Technology helps companies make sure it does. We look at IT issues strategically, in the broader context of our clients' business. We provide information technology (IT) products and services worldwide including outsourcing, process, integrated technology, and technology support to help companies realize the full potential of their IT resources, investments and assets.
We offer business specialized software used to carry out different business activities to increase the productivity of our customers’ businesses and save time in day-to-day tasks. We are one of the few companies that can provide all the “design, build and operate” elements of a complete outsourcing solution.
    """,
    'author':
    "EJAF Technology",
    'website':
    "http://www.ejaftech.com",
    'category':
    'Sales',
    'version':
    '15.1',
    'depends':
    ['base', 'hr_attendance', 'stock', 'sale_management','sale_promotion',
        'web_google_maps', 'product_uom_domain','barcode_action','customer_limit','ejaf_partner_currency_restriction'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/visits_view.xml',
        'views/van_sales_view.xml',
        'views/order_views.xml',
         'views/menu_view.xml',
        'views/payment_views.xml',
        'data/update_partner_cron.xml',


    ],
    'external_dependencies': {
        'python': [
            'couchdb',
            'geopy'

        ],
    }
}

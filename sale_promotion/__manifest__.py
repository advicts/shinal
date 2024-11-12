{
    'name': 'Promotion',
    'version': '15.0.30.12.2022',
    'category': 'sale',
    'summary': 'Sale Promotion',
    'author': 'EjafTech',
    'company': '',
    'maintainer': 'EjafTech',
    'website': 'https://ejaftech.iq',
    'depends': ['sale_management', 'base_address_city', 'product_uom_domain'],
    'data': [
        'views/sale_promotion_views.xml', 'security/ir.model.access.csv',
        'views/sale_order_views.xml'
        # , 'views/cron.xml'
    ],
    'license': 'Other proprietary'
}

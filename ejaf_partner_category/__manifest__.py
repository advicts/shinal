
{
    'name': '''Ejaf Partner Category''',
    'summary': 'This module is used to categorize the partner' ,
    'description': """
        Add categories to Partner
      
    """,
    'category': 'Extra Tools',
    'version': '15.0',
    'sequence': 1,
    'author': 'Ejaftech',
    'depends': ['contacts','sale', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/partner_category_view.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'application': True,
}

# -*- coding: utf-8 -*-
{
    'name': 'Ejaf Invoice By Journal Users',
    'summary': 'Ejaf Invoice By Journal Users',
    "description": """ 
    This app allows you to restrict journals by users that means if user comes under restricted group and if user is allocated only specific journals then system will filter journals and invoices, bills, credit and debit notes, journal entries, sales and purchase receipts for that users for that assigned journals only so that user will not able to see mentioned documents where journal is not available for him/her.
   """,
    'depends': [
        'account','sale_management'
    ],
    'author': "Ejaftech",
    'data': [
        'security/security.xml',
        'views/account_journal.xml',
        'views/menuitems.xml',
    ],
    'installable': True,
    'application': False,
}

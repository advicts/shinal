# -*- coding: utf-8 -*-
{
    'name': "Advicts Partner Ledger & Journal Ledger",
    'summary': """ Advicts Partner Ledger & Journal Ledger """,
    'description': """ Advicts Partner Ledger """,
    'author': "OmarFalih@Advicts",
    'website': "https://advicts.com",
    'category': 'Uncategorized',
    'version': '0.0',
    'depends': ['base', 'account_accountant'],
    'data': [
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'wizard/custom_partner_ledger.xml',
        'wizard/custom_journal_ledger.xml',
        'views/views.xml',
        'report/custom_partner_ledger_report.xml',
        'report/custom_journal_ledger_report.xml',
        'report/report.xml',
    ],
    'license': 'Other proprietary',
}
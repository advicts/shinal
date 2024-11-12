# -*- coding: utf-8 -*-

{
    'name': 'Ejaf Journal Entries Report',
    'version': '15.0.0.0',
    'category': 'Account',
    'summary': 'Allow to print pdf report of Journal Entries.',
    'description': """
    Allow to print pdf report of Journal Entries.
    journal entry
    print journal entry 
    journal entries
    print journal entry reports
    account journal entry reports
    journal reports
    account entry reports

    
""",
    'author': "Ejaf Technology",
    'website': "http://www.ejaftech.com/",
    'depends': ['base', 'account'],
    'data': [
        'report/report_journal_entries.xml',
        'report/report_journal_entries_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

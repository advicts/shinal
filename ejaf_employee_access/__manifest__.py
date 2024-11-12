{
    "name": "Ejaf Employee Access",
    "version": "15.0.",
    'summary': 'Ejaf Employee Access',
    'description': """
        This module add new group for  Employee Access  .
    """
    ,
    'author': 'Ejaf Technology',
    'website': 'http://www.ejaftech.com/',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'views/menu_items.xml',

    ],
    'demo': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
}

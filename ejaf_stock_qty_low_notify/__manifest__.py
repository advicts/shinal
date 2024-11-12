{
    'name' : 'Ejaf Low Stock Quantity Notification',
    'version' : '15.0',
    'author' : 'Ejaftech',
    'summary' : ' This modules is used for sending notification once stock of a product goes below specified amount.',
    'description' : 'The main purpose of this module is to send notification about low stock avaliability.',
    'category' : 'Sales Management',
    'depends' : ['base', 'product'],
    'data':[
                'security/groups.xml',
                'views/product_template.xml',
                'data/ir_cron.xml'
    		],
    'installable': True,
    'license': 'AGPL-3',

}

{
  'name': "Zom Dairy",
  'summary': """      Automation should improve business results. EJAF Technology helps companies make sure it does""",
  'description': """         Automation should improve business results. EJAF Technology helps companies make sure it does. We look at IT issues strategically, in the broader context of our clients' business. We provide information technology (IT) products and services worldwide including outsourcing, process, integrated technology, and technology support to help companies realize the full potential of their IT resources, investments and assets. We offer business specialized software used to carry out different business activities to increase the productivity of our customers’ businesses and save time in day-to-day tasks. We are one of the few companies that can provide all the “design, build and operate” elements of a complete outsourcing solution.     """,
  'author': "EJAF Technology",
  'website': "http://www.ejaftech.com",
  'category': 'Sales',
  'version': '15.1',
  'depends': [
    'base',
    'stock',
    'purchase',
    'barcode_action',
    'ejaf_purchase_multi_approval'
  ],
  'data': [
    'security/security.xml',
    'security/ir.model.access.csv',
    'views/partner_zone.xml',
    'views/zom_dairy_view.xml',
    'views/collection_center_view.xml',
    'views/res_partner_form.xml',
    'views/purchase_view.xml',
    'views/payment_views.xml',
    'views/product_template.xml',
    'views/stock_views.xml',
    'data/sequence.xml',
    'data/update_partner_cron.xml',
    'views/menu_view.xml',
   # 'views/res_config.xml'

  ],
  'external_dependencies': {
    'python': [
      'couchdb',
      
    ],
    
  }
}
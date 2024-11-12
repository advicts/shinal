# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
from .couchdb import CouchDB
import logging
from odoo.tools.safe_eval import safe_eval
from datetime import datetime


_logger = logging.getLogger(__name__)


class VansalesUsers(models.Model):
  _name = 'res.users.vansales'
  _inherit = ['mail.thread']

  user_id = fields.Many2one('res.users',
                            string='Related User',
                            required=True,
                            track_visibility='onchange')
  name = fields.Char(string='User Name', track_visibility='onchange')
  email = fields.Char(string='Email', required=True, track_visibility='onchange')
  password = fields.Char(string='Password', required=True)
  active = fields.Boolean(string='Active', default=True, track_visibility='onchange')
  company_id = fields.Many2one('res.company', string='Company', related='user_id.company_id')

  default_currency_id = fields.Many2one('res.currency',
                                        string="Default Currency",
                                        default=lambda self: self.env.company.currency_id)

  # Inventory Setting ...
  is_delivered = fields.Boolean(string='is delivered', default=False, track_visibility='onchange')
  stock_picking_type = fields.Many2one('stock.picking.type',
                                       string='Operations Types',
                                       track_visibility='onchange')
  warehouse_id = fields.Many2one('stock.warehouse',
                                 string='Warehouse',
                                 compute='_compute_locations',
                                 store=True)
  default_location_src_id = fields.Many2one('stock.location',
                                            string='Default Source Location',
                                            compute='_compute_locations',
                                            store=True)
  default_location_dest_id = fields.Many2one('stock.location',
                                             string='Default Destination Location',
                                             compute='_compute_locations',
                                             store=True)
  # Accounting Setting ...

  return_stock_picking_type = fields.Many2one('stock.picking.type',
                                              string='Operations Types',
                                              track_visibility='onchange')
  return_warehouse_id = fields.Many2one('stock.warehouse',
                                        string='Warehouse',
                                        compute='_compute_return_locations',
                                        store=True)
  return_default_location_src_id = fields.Many2one('stock.location',
                                                   string='Default Source Location',
                                                   compute='_compute_return_locations',
                                                   store=True)
  return_default_location_dest_id = fields.Many2one('stock.location',
                                                    string='Default Destination Location',
                                                    compute='_compute_return_locations',
                                                    store=True)

  load_request_stock_picking_type = fields.Many2one('stock.picking.type',
                                                    string='Operations Types',
                                                    track_visibility='onchange')
  load_request_warehouse_id = fields.Many2one('stock.warehouse',
                                              string='Warehouse',
                                              compute='_compute_load_request_locations',
                                              store=True)
  load_request_default_location_src_id = fields.Many2one('stock.location',
                                                         string='Default Source Location',
                                                         compute='_compute_load_request_locations',
                                                         store=True)
  load_request_default_location_dest_id = fields.Many2one('stock.location',
                                                          string='Default Destination Location',
                                                          compute='_compute_load_request_locations',
                                                          store=True)
  allow_user_update_location = fields.Boolean(string='Allow User to update location ?',
                                              default=True)
  allow_user_order_location = fields.Boolean(
      string='Allow User to order from outside customer location ?', default=True)
  user_order_location_with_in_radius = fields.Integer(
      string='Can user Order from outside customer location With in Radius', default=500)
  allow_over_credit = fields.Boolean('Allow Order Over Credit ?')
  allow_ordering_from_out_of_stock = fields.Boolean('Allow ordering from out of stock ?')
  is_sale_order = fields.Boolean(string='is Sale Order', default=True)
  is_invoiced = fields.Boolean(string='is invoiced', default=False, track_visibility='onchange')
  is_paid_order = fields.Boolean(string='Paid Order', default=False, track_visibility='onchange')
  is_return_validated = fields.Boolean(string='Validate Return and Create Credit Note Draft', default=False, track_visibility='onchange')
  is_return_confirm_credit_note= fields.Boolean(string='Confirm Credit Note', default=False, track_visibility='onchange')

  sale_journal = fields.Many2one('account.journal',
                                 string='Sale Journal',
                                 required=True,
                                 domain="[('type','=','sale')]",
                                 track_visibility='onchange')
  cash_journal = fields.Many2one('account.journal',
                                 string='Cash Journal',
                                 required=True,
                                 domain="[('type','=','cash')]",
                                 track_visibility='onchange')

  is_discount_enable = fields.Boolean(string='Discount', default=False, track_visibility='onchange')
  close_old_visit_on_start_new_visit = fields.Boolean(string='Close old visit on start new visit ?',
                                              default=True)


  enable_free_qty = fields.Boolean(string='Enable Free Qty', default=False)
  analytic_tag_id = fields.Many2one('account.analytic.tag', string='Free Analytic Tag')
  discount_type = fields.Selection(
      [('fixed_amount', 'Fixed Amount'), ('percentage', 'Percentage %')],
      "Apply Maximum Discount",
      default='percentage',
  )

  maximum_discount = fields.Float('Maximum Discount', default=0)

  # Employee Setting ..
  employee_id = fields.Many2one('hr.employee',
                                string='Related Employee',
                                required=True,
                                track_visibility='onchange')
  # Other Setting ...
  is_invoice_printed = fields.Boolean(string='is  printed',
                                      default=False,
                                      track_visibility='onchange')
  is_auto_sync = fields.Boolean(string='Automatic Sync', default=True, track_visibility='onchange')
  force_tracking = fields.Boolean(string='Force Tracking',
                                  default=True,
                                  track_visibility='onchange')

  has_group_uom = fields.Boolean(string="Units of Measure", compute="_compute_has_group_uom")

  product_category_ids = fields.Many2many(string='Product Category',
                                          comodel_name='product.category')

  _sql_constraints = [('user_id_uniq', 'unique (user_id)',
                       "Error This user already assigned to other van sales User")]

  customer_category_ids = fields.Many2many(string='Customer Category',
                                           comodel_name='res.partner.category')

  is_posted_payment = fields.Boolean(string='Posted Payment', default=False)

  is_qr_code_scanning_necessary = fields.Boolean(string='Is QR code scanning necessary ?',
                                              default=True)



  def _compute_has_group_uom(self):
    for rec in self:
      rec.has_group_uom = self._get_default_uom()

  def _get_default_uom(self):
    return self.env.user.user_has_groups('uom.group_uom')

  @api.depends('stock_picking_type', 'stock_picking_type.warehouse_id',
               'stock_picking_type.default_location_src_id',
               'stock_picking_type.default_location_dest_id')
  def _compute_locations(self):
    for rec in self:
      if rec.stock_picking_type:
        rec.warehouse_id = rec.stock_picking_type.warehouse_id
        rec.default_location_src_id = rec.stock_picking_type.default_location_src_id
        rec.default_location_dest_id = rec.stock_picking_type.default_location_dest_id

  @api.depends('return_stock_picking_type', 'return_stock_picking_type.warehouse_id',
               'return_stock_picking_type.default_location_src_id',
               'return_stock_picking_type.default_location_dest_id')
  def _compute_return_locations(self):
    for rec in self:
      if rec.return_stock_picking_type:
        rec.return_warehouse_id = rec.return_stock_picking_type.warehouse_id
        rec.return_default_location_src_id = rec.return_stock_picking_type.default_location_src_id
        rec.return_default_location_dest_id = rec.return_stock_picking_type.default_location_dest_id

  @api.depends('load_request_stock_picking_type', 'load_request_stock_picking_type.warehouse_id',
               'load_request_stock_picking_type.default_location_src_id',
               'load_request_stock_picking_type.default_location_dest_id')
  def _compute_load_request_locations(self):
    for rec in self:
      if rec.load_request_stock_picking_type:
        rec.load_request_warehouse_id = rec.load_request_stock_picking_type.warehouse_id
        rec.load_request_default_location_src_id = rec.load_request_stock_picking_type.default_location_src_id
        rec.load_request_default_location_dest_id = rec.load_request_stock_picking_type.default_location_dest_id

  @api.onchange('user_id')
  def on_change_user_id(self):
    for rec in self:
      if rec.user_id:
        rec.name = rec.user_id.name
        rec.email = rec.user_id.email

  @api.onchange('is_sale_order')
  def on_change_is_sale_order(self):
    for rec in self:
      if rec.is_sale_order == False:
        rec.is_delivered = False
        rec.is_invoiced = False
        rec.is_paid_order = False

  @api.model
  def create(self, values):
    record = super(VansalesUsers, self).create(values)
    self.update_auth_user(record.id)
    self.update_user_setting(record.id)
    return record

  def write(self, values):
    record = super(VansalesUsers, self).write(values)
    self.update_auth_user(self.id)
    self.update_user_setting(self.id)
    return record




  def reset_data_couchdb(self):
    CouchDB().delete_partner_master()
    CouchDB().delete_product_master()
    CouchDB().delete_actions()

  def check_missing_vansales_data(self):
    # self.check_partners(CouchDB().partner_master())
    CouchDB().partner_master().compact()
    # self.check_product(CouchDB().product_master())
    CouchDB().product_master().compact()
    CouchDB().actions().compact()
    CouchDB().settings().compact()

    
  def check_partners(self, db):
    search_partners_obj = self.env['res.partner'].search(
        ['|', ('active', '=', True), ('active', '=', False)])
    doc_ids = list(
        map(lambda partner_id: 'partner' + str(partner_id), (search_partners_obj.mapped('id'))))
    for doc in db.find({'selector': {'type': 'partner'}, 'limit': 100000}):
      if doc['_id'] not in doc_ids:
        doc['_deleted'] = True
        doc_id, doc_rev = db.save(doc)

  def check_product(self, db):
    product_results = self.env['product.product'].search(
        ['|', ('active', '=', True), ('active', '=', False)])
    doc_ids = list(map(lambda pro_id: 'product' + str(pro_id), (product_results.mapped('id'))))
    for doc in db.find({'selector': {'type': 'product'}, 'limit': 100000}):
      if doc['_id'] not in doc_ids:
        doc['_deleted'] = True
        doc_id, doc_rev = db.save(doc)


  def update_auth_user(self, id):
    db = CouchDB().users()
    user = self.env['res.users.vansales'].browse(id)
    doc_id = 'org.couchdb.user:' + user.email
    doc = db.get(doc_id)
    document = {
        '_id': doc_id,
        'type': 'user',
        'password': user.password,
        'name': user.email,
        'phone': user.user_id.phone,
        'image': str(user.user_id.image_1920),
        'company': user.user_id.company_id.name,
        'company_id': user.user_id.company_id.id,
        'mail': user.email,
        'active': user.active,
        'user_name': user.name,
        'roles': [],
        'user_id': user.user_id.id,
    }
    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

  def _get_currencies(self):
    currencies = self.env['res.currency'].search([])
    lst_cur = []
    for currency in currencies:
      lst_cur.append({
          'name': currency.name,
          'id': currency.id,
          'symbol': currency.symbol,
          'rate': currency.rate,
          'rounding': currency.rounding,
          'decimal_places': currency.decimal_places
      })
    return lst_cur

  def update_user_setting(self, id):
    db = CouchDB().settings()
    user = self.env['res.users.vansales'].browse(id)
    team = self.env['crm.team']._get_default_team_id(user_id=user.user_id.id)
    doc_id = 'org.couchdb.user:' + user.email
    doc = db.get(doc_id)
    document = {
        '_id': doc_id,
        'active': user.active,
        'type': 'info_setting',
        'user_id': user.user_id.id,
        'team_id': team.id,
        'default_company_currency_id': {
            'name': user.company_id.currency_id.name,
            'id': user.company_id.currency_id.id,
            'symbol': user.company_id.currency_id.symbol,
            'rate': user.company_id.currency_id.rate,
            'rounding': user.company_id.currency_id.rounding,
            'decimal_places': user.company_id.currency_id.decimal_places
        },
        'default_currency_id': {
            'name': user.default_currency_id.name,
            'id': user.default_currency_id.id,
            'symbol': user.default_currency_id.symbol,
            'rate': user.default_currency_id.rate,
            'rounding': user.default_currency_id.rounding,
            'decimal_places': user.default_currency_id.decimal_places
        },
        'sales_setting': {
            'allow_user_update_location': user.allow_user_update_location,
            'allow_user_order_location': user.allow_user_order_location,
            'allow_ordering_from_out_of_stock':user.allow_ordering_from_out_of_stock,
            'user_order_location_with_in_radius': user.user_order_location_with_in_radius,
            'allow_over_credit': user.allow_over_credit,
            'is_qr_code_scanning_necessary':user.is_qr_code_scanning_necessary,
            'is_invoiced': user.is_invoiced,
            'is_discount_enable': user.is_discount_enable,
            'enable_free_qty': user.enable_free_qty,
            'has_group_uom': user.has_group_uom,
            'is_invoice_printed': user.is_invoice_printed,
            'is_paid_order': user.is_paid_order,
            'sale_journal_id': user.sale_journal.id,
            'sale_journal': str(user.sale_journal.name),
            'cash_journal_id': user.cash_journal.id,
            'cash_journal': str(user.cash_journal.name),
            'customer_category_ids': user.customer_category_ids.mapped('id'),
            'product_category_ids': user.product_category_ids.mapped('id'),
            'currencies': self._get_currencies(),
            'close_old_visit_on_start_new_visit':user.close_old_visit_on_start_new_visit
        },
        'inventory_setting': {
            'is_delivered': user.is_delivered,
            'stock_picking_type': str(user.stock_picking_type.name),
            'stock_picking_type_id': user.stock_picking_type.id,
            'warehouse': str(user.stock_picking_type.warehouse_id.name),
            'warehouse_id': user.stock_picking_type.warehouse_id.id,
            'default_location_src_id': user.stock_picking_type.default_location_src_id.id,
            'default_location_src': str(user.stock_picking_type.default_location_src_id.name),
            'default_location_dest_id': user.stock_picking_type.default_location_dest_id.id,
            'default_location_dest': str(user.stock_picking_type.default_location_dest_id.name),
        },
        'employee': {
            'emp_id': user.employee_id.id,
            'display_name': user.employee_id.display_name,
            'company_id': (user.employee_id.company_id.id),
            'company_name': str(user.employee_id.company_id.name),
            'birthday': str(user.employee_id.birthday),
            'gender': str(user.employee_id.gender),
            'name': user.employee_id.name,
            'mobile_phone': str(user.employee_id.mobile_phone),
            'image_small': str(user.employee_id.image_1920),
            'work_phone': str(user.employee_id.work_phone),
        },
        'other': {
            'is_auto_sync': user.is_auto_sync,
            'force_tracking': user.force_tracking
        }
    }
    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

  def action_update_sync(self):
    self.update_master_data()

  @api.model
  def update_master_data(self):
    for rec in self:
      self.update_user_setting(rec.id)
    db = CouchDB().product_master()
    self.update_product_category(db)
    self.update_product(db, 0)
    self.update_pricelist(db)
    self.update_uom(db)
    self.update_stock_quant(db)
    # self.update_promotion(db)
    CouchDB().actions()
    self.update_partners(CouchDB().partner_master())
    CouchDB().tracking()
    CouchDB().messages()

  def update_partners_cron(self):
    self.update_partners(CouchDB().partner_master())

  def update_product_category(self, db):
    doc = db.get('product_category_list')
    search_product_category_obj = self.env['product.category'].search([('parent_id', '=', False)])
    document = {
        '_id': 'product_category_list',
        'type': 'product_category',
        'list': self.compute_category_tree(search_product_category_obj),
    }
    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

  def compute_category_tree(self, categories):
    list_document = []
    for category in categories:
      document = {
          'category_id': category.id,
          'children': self.compute_category_tree(category.child_id),
          'complete_name': {
              'en': category.with_context({
                  'lang': 'en_US'
              }).complete_name,
              'ar': category.with_context({
                  'lang': 'ar_SY'
              }).complete_name,
              'kr': category.complete_name
          },
          'parent_id': category.parent_id.id,
          'name': {
              'en': category.with_context({
                  'lang': 'en_US'
              }).name,
              'ar': category.with_context({
                  'lang': 'ar_SY'
              }).name,
              'kr': category.name
          },
          'product_count': category.product_count,
      }
      list_document.append(document)
    return list_document

  def update_uom(self, db):
    doc = db.get('product_uom_list')
    search_uom_obj = self.env['uom.uom'].search([])
    lst = []
    for uom in search_uom_obj:
      lst.append({
          'id': uom.id,
          'name': {
              'en': uom.with_context({
                  'lang': 'en_US'
              }).name,
              'ar': uom.with_context({
                  'lang': 'ar_SY'
              }).name,
              'kr': uom.name
          },
          'rounding': uom.rounding,
          'factor': uom.factor,
          'factor_inv': uom.factor_inv,
          'uom_type': uom.uom_type,
          'category_id': uom.category_id.id,
          'active': uom.active
      })
    document = {'_id': 'product_uom_list', 'type': 'product_uom', 'list': lst}
    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

  def update_partners(self, db):
    search_partners_obj = self.env['res.partner'].search(
        ['|', ('active', '=', True), ('active', '=', False)])
    doc_ids = list(
        map(lambda partner_id: 'partner' + str(partner_id), (search_partners_obj.mapped('id'))))
    couchdb_partners_results = (db.view("_all_docs", keys=doc_ids))
    bulk_doc_update = []
    for customer in search_partners_obj:
      doc_id = 'partner' + str(customer.id)
      document = {
          '_id': doc_id,
          'user_id': customer.user_id.id,
          'customer_limit_rule': customer.customer_limit_rule,
          'customer_limit': customer.customer_limit,
          'type': 'partner',
          'active': customer.active,
          'id': customer.id,
          'property_payment_term_id': customer.property_payment_term_id.id,
          'property_payment_term': customer.property_payment_term_id.name,
          'name': customer.name,
          'partner_currency': {
              'name': customer.partner_currency_id.name,
              'id': customer.partner_currency_id.id,
              'symbol': customer.partner_currency_id.symbol,
              'rate': customer.partner_currency_id.rate,
              'rounding': customer.partner_currency_id.rounding,
              'decimal_places': customer.partner_currency_id.decimal_places
          } if customer.partner_currency_id else False,
          'city': customer.city,
          'color': customer.color,
          'total_due': customer.total_due,
          'credit': customer.credit,
          'credit_limit': customer.credit_limit,
          'debit': customer.debit,
          'debit_limit': customer.debit_limit,
          'display_name': customer.display_name,
          'email': customer.email,
          'image_small': '',
          'lang': customer.lang,
          'mobile': customer.mobile,
          'parent_name': customer.parent_name,
          'partner_latitude': customer.partner_latitude,
          'partner_longitude': customer.partner_longitude,
          'phone': str(customer.phone),
          'street': str(customer.street),
          'total_invoiced': customer.total_invoiced,
          'sale_order_count': customer.sale_order_count,
          'property_product_pricelist_id': customer.property_product_pricelist.id,
          'property_product_pricelist': customer.property_product_pricelist.name,
          'category_id': customer.category_id.mapped('id'),
          'company_type': customer.company_type
      }

      old_doc = list(filter(lambda x: x.id == doc_id, couchdb_partners_results))
      if len(old_doc) > 0:
        document['_rev'] = old_doc[0].value['rev']
      bulk_doc_update.append(document)
    db.update(bulk_doc_update)

  # Used To Insert Or Update Bulk Products ..
  def update_product(self, db, offset):
    product_results = self.env['product.product'].search(
        ['|', ('active', '=', True), ('active', '=', False)], offset=offset, limit=1000)
    doc_ids = list(map(lambda pro_id: 'product' + str(pro_id), (product_results.mapped('id'))))
    couchdb_products = (db.view("_all_docs", keys=doc_ids))
    # Bulk Query of old Products
    bulk_doc_update = []
    for product in product_results:
      doc_id = 'product' + str(product.id)
      document = {
          '_id': doc_id,
          'type': 'product',
          'product_id': product.id,
          'product_tmpl_id': product.product_tmpl_id.id,
          'code': product.default_code,
          'active': product.active,
          'tracking':product.tracking,
          'display_name': {
              'en': product.with_context({
                  'lang': 'en_US'
              }).display_name,
              'ar': product.with_context({
                  'lang': 'ar_SY'
              }).display_name,
              'kr': product.display_name
          },
          'categ_id': product.categ_id.id,
          'categ': {
              'en': product.with_context({
                  'lang': 'en_US'
              }).categ_id.name,
              'ar': product.with_context({
                  'lang': 'ar_SY'
              }).categ_id.name,
              'kr': product.categ_id.name
          },
          'image_small': '',
          'uom_id': product.uom_id.id,
          'uom_categ_id': product.uom_id.category_id.id,
          # TODO Remove uom
          'uom': {
              'en': product.with_context({
                  'lang': 'en_US'
              }).uom_id.name,
              'ar': product.with_context({
                  'lang': 'ar_SY'
              }).uom_id.name,
              'kr': product.uom_id.name
          },
          'default_uom': {
              'id': product.uom_id.id,
              'name': {
                  'en': product.uom_id.with_context({
                      'lang': 'en_US'
                  }).name,
                  'ar': product.uom_id.with_context({
                      'lang': 'ar_SY'
                  }).name,
                  'kr': product.uom_id.name
              },
              'rounding': product.uom_id.rounding,
              'factor': product.uom_id.factor,
              'factor_inv': product.uom_id.factor_inv,
              'uom_type': product.uom_id.uom_type,
              'category_id': product.uom_id.category_id.id,
              'active': product.uom_id.active
          },
          'list_price': product.lst_price,
          'name': {
              'en': product.with_context({
                  'lang': 'en_US'
              }).name,
              'ar': product.with_context({
                  'lang': 'ar_SY'
              }).name,
              'kr': product.name
          },
          'price': product.price,
          'barcode': product.barcode,
          'qty_available': 0,
          'display_price': product.lst_price,
          'uom_sell_ids': product.uom_sell_ids.mapped('id'),
          'lots':product._get_product_lots(product_id=product.id)

          # 'has_packages':True if product.packaging_ids else False,
          # 'packaging_ids':self.init_product_packages(product.packaging_ids)
      }

      old_doc = list(filter(lambda x: x.id == doc_id, couchdb_products))
      if len(old_doc) > 0:
        document['_rev'] = old_doc[0].value['rev']
      bulk_doc_update.append(document)
    db.update(bulk_doc_update)
    if product_results:
      self.update_product(db, (offset + 1000))
    else:
      return

  def update_pricelist(self, db):
    pricelist_results = self.env['product.pricelist'].search([('active', '=', True)])
    doc_ids = list(map(lambda p_id: 'pricelist' + str(p_id), (pricelist_results.mapped('id'))))
    couchdb_pricelist = (db.view("_all_docs", keys=doc_ids))
    # Bulk Query of old Products
    bulk_doc_update = []
    for pricelist in pricelist_results:
      doc_id = 'pricelist' + str(pricelist.id)
      document = {
          '_id': doc_id,
          'type': 'pricelist',
          'id': pricelist.id,
          'display_name': pricelist.display_name,
          'name': pricelist.name,
          'active': pricelist.active,
          'currency': {
              'name': pricelist.currency_id.name,
              'id': pricelist.currency_id.id,
              'symbol': pricelist.currency_id.symbol,
              'rate': pricelist.currency_id.rate,
              'rounding': pricelist.currency_id.rounding,
              'decimal_places': pricelist.currency_id.decimal_places
          },
          'discount_policy': pricelist.discount_policy,
          'item_ids': self.get_item_ids(pricelist.item_ids)
      }
      old_doc = list(filter(lambda x: x.id == doc_id, couchdb_pricelist))
      if len(old_doc) > 0:
        document['_rev'] = old_doc[0].value['rev']
      bulk_doc_update.append(document)
    db.update(bulk_doc_update)

  def get_item_ids(self, item_ids):
    doc = []
    for item in item_ids:
      doc.append({
          'id': item.id,
          'name': item.name,
          'applied_on': item.applied_on,
          'base': item.base,
          'categ_id': item.categ_id.id,
          'company_id': item.company_id.id,
          'compute_price': item.compute_price,
          'currency_id': item.currency_id.id,
          'currency_symbol': {
              'en': item.with_context({
                  'lang': 'en_US'
              }).currency_id.symbol,
              'ar': item.with_context({
                  'lang': 'ar_SY'
              }).currency_id.symbol,
              'kr': item.currency_id.symbol
          },
          'currency': item.currency_id.display_name,
          'date_end': str(item.date_end),
          'date_start': str(item.date_start),
          'fixed_price': item.fixed_price,
          'min_quantity': item.min_quantity,
          'percent_price': item.percent_price,
          'price': item.price,
          'price_discount': item.price_discount,
          'price_max_margin': item.price_max_margin,
          'price_min_margin': item.price_min_margin,
          'price_round': item.price_round,
          'price_surcharge': item.price_surcharge,
          'product_id': item.product_id.id,
          'product_tmpl_id': item.product_tmpl_id.id
      })

    return doc

  def update_stock_quant(self, db):
    # Used To Insert Or Update Bulk Products ..
    search_settings_obj = self.env['res.users.vansales'].search([('active', '=', True)])
    for location_id in set(search_settings_obj.mapped('default_location_src_id')):
      self.update_stock_quant_product(db, location_id.id, 0)
    return

  def update_stock_quant_product(self, db, location_id, offset):
    search_stock_quants = self.env['stock.quant'].search([('location_id', '=', location_id)],
                                                         offset=offset,
                                                         limit=1000)
    doc_ids = list(
        map(lambda pro_id: 'quant-' + str(pro_id.id) + "-" + str(location_id),
            (search_stock_quants.mapped('product_id'))))
    couchdb_products = (db.view("_all_docs", keys=doc_ids))

    # Bulk Query of old Products
    docs = {}
    for quant in search_stock_quants:
      doc_id = 'quant-' + str(quant.product_id.id) + \
          "-" + str(location_id)
      doc_key = str(quant.product_id.id)+"-" + \
          str(location_id)+"-"+str(quant.lot_id.id)
      if docs.get(doc_id):
        if docs[doc_id]['lots'].get(doc_key):
          docs[doc_id]['lots'][
              doc_key].quantity = docs[doc_id]['lots'][doc_key]['quantity'] + quant.quantity
          docs[doc_id]['lots'][doc_key].reserved_quantity = docs[doc_id]['lots'][doc_key]['reserved_quantity'] + \
              quant.reserved_quantity
        else:
          docs[doc_id]['lots'][doc_key] = {
              'lot_id': quant.lot_id.id,
              'lot': quant.lot_id.name,
              'lot_expiration_date': str(quant.lot_id.expiration_date),
              'lot_removal_date': str(quant.lot_id.removal_date),
              'quantity': quant.quantity,
              'reserved_quantity': quant.reserved_quantity
          }
      else:
        docs[doc_id] = {
            'lots': {
                doc_key: {
                    'lot_id': quant.lot_id.id,
                    'lot': quant.lot_id.name,
                    'lot_expiration_date': str(quant.lot_id.expiration_date),
                    'lot_removal_date': str(quant.lot_id.removal_date),
                    'quantity': quant.quantity,
                    'reserved_quantity': quant.reserved_quantity
                }
            },
            'product_id': quant.product_id.id,
            'location_id': location_id,
            '_id': doc_id,
            'type': quant
        }

    bulk_doc_update = []
    for key, item in docs.items():
      quants_lst = list(item['lots'].values())
      document = {
          '_id': item['_id'],
          'type': 'quant',
          'product_id': item['product_id'],
          'location_id': item['location_id'],
          'update_date':datetime.timestamp(datetime.now())*1000,
          'quant': {
              'qty': sum(q['quantity'] for q in quants_lst),
              'reserved_quantity': sum(q['reserved_quantity'] for q in quants_lst),
              'lots': quants_lst
          }
      }
      old_doc = list(filter(lambda x: x.id == item['_id'], couchdb_products))
      if len(old_doc) > 0:
        document['_rev'] = old_doc[0].value['rev']
      bulk_doc_update.append(document)
    db.update(bulk_doc_update)
    if search_stock_quants:
      self.update_stock_quant_product(db, location_id, (offset + 1000))
    else:
      return

  def update_promotion(self, db):
    partner_obj = self.env['res.partner']
    product_obj = self.env['product.product']
    promotions = self.env['coupon.program'].search([('program_type', '=', 'promotion_program')])

    doc_ids = list(
        map(lambda promotion_id: 'promotion' + str(promotion_id), (promotions.mapped('id'))))
    couchd_promotions = (db.view("_all_docs", keys=doc_ids))
    # Bulk Query of old Products
    bulk_doc_update = []
    for promotion in promotions:
      doc_id = 'promotion' + str(promotion.id)
      document = {
          '_id': doc_id,
          'type': 'promotion',
          'id': promotion.id,
          'name': {
              'en': promotion.with_context({
                  'lang': 'en_US'
              }).name,
              'ar': promotion.with_context({
                  'lang': 'ar_SY'
              }).name,
              'kr': promotion.name
          },
          'active': promotion.active,
          'promo_code_usage': promotion.promo_code_usage,
          'rule_partners_domain': promotion.rule_partners_domain,
          'rule_min_quantity': promotion.rule_min_quantity,
          'rule_minimum_amount': promotion.rule_minimum_amount,
          'promo_applicability': promotion.promo_applicability,
          'reward_type': promotion.reward_type,
          'discount_type': promotion.discount_type,
          'discount_apply_on': promotion.discount_apply_on,
          'reward_product_id': {
              'product': promotion.reward_product_id.name,
              'product_id': promotion.reward_product_id.id,
              'product_barcode': promotion.reward_product_id.barcode,
              'product_uom_id': promotion.reward_product_id.uom_id.id,
              'product_uom_categ_id': promotion.reward_product_id.uom_id.category_id.id,
              'product_uom': promotion.reward_product_id.uom_id.name,
          },
          'reward_product_quantity': promotion.reward_product_quantity,
          'discount_fixed_amount': promotion.discount_fixed_amount,
          'discount_line_product_id': {
              'product': promotion.discount_line_product_id.name,
              'product_id': promotion.discount_line_product_id.id,
              'product_barcode': promotion.discount_line_product_id.barcode,
              'product_uom_id': promotion.discount_line_product_id.uom_id.id,
              'product_uom_categ_id': promotion.discount_line_product_id.uom_id.category_id.id,
              'product_uom': promotion.discount_line_product_id.uom_id.name,
          },
          'discount_max_amount': promotion.discount_max_amount,
          'reward_product_uom_id': promotion.reward_product_uom_id.id,
          'discount_percentage': promotion.discount_percentage,
          'discount_specific_product_ids': promotion.discount_specific_product_ids.mapped('id'),
          'display_name': promotion.display_name,
          'rule_id': promotion.rule_id.id,
          'rule_date_from': promotion.rule_date_from,
          'rule_date_to': promotion.rule_date_to,
          'rule_minimum_amount_tax_inclusion': promotion.rule_minimum_amount_tax_inclusion,
          'reward_id': promotion.reward_id.id,
          'rule_partner_ids': self._compute_rule_partner_ids(promotion, partner_obj),
          'rule_product_ids': self._compute_rule_product_ids(promotion, product_obj),
      }

      old_doc = list(filter(lambda x: x.id == doc_id, couchd_promotions))
      if len(old_doc) > 0:
        document['_rev'] = old_doc[0].value['rev']
      bulk_doc_update.append(document)
    db.update(bulk_doc_update)

    return

  def _compute_rule_partner_ids(self, program, partner_obj):
    try:
      domain = safe_eval(program.rule_id.rule_partners_domain)
    except:
      domain = []
    return partner_obj.search(domain).mapped('id')

  def _compute_rule_product_ids(self, program, product_obj):
    try:
      domain = safe_eval(program.rule_id.rule_products_domain)
    except:
      domain = []
    return product_obj.search(domain).mapped('id')


class VansalesUsersLive(models.Model):
  _name = 'res.users.vansales.live'

  name = fields.Char('')

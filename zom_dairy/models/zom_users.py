# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
from .couchdb import CouchDB
import logging
from odoo.tools.safe_eval import safe_eval
from functools import reduce

_logger = logging.getLogger(__name__)


class ZomDairyUsers(models.Model):
  _name = 'res.users.zom_dairy'
  _inherit = ['mail.thread']

  user_id = fields.Many2one('res.users',
                            string='Related User',
                            required=True,
                            track_visibility='onchange')
  name = fields.Char(string='User Name', track_visibility='onchange')
  email = fields.Char(string='Email', required=True, track_visibility='onchange')
  password = fields.Char(string='Password', required=True)
  active = fields.Boolean(string='Active', default=True, track_visibility='onchange')
  collection_center_id = fields.Many2one('collection.center',
                                         string='Collection Center',
                                         required=True,
                                         domain=[('active', '=', True)])

  cash_journal = fields.Many2one('account.journal',
                                   string='Cash Journal',
                                   required=True,
                                   domain="[('type','=','cash')]",
                                   track_visibility='onchange')


  @api.onchange('user_id')
  def on_change_user_id(self):
    for rec in self:
      if rec.user_id:
        rec.name = rec.user_id.name
        rec.email = rec.user_id.email

  @api.model
  def create(self, values):
    record = super(ZomDairyUsers, self).create(values)
    self.update_auth_user(record.id)
    self.update_user_setting(record.id)
    return record

  def write(self, values):
    record = super(ZomDairyUsers, self).write(values)
    self.update_auth_user(self.id)
    self.update_user_setting(self.id)
    return record

  def update_auth_user(self, id):
    db = CouchDB().users()
    user = self.env['res.users.zom_dairy'].browse(id)
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
        'roles': ['user'],
        'user_id': user.user_id.id,
    }
    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

  def update_user_setting(self, _id):
    db = CouchDB().settings()
    user = self.env['res.users.zom_dairy'].browse(_id)
    doc_id = 'org.couchdb.user:' + user.email
    doc = db.get(doc_id)
    document = {
        '_id': doc_id,
        'active': user.active,
        'type': 'info_setting',
        'user_id': user.user_id.id,
        'collection_center': {
            'id': user.collection_center_id.id,
            'name': user.collection_center_id.name,
            'driver':self._get_drivers(user.collection_center_id.receive_milk_driver_operation_type_id),
            'product_ids': self._get_products(user.collection_center_id.product_ids)
        }
    }
    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

  def _get_products(self, products):
    products_lst = []
    for product in products:
      products_lst.append({
          'id': product.id,
          'name': product.name,
          'standard_price': product.fixed_cost,
          'uom_po_id': product.uom_po_id.id,
          'uom_po': product.uom_po_id.name
      })
    return products_lst


  def _get_drivers(self, drivers):
    driver_lst = []
    for driver in drivers:
      driver_lst.append({
          'id': driver.id,
          'name': driver.name,
          'default_location_src':driver.default_location_src_id.name+"-"+driver.name,
          'default_location_src_id':driver.default_location_src_id.id
      })
    return driver_lst
  def action_update_sync(self):
    self.update_master_data()

  @api.model
  def update_master_data(self):
    for rec in self:
      self.update_user_setting(rec.id)
    CouchDB().actions()
    self.update_partners(CouchDB().partner_master())


  def update_partners_cron(self):
    self.update_partners(CouchDB().partner_master())
  def update_partner(self,partner_id):
      self.update_partners(CouchDB().partner_master(),partner_id)

  def update_partners(self, db,partner_id=False):
    if partner_id:
        search_partners_obj = self.env['res.partner'].search([('id','=',partner_id)])
    else:
        search_partners_obj = self.env['res.partner'].search([])
    doc_ids = list(
        map(lambda partner_id: 'partner' + str(partner_id), (search_partners_obj.mapped('id'))))
    couchdb_partners_results = (db.view("_all_docs", keys=doc_ids))
    bulk_doc_update = []
    for customer in search_partners_obj:
      doc_id = 'partner' + str(customer.id)
      invoices = customer._get_invoices(customer)
      document = {
            '_id': doc_id,
            'user_id': customer.user_id.id,
            'type': 'partner',
            'id': customer.id,
            'is_milk_supplier': customer.is_milk_supplier,
            'name': customer.name,
            'city': customer.city,
            'display_name': customer.display_name,
            'email': customer.email,
            'lang': customer.lang,
            'debit':reduce(lambda total,invoice: total + invoice['amount'], invoices,0),
            'credit':0,
            'mobile': customer.mobile,
            'parent_name': customer.parent_name,
            'partner_latitude': customer.partner_latitude,
            'partner_longitude': customer.partner_longitude,
            'category_id': customer.category_id.mapped('id'),
            'phone': str(customer.phone),
            'street': str(customer.street),
            'total_invoiced': reduce(lambda total,invoice: total + invoice['amount'], invoices,0),
            'collection_center_id': customer.collection_center_id.id,
            'collection_center': customer.collection_center_id.name,
            'invoices': invoices
        }

      old_doc = list(filter(lambda x: x.id == doc_id, couchdb_partners_results))
      if len(old_doc) > 0:
        document['_rev'] = old_doc[0].value['rev']
      bulk_doc_update.append(document)
    db.update(bulk_doc_update)


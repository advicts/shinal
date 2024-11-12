from ast import Return
import logging
from odoo import models, fields, api
from .couchdb import CouchDB
import json


class Partner(models.Model):
  _inherit = 'res.partner'

  @api.model
  def create(self, vals):
    res = super().create(vals)
    if not self.env.context.get('import_file'):
      self.update_partner(CouchDB().partner_master(), res.id)
    return res

  def write(self, values):
    for rec in self:
      record = super(Partner, self).write(values)
      self.update_partner(CouchDB().partner_master(), rec.id)
      return record

  def unlink(self):
    for rec in self:
      res = super(Partner, self).unlink()
      if res:
        self.unlink_partner(CouchDB().partner_master(), rec.id)
      return res

  def unlink_partner(self, db, partner_id):
    doc_id = 'partner' + str(partner_id)
    doc = db.get(doc_id)
    doc['_deleted'] = True
    doc_id, doc_rev = db.save(doc)

  def update_partner_doc(self):
    for rec in self:
      self.update_partner(CouchDB().partner_master(), rec.id)

  def update_partner(self, db, partner_id):
    customer = self.env['res.partner'].browse(partner_id)
    doc_id = 'partner' + str(partner_id)
    doc = db.get(doc_id)
    document = {
        '_id': doc_id,
        'user_id': customer.user_id.id,
        'customer_limit_rule': customer.customer_limit_rule,
        'customer_limit': customer.customer_limit,
        'type': 'partner',
        'active':customer.active,
        'id': customer.id,
        'partner_currency': {
            'name': customer.partner_currency_id.name,
            'id': customer.partner_currency_id.id,
            'symbol': customer.partner_currency_id.symbol,
            'rate': customer.partner_currency_id.rate,
            'rounding': customer.partner_currency_id.rounding,
            'decimal_places': customer.partner_currency_id.decimal_places
        } if customer.partner_currency_id else False,
        'property_payment_term_id': customer.property_payment_term_id.id,
        'property_payment_term': customer.property_payment_term_id.name,
        'name': customer.name,
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
        'category_id': customer.category_id.mapped('id'),
        'phone': str(customer.phone),
        'street': str(customer.street),
        'total_invoiced': customer.total_invoiced,
        'sale_order_count': customer.sale_order_count,
        'property_product_pricelist_id': customer.property_product_pricelist.id,
        'property_product_pricelist': customer.property_product_pricelist.name,
    }

    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

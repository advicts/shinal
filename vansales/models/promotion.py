from odoo import models, fields, api
from .couchdb import CouchDB
import json


class Promotion(models.Model):
  _inherit = 'sale.promotion'

  @api.model
  def create(self, vals):
    res = super().create(vals)
    if not self.env.context.get('import_file'):
      self.update_promotion(CouchDB().product_master(), res.id)
    return res

  def unlink(self):
    for rec in self:
      res = super(Promotion, self).unlink()
      if res:
        self.unlink_promotion(CouchDB().product_master(), rec.id)
      return res

  def unlink_promotion(self, db, promotion_id):
    doc_id = 'promotion' + str(promotion_id)
    doc = db.get(doc_id)
    doc['_deleted'] = True
    doc_id, doc_rev = db.save(doc)

  def write(self, values):
    record = super(Promotion, self).write(values)
    self.update_promotion(CouchDB().product_master(), self.id)
    return record

  def update_promotion(self, db, promotion_id):
    promotion = self.env['sale.promotion'].browse(promotion_id)
    doc_id = 'promotion' + str(promotion.id)
    doc = db.get(doc_id)
    document = {
        '_id':
            doc_id,
        'type':
            'promotion',
        'promotion_id':
            promotion.id,
        'promotion':
            promotion.name,
        'analytic_tag_id':
            promotion.analytic_tag_id.id,
        'default_currency_id':{
              'name': promotion.default_currency_id.name,
              'id': promotion.default_currency_id.id,
              'symbol': promotion.default_currency_id.symbol,
              'rate': promotion.default_currency_id.rate,
              'rounding': promotion.default_currency_id.rounding,
              'decimal_places': promotion.default_currency_id.decimal_places
          },
          'description':promotion.description,
        'active':
            promotion.active,
        'state':
            promotion.state,
        'start_at':
            str(promotion.start_at),
        'end_at':
            str(promotion.end_at),
        'users_rule_based_on':
            promotion.users_rule_based_on,
        'specific_team_ids':
            promotion.specific_team_ids.mapped('id') if promotion.specific_team_ids else [],
        'specific_user_ids':
            promotion.specific_user_ids.mapped('id') if promotion.specific_user_ids else [],
        'partner_rule_based_on':
            promotion.partner_rule_based_on,
        'customer_category_ids':
            promotion.customer_category_ids.mapped('id') if promotion.customer_category_ids else [],
        'product_rule_based_on':
            promotion.product_rule_based_on,
        'specific_categ_ids':
            promotion.specific_categ_ids.mapped('id') if promotion.specific_categ_ids else [],
        'specific_product_ids':
            promotion.specific_product_ids.mapped('id') if promotion.specific_product_ids else [],
        'specific_product_temp_ids':
            promotion.specific_product_temp_ids.mapped('id')
            if promotion.specific_product_temp_ids else [],
        'applied_on':
            promotion.applied_on,
        'reward_by':
            promotion.reward_by,
        'min_quantity':
            promotion.min_quantity,
        'min_amount':
            promotion.min_amount,
        'discount_type':
            promotion.discount_type,
        'discount_fixed_amount':
            promotion.discount_fixed_amount,
        'discount_percentage':
            promotion.discount_percentage,
        'product_discounts_ids':
            self._get_product_discounts_ids(promotion.product_discounts_ids),
        'product_rewards_ids':
            self._get_product_rewards_ids(promotion.product_rewards_ids),
        'global_discount_product_id':
            self._get_global_discount_product_id(promotion.global_discount_product_id)
            if promotion.global_discount_product_id else False
    }

    if doc:
      document['_rev'] = doc['_rev']
    doc_id, doc_rev = db.save(document)

  def _get_product_discounts_ids(self, product_discounts_ids):
    lst = []
    for discount in product_discounts_ids:
      lst.append({
          'id': discount.id,
          'discount_type': discount.discount_type,
          'amount': discount.amount
      })
    return lst

  def _get_product_rewards_ids(self, product_rewards_ids):
    lst = []
    for reward in product_rewards_ids:
      lst.append({
          'id': reward.id,
          'product_id': reward.product_id.id,
          'product_uom_id': {
              'id': reward.product_uom_id.id,
              'name': {
                  'en': reward.product_uom_id.with_context({
                      'lang': 'en_US'
                  }).name,
                  'ar': reward.product_uom_id.with_context({
                      'lang': 'ar_SY'
                  }).name,
                  'kr': reward.product_uom_id.name
              },
              'rounding': reward.product_uom_id.rounding,
              'factor': reward.product_uom_id.factor,
              'factor_inv': reward.product_uom_id.factor_inv,
              'uom_type': reward.product_uom_id.uom_type,
              'category_id': reward.product_uom_id.category_id.id,
              'active': reward.product_uom_id.active
          },
          'qty': reward.qty
      })
    return lst

  def _get_global_discount_product_id(self, product):
    return {
        'type': 'product',
        'product_id': product.id,
        'product_tmpl_id': product.product_tmpl_id.id,
        'code': product.default_code,
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
        'qty_available': product.qty_available,
        'display_price': product.lst_price,
        'uom_sell_ids': product.uom_sell_ids.mapped('id')
    }

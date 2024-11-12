from functools import reduce
from odoo import models, fields, api
from .. import utils
import copy
from toolz import assoc, assoc_in
import random
import uuid


class SaleOrder(models.Model):
  _inherit = 'sale.order'

  def apply_promotion(self):
    available_promotions = self._filter_promotion_basedon_customer_rule(
        self._filter_promotion_basedon_user_rule())
    if available_promotions:
      potential_order_lines = self.consolidate_lines(
          self.apply_promotion_order_lines(self._clone_order(), available_promotions))
      potential_order = self._apply_discount_on_total_order(potential_order_lines,
                                                            available_promotions)
      self.order_line.unlink()
      self.order_line = self._recreate_lines(potential_order)
    return True

  # TO-DO use reduce Func
  def _clone_order(self):
    order_to_promot = {}
    for i, line in enumerate(self.order_line.filtered(lambda l: not l.is_reward_product)):
      for j, qty in enumerate(
          utils.disassemble(
              line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id))):
        order_to_promot[str(i) + "-" + str(j)] = {
            'index':
                str(i) + "-" + str(j),
            'product_id':
                line.product_id.id,
            'categ_id':
                line.product_id.categ_id.id,
            'product_tmpl_id':
                line.product_id.product_tmpl_id.id,
            'product_uom':
                line.product_uom.id,
            'default_uom':
                line.product_id.uom_id.id,
            'discount':
                0 if line.promotion_id else line.discount,
            'price':
                line.price_unit,
            'default_price':
                line.product_uom._compute_price(line.price_unit, line.product_id.uom_id),
            'qty':
                line.product_uom_qty,
            'default_qty':
                qty,
            'is_promotion':
                False,
            'total_price':
                0,
            'discount_amount':
                0,
            'promotion_id':
                0,
            'is_reward_product':
                False,
            'total_amount':
                0
        }
    return {'orderLines': order_to_promot, 'total_discount': 0}

  def consolidate_lines(self, order):

    def _get_key(line):
      return str(line['product_id']) + "-" + str(line['promotion_id']) + "-" + str(
          line['discount']) + "-" + str(line['product_uom'])

    lines = reduce(
        lambda acc, line: assoc_in(
            acc, [_get_key(line)], line if _get_key(line) not in acc else assoc_in(
                acc[_get_key(line)], ['default_qty'], acc[_get_key(line)]['default_qty'] + line[
                    'default_qty'])), list(order['orderLines'].values()), {})

    return list(lines.values())

  def _recreate_lines(self, order_lines):
    new_order_lines = []
    for line in order_lines:
      product = self.env['product.product'].browse(line['product_id'])
      uom = self.env['uom.uom'].browse(line['product_uom'])
      promotion = self.env['sale.promotion'].sudo().browse(line["promotion_id"])
      new_order_lines.append((0, 0, {
          'product_id': product.id,
          'product_uom': uom.id,
          'price_unit': line['price'],
          'product_uom_qty': product.uom_id._compute_quantity(line['default_qty'], uom),
          'discount': line['discount'],
          'promotion_id': promotion.id,
          'is_reward_product': line['is_reward_product']
      }))
    return new_order_lines

  def _filter_basedon_user_rule(self, promotion):
    if promotion.users_rule_based_on == 'all':
      return True
    elif promotion.users_rule_based_on == 'specific_teams':
      if self.team_id.id in promotion.specific_team_ids.ids:
        return True
    elif promotion.users_rule_based_on == 'specific_user':
      if self.user_id.id in promotion.specific_user_ids.ids:
        return True
    return False

  def _filter_promotion_basedon_user_rule(self):
    promotions = self.env['sale.promotion'].sudo().search([('active', '=', True),
                                                           ('state', '=', 'running')])
    return promotions.filtered(self._filter_basedon_user_rule)

  def _filter_basedon_customer_rule(self, promotion):
    if promotion.partner_rule_based_on == 'all':
      return True
    elif promotion.partner_rule_based_on == 'specific_customer_category':
      if self.partner_id.category_id.filtered(
          lambda c: c.id in promotion.customer_category_ids.ids):
        return True
    return False

  def _filter_promotion_basedon_customer_rule(self, promotions):
    lst = []
    for promotion in promotions.filtered(self._filter_basedon_customer_rule):
      lst.append({
          'id':
              promotion.id,
          'promotion':
              promotion.name,
          'analytic_tag_id':
              promotion.analytic_tag_id.id,
          'default_currency_id':
              promotion.default_currency_id,
          'currency_rate':
              self.pricelist_id.currency_id.compute(1, promotion.default_currency_id),
          'description':
              promotion.description,
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
              promotion.customer_category_ids.mapped('id')
              if promotion.customer_category_ids else [],
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
      })
    return lst

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
          'list_price': reward.product_id.with_context(pricelist=self.pricelist_id.id).price,
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

  def apply_promotion_order_lines(self, new_order, promotions_lst):
    discount = new_order['total_discount']
    promotions = filter(lambda promotion: promotion['applied_on'] == "order_lines", promotions_lst)
    potential_orders = list(
        map(
            lambda promotion: self._apply_promotion_order_lines_reward_by_discounts(
                promotion, new_order) if promotion['reward_by'] == 'discounts' else self.
            _apply_promotion_order_lines_reward_by_discounts_lines(promotion, new_order)
            if promotion['reward_by'] == 'discount_lines' else self.
            _apply_promotion_order_lines_reward_by_reward_product(promotion, new_order),
            promotions))
    if potential_orders and len(potential_orders) > 0:
      potential_orders.sort(key=lambda o: o['total_discount'], reverse=True)
      if discount == potential_orders[0]['total_discount']:
        return potential_orders[0]
      else:
        return self.apply_promotion_order_lines(potential_orders[0], promotions_lst)
    return new_order

  def _compute_total_discounts_amount(self, promotion, line):
    if promotion['discount_type'] == 'percentage':
      return (line['default_price'] * promotion['discount_percentage']) / 100
    else:
      return promotion['discount_fixed_amount'] * promotion['currency_rate']

  def _compute_total_discounts_percentage(self, promotion, line):
    if promotion['discount_type'] == 'percentage':
      return promotion['discount_percentage']
    else:
      return ((promotion['discount_fixed_amount'] * promotion['currency_rate']) *
              100) / line['default_price']

  def _apply_promotion_order_lines_reward_by_discounts(self, promotion, new_order):
    lines = []
    if promotion['product_rule_based_on'] == "all":
      lines = list(
          filter(lambda l: not l['is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
                 list(new_order['orderLines'].values())))
    elif promotion['product_rule_based_on'] == "specific_product_category":
      lines = list(
          filter(
              lambda l: l['categ_id'] in promotion['specific_categ_ids'] and not l['is_promotion']
              and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    elif promotion['product_rule_based_on'] == "specific_product_templates":
      lines = list(
          filter(
              lambda l: l['product_tmpl_id'] in promotion['specific_product_temp_ids'] and not l[
                  'is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    else:
      lines = list(
          filter(
              lambda l: l['product_id'] in promotion['specific_product_ids'] and not l[
                  'is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    lines.sort(key=lambda l: l['price'], reverse=True)
    if len(lines) >= promotion['min_quantity']:
      total_discount = reduce(
          lambda total, l: total + self._compute_total_discounts_amount(promotion, l), lines, 0)
      lines_after_promotion = map(
          lambda line: assoc_in(
              assoc_in(assoc_in(line, ['is_promotion'], True), ['promotion_id'], promotion['id']),
              ['discount'], self._compute_total_discounts_percentage(promotion, line)), lines)

      return assoc_in(
          assoc_in(
              new_order, ['orderLines'],
              reduce(lambda lines, line: assoc_in(lines, [line['index']], line),
                     lines_after_promotion, new_order['orderLines'])), ['total_discount'],
          new_order['total_discount'] + total_discount)
    return new_order

  def _apply_promotion_order_lines_reward_by_discounts_lines(self, promotion, new_order):
    lines = []
    if promotion['product_rule_based_on'] == "all":
      lines = list(
          filter(lambda l: not l['is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
                 list(new_order['orderLines'].values())))
    elif promotion['product_rule_based_on'] == "specific_product_category":
      lines = list(
          filter(
              lambda l: l['categ_id'] in promotion['specific_categ_ids'] and not l['is_promotion']
              and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    elif promotion['product_rule_based_on'] == "specific_product_templates":
      lines = list(
          filter(
              lambda l: l['product_tmpl_id'] in promotion['specific_product_temp_ids'] and not l[
                  'is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    else:
      lines = list(
          filter(
              lambda l: l['product_id'] in promotion['specific_product_ids'] and not l[
                  'is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    lines.sort(key=lambda l: l['price'], reverse=True)
    if len(lines) >= promotion['min_quantity']:
      discounts = promotion['product_discounts_ids']
      lines_to_be_promoted = lines[-int((promotion['min_quantity'])):]
      lines_to_be_discounted = lines_to_be_promoted[0:(len(discounts))]
      if len(lines_to_be_discounted) > 0:

        total_discount = 0
        for i, line in enumerate(lines_to_be_discounted):
          if discounts[i]['discount_type'] == 'percentage':
            total_discount = total_discount + (line['default_price'] * discounts[i]['amount']) / 100
          else:
            total_discount = total_discount + discounts[i]['amount'] * promotion['currency_rate']

        def _compute_discount_lines(discount, line):
          if discount['discount_type'] == 'percentage':
            return discount['amount']
          else:
            return ((discount['amount'] * promotion['currency_rate']) * 100) / line['default_price']

        lines_after_promotion = []
        for i, line in enumerate(lines_to_be_promoted):
          lines_after_promotion.append(
              assoc_in(
                  assoc_in(assoc_in(line, ['is_promotion'], True), ['promotion_id'],
                           promotion['id']), ['discount'],
                  _compute_discount_lines(discounts[i], line)
                  if i < len(discounts) else line['discount']))

        return assoc_in(
            assoc_in(
                new_order, ['orderLines'],
                reduce(lambda lines, line: assoc_in(lines, [line['index']], line),
                       lines_after_promotion, new_order['orderLines'])), ['total_discount'],
            new_order['total_discount'] + total_discount)
    return new_order

  def _apply_promotion_order_lines_reward_by_reward_product(self, promotion, new_order):
    lines = []
    if promotion['product_rule_based_on'] == "all":
      lines = list(
          filter(lambda l: not l['is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
                 list(new_order['orderLines'].values())))
    elif promotion['product_rule_based_on'] == "specific_product_category":
      lines = list(
          filter(
              lambda l: l['categ_id'] in promotion['specific_categ_ids'] and not l['is_promotion']
              and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    elif promotion['product_rule_based_on'] == "specific_product_templates":
      lines = list(
          filter(
              lambda l: l['product_tmpl_id'] in promotion['specific_product_temp_ids'] and not l[
                  'is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    else:
      lines = list(
          filter(
              lambda l: l['product_id'] in promotion['specific_product_ids'] and not l[
                  'is_promotion'] and l['discount'] == 0 and l['default_qty'] == 1,
              list(new_order['orderLines'].values())))
    lines.sort(key=lambda l: l['price'], reverse=True)
    if len(lines) >= promotion['min_quantity']:
      lines_to_be_discounted = []
      lines_to_be_promoted = lines[-int((promotion['min_quantity'])):]
      for reward in promotion['product_rewards_ids']:
        key = str(uuid.uuid1()) + "-reward"
        lines_to_be_discounted.append({
            'index': key,
            'product_id': reward['product_id'],
            'categ_id': 0,
            'product_tmpl_id': 0,
            'product_uom': reward['product_uom_id']['id'],
            'default_uom': reward['product_uom_id']['id'],
            'discount': 100,
            'price': reward['list_price'],
            'default_price': reward['list_price'],
            'qty': reward['qty'],
            'default_qty': reward['qty'],
            'is_promotion': True,
            'total_price': 0,
            'discount_amount': 0,
            'promotion_id': 0,
            'is_reward_product': True,
            'total_amount': 0
        })
      if len(lines_to_be_discounted) > 0:
        total_discount = reduce(lambda total, l: total + (l['default_price'] * l['default_qty']),
                                lines_to_be_discounted, 0)
        new_lines = [*lines_to_be_promoted, *lines_to_be_discounted]
        lines_after_promotion = map(
            lambda line: assoc_in(assoc_in(line, ['is_promotion'], True), ['promotion_id'],
                                  promotion['id']), new_lines)

        return assoc_in(
            assoc_in(
                new_order, ['orderLines'],
                reduce(lambda lines, line: assoc_in(lines, [line['index']], line),
                       lines_after_promotion, new_order['orderLines'])), ['total_discount'],
            new_order['total_discount'] + total_discount)
    return new_order

  def _apply_discount_on_total_order(self, new_order: list, promotions):
    promotions_lst = list(
        map(lambda promotion: self._calculate_total_order_promotion(new_order, promotion),
            filter(lambda promotion: promotion['applied_on'] == "total_order", promotions)))

    valid_promotion = list(filter(lambda p: p['valid'], promotions_lst))
    valid_promotion.sort(key=lambda p: p['discount'], reverse=True)
    if len(valid_promotion) > 0:
      promotion = valid_promotion[0]['promotion']
      discount = valid_promotion[0]['discount']
      product = promotion.global_discount_product_id
      new_order.append({
          'index': 'discount_product',
          'product_id': product.id,
          'categ_id': product.categ_id.id,
          'product_tmpl_id': product.product_tmpl_id.id,
          'product_uom': product.uom_id.id,
          'default_uom': product.uom_id.id,
          'discount': 0,
          'price': discount,
          'default_price': discount,
          'qty': 1,
          'default_qty': 1,
          'is_promotion': True,
          'total_price': 0,
          'discount_amount': 0,
          'promotion_id': promotion.id,
          'is_reward_product': True,
          'total_amount': 0
      })
    return new_order

  def _calculate_total_order_promotion(self, new_order, promotion):

    def calc_discount(promotion, base_to_discount):
      discount = 0
      if promotion['discount_type'] == "percentage":
        discount = (-promotion['discount_percentage'] / 100.0) * base_to_discount
      if promotion['discount_type'] == "fixed_amount":
        discount = promotion['discount_fixed_amount'] * promotion['currency_rate']
      return discount

    def _compute_total_line(line):
      total_before_discount = line['price'] * line['qty']
      discount_amount = (total_before_discount * line['discount']) / 100
      return assoc_in(
          assoc_in(assoc_in(line, ['discount_amount'], discount_amount), ['total_price'],
                   total_before_discount), ['total_amount'],
          total_before_discount - discount_amount)

    def compute_total_amount(order_lines_lst):
      return reduce(lambda total, item: total + (item['total_amount']), order_lines_lst, 0)

    if promotion['product_rule_based_on'] == "all":
      base_to_discount = compute_total_amount(map(_compute_total_line, new_order))

    elif promotion['product_rule_based_on'] == "specific_product_category":
      lines = list(
          filter(lambda line: line['categ_id'] in promotion['specific_categ_ids'], new_order))
      base_to_discount = compute_total_amount(map(_compute_total_line, lines))
    elif promotion['product_rule_based_on'] == "specific_product_templates":
      lines = list(
          filter(lambda line: line['categ_id'] in promotion['specific_product_temp_ids'],
                 new_order))
      base_to_discount = compute_total_amount(map(_compute_total_line, lines))
    else:
      lines = list(
          filter(lambda line: line['categ_id'] in promotion['specific_product_ids'], new_order))
      base_to_discount = compute_total_amount(map(_compute_total_line, lines))

    return {
        'promotion': promotion,
        'discount': calc_discount(promotion, base_to_discount),
        'valid': bool((promotion['min_amount'] * promotion['currency_rate']) <= base_to_discount)
    }


class SaleOrderLine(models.Model):
  _inherit = 'sale.order.line'

  promotion_id = fields.Many2one('sale.promotion', string='Promotion')
  is_reward_product = fields.Boolean(
      default=False, string="Flag used to reset data on clone Order in applying Promotion")

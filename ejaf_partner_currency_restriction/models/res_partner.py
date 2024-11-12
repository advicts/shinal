# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResPartnerInherit(models.Model):
  _inherit = 'res.partner'

  partner_currency_id = fields.Many2one('res.currency', string='Partner Currency')
  property_purchase_currency_id = fields.Many2one(
      'res.currency',
      string="Supplier Currency",
      company_dependent=True,
      related="partner_currency_id",
      store=1,
      help=
      "This currency will be used, instead of the default one, for purchases from the current partner"
  )

  @api.constrains('partner_currency_id', 'property_product_pricelist')
  def _constrains_partner_currency_id(self):
    for rec in self:
      if rec.partner_currency_id:
        if rec.property_product_pricelist.currency_id.id != rec.partner_currency_id.id:
          raise ValidationError(_('Partner currency should be the same currency on the price list'))

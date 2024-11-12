# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res = super(SaleOrderInherit, self).create(vals)
        for rec in res:
            if rec.partner_id and rec.partner_id.partner_currency_id and rec.currency_id != rec.partner_id.partner_currency_id:
                raise ValidationError(_('Transactions for this partner is allowed only in the %s currency.' % (rec.partner_id.partner_currency_id.name)))
        return res

    def write(self, vals):
        res = super(SaleOrderInherit, self).write(vals)
        for rec in self:
            if rec.partner_id and rec.partner_id.partner_currency_id and rec.currency_id != rec.partner_id.partner_currency_id:
                raise ValidationError(_('Transactions for this partner is allowed only in the %s currency.' % (
                    rec.partner_id.partner_currency_id.name)))
        return res
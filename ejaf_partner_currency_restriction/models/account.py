# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveInherit, self).create(vals_list)
        for rec in res:
            if rec.move_type != 'entry' and rec.partner_id and rec.partner_id.partner_currency_id and rec.currency_id != rec.partner_id.partner_currency_id:
                raise ValidationError(_('Transactions for this partner is allowed only in the %s currency.' % (rec.partner_id.partner_currency_id.name)))
        return res

    def write(self, vals):
        res = super(AccountMoveInherit, self).write(vals)
        for rec in self:
            if rec.move_type != 'entry' and rec.partner_id and rec.partner_id.partner_currency_id and rec.currency_id != rec.partner_id.partner_currency_id:
                raise ValidationError(_('Transactions for this partner is allowed only in the %s currency.' % (
                    rec.partner_id.partner_currency_id.name)))
        return res


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountPaymentInherit, self).create(vals_list)
        for rec in res:
            if rec.partner_id and rec.partner_id.partner_currency_id and rec.currency_id != rec.partner_id.partner_currency_id:
                raise ValidationError(_('Transactions for this partner is allowed only in the %s currency.' % (
                    rec.partner_id.partner_currency_id.name)))
        return res

    def write(self, vals):
        res = super(AccountPaymentInherit, self).write(vals)
        for rec in self:
            if rec.partner_id and rec.partner_id.partner_currency_id and rec.currency_id != rec.partner_id.partner_currency_id:
                raise ValidationError(_('Transactions for this partner is allowed only in the %s currency.' % (
                    rec.partner_id.partner_currency_id.name)))
        return res

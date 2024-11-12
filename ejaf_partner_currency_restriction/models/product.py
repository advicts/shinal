# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.onchange('name')
    def onchange_partner(self):
        if self.name.partner_currency_id:
            self.currency_id = self.name.partner_currency_id

    @api.model
    def create(self, vals):
        res = super(SupplierInfo, self).create(vals)
        if vals.get('currency_id', False):
            for rec in res:
                if rec.name and rec.name.partner_currency_id and rec.currency_id != rec.name.partner_currency_id:
                    raise ValidationError(_('Vendor pricelists for this partner is allowed only in the %s currency.' % (
                        rec.name.partner_currency_id.name)))
        return res

    def write(self, vals):
        res = super(SupplierInfo, self).write(vals)
        if vals.get('currency_id', False):
            for rec in self:
                if rec.name and rec.name.partner_currency_id and rec.currency_id != rec.name.partner_currency_id:
                    raise ValidationError(_('Vendor pricelists for this partner is allowed only in the %s currency.' % (
                        rec.name.partner_currency_id.name)))
        return res
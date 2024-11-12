# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_limit_rule = fields.Selection([('credit_limit', 'Credit Limit'),('credit_balance', 'Credit Balance'),('cash', 'Cash')], string='Customer Limit Rule',default="cash")
    # Created new field to avoid conflicts
    customer_limit = fields.Float(
        string='Customer Limit', help='Customer limit specific to this partner.',
        groups='account.group_account_invoice,account.group_account_readonly',default=1000,
        company_dependent=True, copy=False, readonly=False)
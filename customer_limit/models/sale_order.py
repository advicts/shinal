# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"


    payment_type = fields.Selection([('debit', 'Debit Sales'), ('cash', 'Cash Sales')], string='Payment Type',compute="_compute_payment_type")


    def _compute_payment_type(self):
        for rec in self:
            if rec.partner_id.customer_limit_rule == 'cash':
                rec.payment_type = 'cash'
            else:
                rec.payment_type = 'debit'


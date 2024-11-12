from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_type = fields.Selection([('debit', 'Debit Sales'), ('cash', 'Cash Sales')], string='Payment Type',compute="_compute_payment_type")


    def _compute_payment_type(self):
        for rec in self:
            if rec.partner_id.customer_limit_rule == 'cash':
                rec.payment_type = 'cash'
            else:
                rec.payment_type = 'debit'


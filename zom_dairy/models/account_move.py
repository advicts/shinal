import logging
from shutil import move
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _auto_assign_outstanding_line(self):
      for rec in self:
        lines = (rec._compute_payments_to_reconcile())
        while ((lines and len(lines['content'])>0) and rec.amount_residual>0):
              rec.js_assign_outstanding_line(lines['content'][0]["id"])
              lines = (rec._compute_payments_to_reconcile())



    def _compute_payments_to_reconcile(self):
      for move in self:

        if move.state != 'posted' \
                or move.payment_state not in ('not_paid', 'partial') \
                or not move.is_invoice(include_receipts=True):
            continue

        pay_term_lines = move.line_ids\
            .filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

        domain = [
            ('account_id', 'in', pay_term_lines.account_id.ids),
            ('parent_state', '=', 'posted'),
            ('partner_id', '=', move.commercial_partner_id.id),
            ('reconciled', '=', False),
            '|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
        ]

        payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

        if move.is_inbound():
            domain.append(('balance', '<', 0.0))
            payments_widget_vals['title'] = _('Outstanding credits')
        else:
            domain.append(('balance', '>', 0.0))
            payments_widget_vals['title'] = _('Outstanding debits')

        for line in self.env['account.move.line'].search(domain):

            if line.currency_id == move.currency_id:
                # Same foreign currency.
                amount = abs(line.amount_residual_currency)
            else:
                # Different foreign currencies.
                amount = move.company_currency_id._convert(
                    abs(line.amount_residual),
                    move.currency_id,
                    move.company_id,
                    line.date,
                )

            if move.currency_id.is_zero(amount):
                continue

            payments_widget_vals['content'].append({
                'journal_name': line.ref or line.move_id.name,
                'amount': amount,
                'currency': move.currency_id.symbol,
                'id': line.id,
                'move_id': line.move_id.id,
                'position': move.currency_id.position,
                'digits': [69, move.currency_id.decimal_places],
                'payment_date': fields.Date.to_string(line.date),
            })

        if not payments_widget_vals['content']:
            continue

        return payments_widget_vals


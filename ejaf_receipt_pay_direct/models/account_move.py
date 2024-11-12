# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, html_escape


#forbidden fields
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')


class AccountMove(models.Model):
    _inherit = "account.move"

    move_payment_type = fields.Selection([
        ('direct', 'Pay Directly'),
        ('later', 'Pay Later'),
    ], string='Payment Type', default='later', tracking=True)

    @api.onchange('move_payment_type')
    def onchange_move_payment_type(self):
        if self.move_payment_type == 'direct':
            self.invoice_payment_term_id = False
            js = self.env['account.journal'].search([('company_id', '=', self.company_id.id), ('type', 'in', ['bank', 'cash'])])
            if self.journal_id.type not in ['bank', 'cash']:
                self.journal_id = js[0] if js else False
            return {
                'domain': {
                    'journal_id': [('type', 'in', ['bank', 'cash'])]
                }
            }
        else:
            if self.journal_id.type in ['bank', 'cash']:
                self.journal_id = self._get_default_journal()
            if self.invoice_filter_type_domain:
                domain = [('type', '=', self.invoice_filter_type_domain)]
            else:
                domain = [('type', '!=', False)]
            return {
                'domain': {
                    'journal_id': domain
                }
            }

    def action_post(self):
        # OVERRIDE
        for rec in self:
            if not rec.is_invoice(include_receipts=True):
                continue
            if rec.move_payment_type == 'direct':
                if not rec.journal_id.default_account_id:
                    raise ValidationError(_('Please define the default account in journal.'))
                for line in rec.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    account_id = rec.journal_id.default_account_id
                    line.origin_payment_term_account_id = line.account_id.id
                    line.account_id = account_id.id

        res = super(AccountMove, self).action_post()

        for rec in self:
            if not rec.is_invoice(include_receipts=True):
                continue
            if rec.move_payment_type == 'direct':
                rec.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable') and float_compare(line.debit, 0.0, 5) == 0 and float_compare(line.credit, 0.0, 5) == 0).with_context(force_delete=True).sudo().unlink()
        return res

    def button_draft(self):
        # OVERRIDE
        for rec in self:
            if not rec.is_invoice(include_receipts=True):
                continue
            if rec.move_payment_type == 'direct':
                for line in rec.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('liquidity')):
                    account_id = line.origin_payment_term_account_id
                    if account_id:
                        line.account_id = account_id.id
                        line.origin_payment_term_account_id = False
        return super(AccountMove, self).button_draft()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    origin_payment_term_account_id = fields.Many2one('account.account', copy=False)

    def write(self, vals):
        # OVERRIDE to skip account_id type constraint
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')
        PROTECTED_FIELDS_TAX_LOCK_DATE = ['debit', 'credit', 'tax_line_id', 'tax_ids', 'tax_tag_ids']
        PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + ['account_id', 'journal_id', 'amount_currency', 'currency_id', 'partner_id']
        PROTECTED_FIELDS_RECONCILIATION = ('account_id', 'date', 'debit', 'credit', 'amount_currency', 'currency_id')

        account_to_write = self.env['account.account'].browse(vals['account_id']) if 'account_id' in vals else None

        # Check writing a deprecated account.
        if account_to_write and account_to_write.deprecated:
            raise UserError(_('You cannot use a deprecated account.'))

        for line in self:
            if line.parent_state == 'posted':
                if line.move_id.restrict_mode_hash_table and set(vals).intersection(INTEGRITY_HASH_LINE_FIELDS):
                    raise UserError(_("You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(INTEGRITY_HASH_LINE_FIELDS))
                if any(key in vals for key in ('tax_ids', 'tax_line_ids')):
                    raise UserError(_('You cannot modify the taxes related to a posted journal item, you should reset the journal entry to draft to do so.'))

            # Check the lock date.
            if line.parent_state == 'posted' and any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_LOCK_DATE):
                line.move_id._check_fiscalyear_lock_date()

            # Check the tax lock date.
            if line.parent_state == 'posted' and any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_TAX_LOCK_DATE):
                line._check_tax_lock_date()

            # Check the reconciliation.
            if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_RECONCILIATION):
                line._check_reconciliation()

            # Check switching receivable / payable accounts.
            # if account_to_write:
            #     account_type = line.account_id.user_type_id.type
            #     if line.move_id.is_sale_document(include_receipts=True):
            #         if (account_type == 'receivable' and account_to_write.user_type_id.type != account_type) \
            #                 or (account_type != 'receivable' and account_to_write.user_type_id.type == 'receivable'):
            #             raise UserError(_("You can only set an account having the receivable type on payment terms lines for customer invoice."))
            #     if line.move_id.is_purchase_document(include_receipts=True):
            #         if (account_type == 'payable' and account_to_write.user_type_id.type != account_type) \
            #                 or (account_type != 'payable' and account_to_write.user_type_id.type == 'payable'):
            #             raise UserError(_("You can only set an account having the payable type on payment terms lines for vendor bill."))

        # Tracking stuff can be skipped for perfs using tracking_disable context key
        if not self.env.context.get('tracking_disable', False):
            # Get all tracked fields (without related fields because these fields must be manage on their own model)
            tracking_fields = []
            for value in vals:
                field = self._fields[value]
                if hasattr(field, 'related') and field.related:
                    continue # We don't want to track related field.
                if hasattr(field, 'tracking') and field.tracking:
                    tracking_fields.append(value)
            ref_fields = self.env['account.move.line'].fields_get(tracking_fields)

            # Get initial values for each line
            move_initial_values = {}
            for line in self.filtered(lambda l: l.move_id.posted_before): # Only lines with posted once move.
                for field in tracking_fields:
                    # Group initial values by move_id
                    if line.move_id.id not in move_initial_values:
                        move_initial_values[line.move_id.id] = {}
                    move_initial_values[line.move_id.id].update({field: line[field]})

        result = True
        for line in self:
            cleaned_vals = line.move_id._cleanup_write_orm_values(line, vals)
            if not cleaned_vals:
                continue

            # Auto-fill amount_currency if working in single-currency.
            if 'currency_id' not in cleaned_vals \
                and line.currency_id == line.company_currency_id \
                and any(field_name in cleaned_vals for field_name in ('debit', 'credit')):
                cleaned_vals.update({
                    'amount_currency': vals.get('debit', 0.0) - vals.get('credit', 0.0),
                })

            result |= super(models.Model, line).write(cleaned_vals)

            if not line.move_id.is_invoice(include_receipts=True):
                continue

            # Ensure consistency between accounting & business fields.
            # As we can't express such synchronization as computed fields without cycling, we need to do it both
            # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
            # business [resp. accounting] fields are recomputed.
            if any(field in cleaned_vals for field in ACCOUNTING_FIELDS):
                price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
                to_write = line._get_fields_onchange_balance(price_subtotal=price_subtotal)
                to_write.update(line._get_price_total_and_subtotal(
                    price_unit=to_write.get('price_unit', line.price_unit),
                    quantity=to_write.get('quantity', line.quantity),
                    discount=to_write.get('discount', line.discount),
                ))
                result |= super(models.Model, line).write(to_write)
            elif any(field in cleaned_vals for field in BUSINESS_FIELDS):
                to_write = line._get_price_total_and_subtotal()
                to_write.update(line._get_fields_onchange_subtotal(
                    price_subtotal=to_write['price_subtotal'],
                ))
                result |= super(models.Model, line).write(to_write)

        # Check total_debit == total_credit in the related moves.
        if self._context.get('check_move_validity', True):
            self.mapped('move_id')._check_balanced()

        self.mapped('move_id')._synchronize_business_models({'line_ids'})

        if not self.env.context.get('tracking_disable', False):
            # Log changes to move lines on each move
            for move_id, modified_lines in move_initial_values.items():
                for line in self.filtered(lambda l: l.move_id.id == move_id):
                    tracking_value_ids = line._mail_track(ref_fields, modified_lines)[1]
                    if tracking_value_ids:
                        msg = f"{html_escape(_('Journal Item'))} <a href=# data-oe-model=account.move.line data-oe-id={line.id}>#{line.id}</a> {html_escape(_('updated'))}"
                        line.move_id._message_log(
                            body=msg,
                            tracking_value_ids=tracking_value_ids
                        )

        return result

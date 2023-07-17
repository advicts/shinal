# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_intercompany_transfer = fields.Boolean('Intercompany Transfer')
    paired_intercompany_payment_id = fields.Many2one('account.payment', 'Paired Intercompany Payment')

    def action_post(self):
        self.move_id._post(soft=False)
        if self.is_intercompany_transfer:
            self._create_paired_intercompany_transfer_payment()
        else:
            self.filtered(
                lambda pay: pay.is_internal_transfer or pay.is_intercompany_transfer and not pay.paired_internal_transfer_payment_id
            )._create_paired_internal_transfer_payment()

    def _create_paired_intercompany_transfer_payment(self):

        for payment in self:
            company = self.env.user.company_id
            if not payment.partner_id.ref_company_ids.journal_code or not payment.partner_id.ref_company_ids.account_code:
                raise UserError("Please set the journal code and account code for the the company you are using to transfer money.")
            
            journal_id = self.env['account.journal'].sudo().search([('company_id', '=', payment.partner_id.ref_company_ids.id), ('code', '=', payment.partner_id.ref_company_ids.journal_code),])
            destination_account_id = self.env['account.account'].sudo().search([('company_id', '=', payment.partner_id.ref_company_ids.id), ('code', '=', payment.partner_id.ref_company_ids.account_code),])
            
            paired_payment = payment.sudo().copy({
                'company_id': payment.partner_id.ref_company_ids.id,
                'partner_id': company.partner_id.id,
                'destination_account_id': destination_account_id.id,
                'journal_id': journal_id.id,
                'payment_type': 'outbound' if payment.payment_type == 'outbound' else 'inbound',
                'move_id': None,
                'ref': payment.ref,
                'paired_intercompany_payment_id': payment.id,
                'date': payment.date,
            })
            paired_payment.move_id._post(soft=False)
            payment.paired_intercompany_payment_id = paired_payment

            body = _(
                "This payment has been created from %s",
                payment._get_html_link(),
            )
            paired_payment.message_post(body=body)
            body = _(
                "A second payment has been created: %s",
                paired_payment._get_html_link(),
            )
            payment.message_post(body=body)

            lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id and not l.reconciled)
            lines.reconcile()


class ResCompany(models.Model):
    _inherit = 'res.company'

    journal_code = fields.Char(string='Journal Code')
    account_code = fields.Char(string='Account Code')

    @api.constrains('account_code')
    def _check_account_code(self):
        for company in self:
            if company.account_code:
                account_code_count = self.env['account.account'].sudo().search_count([('code', '=', company.account_code), ('company_id', '=', company.id)])
                if account_code_count < 1:
                    raise UserError(_('There is no Account with this Code!'))
                
    @api.constrains('journal_code')
    def _check_journal_code(self):
        for company in self:
            if company.journal_code:
                journal_code_count = self.env['account.journal'].sudo().search_count([('code', '=', company.journal_code), ('company_id', '=', company.id)])
                if journal_code_count < 1:
                    raise UserError(_('There is no Journal with this Code!'))
        
        

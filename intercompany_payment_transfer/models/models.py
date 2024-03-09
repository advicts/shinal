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
        res=super(AccountPayment, self).action_post()
        if self.is_intercompany_transfer:
            self._create_paired_intercompany_transfer_payment()
     

    def _create_paired_intercompany_transfer_payment(self):

        for payment in self:
            company = payment.company_id
            receiver_company = payment.partner_id.ref_company_ids

            if not receiver_company.journal_code:
                raise UserError("Please set the journal code for the company you are transferring money to.")

            # Get the journal for the receiving company
            journal = self.env['account.journal'].sudo().search([('company_id', '=', receiver_company.id), ('code', '=', receiver_company.journal_code)], limit=1)
            if not journal:
                raise UserError("Journal not found for the receiving company.")
            
            amount = payment.amount
            if payment.currency_id != journal.currency_id:
                amount = journal.currency_id.sudo()._convert(amount, journal.currency_id, receiver_company.id, payment.date)

            paired_payment = self.env['account.payment'].sudo().create({
                'company_id': receiver_company.id,
                'partner_id': company.partner_id.id,
                'is_intercompany_transfer': payment.is_intercompany_transfer,
                'amount': payment.amount,
                'journal_id': journal.id,
                'currency_id': journal.currency_id.id,
                'payment_type': payment.payment_type == 'outbound' and 'inbound' or 'outbound',
                'move_id': None,
                'ref': payment.ref,
                'paired_intercompany_payment_id': payment.id,
                'date': payment.date,
            })

            payment.paired_intercompany_payment_id = paired_payment

            body = _('This payment has been created from <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (payment.id, payment.name)
            paired_payment.message_post(body=body)
            body = _('A second payment has been created: <a href=# data-oe-model=account.payment data-oe-id=%d>%s</a>') % (paired_payment.id, paired_payment.name)
            payment.message_post(body=body)



class ResCompany(models.Model):
    _inherit = 'res.company'

    journal_code = fields.Char(string='Journal Code')
                
    @api.constrains('journal_code')
    def _check_journal_code(self):
        for company in self:
            if company.journal_code:
                journal_code_count = self.env['account.journal'].sudo().search_count([('code', '=', company.journal_code), ('company_id', '=', company.id)])
                if journal_code_count < 1:
                    raise UserError(_('There is no Journal with this Code!'))
        
        

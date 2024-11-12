# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(
        selection_add=[('approved', 'Approved'),
                       ('rejected', 'Rejected')],
        ondelete={'approved': 'set default', 'rejected': 'set default'})


class AccountPayment(models.Model):
    _inherit = "account.payment"
    _inherits = {'account.move': 'move_id'}

    is_approver = fields.Boolean(compute='_check_is_approver', readonly=True)
    show_post = fields.Boolean(compute='_check_show_post', readonly=False)

    @api.depends('is_approver', 'state')
    def _check_show_post(self):
        for record in self:
            record.show_post = True if (not record.is_approver and record.state == 'draft') or (
                    record.is_approver and record.state == 'approved') else False

    @api.depends('payment_type', 'amount', 'date', 'currency_id')
    def _check_is_approver(self):
        for record in self:
            approval = self.env['ir.config_parameter'].sudo().get_param(
                'ejaf_account_payment_approval.payment_approval')
            approver_id = int(self.env['ir.config_parameter'].sudo().get_param(
                'ejaf_account_payment_approval.approval_user_id'))
            payment_type = self.env['ir.config_parameter'].sudo().get_param(
                'ejaf_account_payment_approval.payment_type')
            limit_amount = float(self.env['ir.config_parameter'].sudo().get_param(
                'ejaf_account_payment_approval.approval_amount'))
            payment_currency_id = int(self.env['ir.config_parameter'].sudo().get_param(
                'ejaf_account_payment_approval.approval_currency_id'))
            payment_amount = record.amount
            if payment_currency_id:
                if record.currency_id and record.currency_id.id != payment_currency_id:
                    currency_id = self.env['res.currency'].browse(payment_currency_id)
                    payment_amount = record.currency_id._convert(
                        record.amount, currency_id, record.company_id,
                        record.date or fields.Date.today(), round=True)
            record.is_approver = True if self.env.user.id == approver_id and approval and payment_type == record.payment_type and payment_amount > limit_amount else False

    def approve_transfer(self):
        for record in self:
            record.write({'state': 'approved'})

    def reject_transfer(self):
        for record in self:
            record.write({'state': 'rejected'})

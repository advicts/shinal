# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(selection_add=[
        ('approvals', 'Waiting Approvals'),
        ('amount_limitation', 'Amount Limit to Approve'),
    ])
    approval_allowed = fields.Boolean(compute='_check_approval_access')
    next_approval_level_id = fields.Many2one('po.approval.level', string='Next Approval Level',
                                             compute='get_next_approval_level', store=1)
    last_approved_level_id = fields.Many2one('po.approval.level', string='Approved by Level', tracking=True, copy=False)
    amount_limit_approval_allowed = fields.Boolean(compute='_check_approval_access')
    multi_approval = fields.Boolean(compute='_check_approval_access')
    order_limit_exceeded = fields.Boolean(compute='_check_order_amount_limit')

    def get_approval_levels_list(self):
        self.ensure_one()
        approvals_list = []
        if self.company_id.po_multi_approval:
            approval_levels = self.env['po.approval.level'].search([('company_id', '=', self.company_id.id)])
            for approval_level in approval_levels:
                approvals_list.append({
                    'level': approval_level,
                    'level_id': approval_level.id,
                    'access_type':approval_level.access_type,
                    'group_ids': approval_level.group_ids if approval_level.access_type == 'groups' else False,
                    'user_ids': approval_level.user_ids if approval_level.access_type == 'users' else False,
                })
        return approvals_list

    @api.depends('amount_total', 'company_id', 'company_id.po_double_validation',
                 'company_id.po_double_validation_amount')
    def _check_order_amount_limit(self):
        for order in self:
            if order.company_id.po_double_validation == 'two_step' \
                and float_compare(order.amount_total,
                      self.env.company.currency_id._convert(
                          order.company_id.po_double_validation_amount,
                          order.currency_id,
                          order.company_id,
                          order.date_order or fields.Date.today()),
                      5) >= 0:
                order.order_limit_exceeded = True
            else:
                order.order_limit_exceeded = False

    @api.depends('last_approved_level_id', 'state')
    def get_next_approval_level(self):
        for order in self:
            next_approval_level_id = False
            approvals_list = order.get_approval_levels_list()
            approvals_length = len(approvals_list) - 1
            for index, x in enumerate(approvals_list):

                # set first approval level if it's not set
                if index == 0 and not order.last_approved_level_id and order.state in ['draft', 'sent', 'approvals']:
                    next_approval_level_id = approvals_list[index]['level_id']
                    break

                if x['level'] == order.last_approved_level_id:
                    # check if it's the last approval level, or update the next po approval level
                    if index == approvals_length:
                        # it's the last approval level
                        next_approval_level_id = False
                    else:
                        next_approval_level_id = approvals_list[index + 1]['level_id']
                    # break after finding the index of the last approved level
                    break

            order.next_approval_level_id = next_approval_level_id

    @api.depends('state', 'company_id', 'company_id.po_multi_approval', 'company_id.po_limit_approval_group_ids')
    def _check_approval_access(self):
        '''
        Check both the current user approval access for the current PO state,
        and the approval access for exceeding the amount limit
        :return:
        '''
        for order in self:
            # check amount limit approval
            amount_limit_approval_allowed = False
            if order.company_id.po_limit_approval_group_ids:
                for group in order.company_id.po_limit_approval_group_ids:
                    if group in self.env.user.groups_id:
                        amount_limit_approval_allowed = True
                        break

            # check multi level approval
            if order.company_id.po_multi_approval:
                multi_approval = True
                approval_allowed = False
                approvals_list = order.get_approval_levels_list()
                index = 0
                for approval_elem in approvals_list:
                    # if it's the first level approval, and po is draft or sent, allow level groups users to approve
                    if order.state in ['draft', 'sent'] and index == 0:
                        if approval_elem['access_type'] == 'groups':
                            for group in approval_elem['group_ids']:
                                if group in self.env.user.groups_id:
                                    approval_allowed = True
                                    break
                        else:
                            for user in approval_elem['user_ids']:
                                if user == self.env.user:
                                    approval_allowed = True
                                    break

                    # check the next levels
                    if order.state in ['approvals'] and order.next_approval_level_id == approval_elem['level']:
                        if approval_elem['access_type'] == 'groups':
                            for group in approval_elem['group_ids']:
                                if group in self.env.user.groups_id:
                                    approval_allowed = True
                                    break
                        else:
                            for user in approval_elem['user_ids']:
                                if user == self.env.user:
                                    approval_allowed = True
                                    break

                    # break if approval allowed, no need to check other levels
                    if approval_allowed:
                        break

                    index += 1
            else:
                multi_approval = False
                approval_allowed = False

            order.approval_allowed = approval_allowed
            order.multi_approval = multi_approval
            order.amount_limit_approval_allowed = amount_limit_approval_allowed

    def action_multi_approval(self):
        for order in self:
            approvals_list = order.get_approval_levels_list()

            # if multiple levels move po to approvals state else check amount limit and confirm
            if order.state in ['draft', 'sent'] and len(approvals_list) > 1:
                order.write({'last_approved_level_id': approvals_list[0]['level_id']})
                order.write({'state': 'approvals'})
            elif order.state in ['approvals'] and approvals_list:
                # get the index of the next approval level
                approvals_length = len(approvals_list) - 1
                for index, x in enumerate(approvals_list):
                    if x['level'] == order.next_approval_level_id:
                        # check if it's the last approval level, or update the next po approval level
                        if index == approvals_length:
                            # it's the last approval level
                            # check amount limit before final approve
                            if order.order_limit_exceeded:
                                order.write({'last_approved_level_id': approvals_list[index]['level_id']})
                                order.write({'state': 'amount_limitation'})
                            else:
                                order.write({'last_approved_level_id': approvals_list[index]['level_id']})
                                order.with_context(direct_approve=True).button_confirm()
                        else:
                            order.write({'last_approved_level_id': approvals_list[index]['level_id']})
                            order.write({'state': 'approvals'})

                        # break after finding the index of the next approval level
                        break
            else:
                # check amount limit before final approve
                if order.order_limit_exceeded:
                    order.write({'state': 'amount_limitation'})
                else:
                    order.with_context(direct_approve=True).button_confirm()

    def button_draft(self):
        res = super(PurchaseOrderInherit, self).button_draft()
        self.write({'last_approved_level_id': False})
        return res

    def button_confirm(self):
        res = super(PurchaseOrderInherit, self).button_confirm()
        if self._context.get('direct_approve', False):
            for order in self:
                order.button_approve()
        return res
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class POApprovalLevel(models.Model):
    _inherit = 'po.approval.level'

    group_user_ids = fields.Many2many('res.users', 'level_users_rel', 'level_id', 'group_user_id',
                                      compute='get_group_users', store=1)
    to_notify_user_ids = fields.Many2many('res.users', 'level_user_rel', 'level_id', 'user_id',
                                          string='Users to Notify')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id,
                                  required=1)
    amount_from = fields.Monetary('From')
    amount_to = fields.Monetary('To')

    @api.constrains('amount_from', 'amount_to')
    def check_amounts(self):
        if self.filtered(lambda l: l.amount_from > l.amount_to):
            raise ValidationError(_('The amount from must be less than the amount to.'))

        if self.filtered(lambda l: l.amount_from < 0 or l.amount_to < 0):
            raise ValidationError(_('The amount from / to should be strictly positive.'))

    @api.depends('group_ids', 'group_ids.users')
    def get_group_users(self):
        for rec in self:
            rec.group_user_ids = [(6, 0, rec.group_ids.mapped('users').ids)]

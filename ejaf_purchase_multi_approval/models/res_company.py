# -*- coding: utf-8 -*-

from odoo import fields, models


class CompanyInherit(models.Model):
    _inherit = 'res.company'

    po_multi_approval = fields.Boolean(string='Purchase Order Multi Approvals')
    po_limit_approval_group_ids = fields.Many2many('res.groups', 'company_po_limit_approval_rel', 'company_id',
                                                   'group_id', string='Amount Limit Approval Groups')
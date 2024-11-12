# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    po_multi_approval = fields.Boolean(related='company_id.po_multi_approval', string='Purchase Order Multi Approvals', readonly=False)
    group_po_multi_approval_level = fields.Boolean(string='PO Approval Levels', implied_group='ejaf_purchase_multi_approval.group_po_multi_approval_level')
    po_limit_approval_group_ids = fields.Many2many('res.groups', related='company_id.po_limit_approval_group_ids', string='Amount Limit Approval Groups', readonly=False)

    @api.onchange('po_multi_approval')
    def _onchange_po_multi_approval(self):
        if self.po_multi_approval:
            self.group_po_multi_approval_level = True
        else:
            self.group_po_multi_approval_level = False
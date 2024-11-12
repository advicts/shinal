# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    rel_cust_invoice_id = fields.Many2one('account.move', 'Rel. Customer Invoice')
    receipts_count = fields.Integer(compute='get_receipts_count')

    def get_receipts_count(self):
        for rec in self:
            rec.receipts_count = self.env['account.move'].search_count([('rel_cust_invoice_id', '=', rec.id)])

    def add_vendor_receipt(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_receipt_type")
        action['context'] = {'default_move_type': 'in_receipt', 'default_rel_cust_invoice_id': self.id, 'default_partner_id': self.partner_id.id}
        action['domain'] = [('move_type', '=', 'in_receipt'), ('rel_cust_invoice_id', '=', self.id)]
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        return action

    def open_vendor_receipt(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_receipt_type")
        action['context'] = {'default_move_type': 'in_receipt', 'default_rel_cust_invoice_id': self.id, 'default_partner_id': self.partner_id.id}
        action['domain'] = [('move_type', '=', 'in_receipt'), ('rel_cust_invoice_id', '=', self.id)]
        return action


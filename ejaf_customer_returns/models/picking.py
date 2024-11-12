# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_customer_return = fields.Boolean()
    credit_note_id = fields.Many2one('account.move', copy=False)
    
    def get_default_currency(self):
        if self.partner_id.partner_currency_id.id:
            return self.partner_id.partner_currency_id.id
        else:
            return self.env.company.currency_id.id

    currency_id = fields.Many2one('res.currency', string= 'Currency',default=get_default_currency)

    @api.model
    def create(self, vals):
        if vals.get('is_customer_return'):
            defaults = self.default_get(['name', 'picking_type_id'])

            picking_type = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', defaults.get('picking_type_id')))
            vals['name'] = picking_type.warehouse_id.code + '/' + self.env['ir.sequence'].next_by_code(
                'customer.returns')
        return super(StockPicking, self).create(vals)

    def action_view_refund_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Credit Notes'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', '=', self.credit_note_id.id)],
            'context': dict(self._context, default_partner_id=self.partner_id.id, default_move_type='out_refund',
                            create=False, edit=True)
        }

    def create_refund_invoice(self):
        inv_obj = self.env['account.move']
        for pick in self:
            inv_type = 'out_refund'
            inv_vals = {'move_type': inv_type, 'partner_id': pick.partner_id.id,
                        'invoice_line_ids': [],
                        'currency_id':pick.currency_id.id,
                        'picking_created_from': pick.id,
                        }
            for line in pick.move_lines:
                inv_vals['invoice_line_ids'] += [(0, 0, line._prepare_refund_line())]
            if inv_vals['invoice_line_ids']:
                inv_id = inv_obj.create(inv_vals)
                pick.credit_note_id = inv_id.id
        return True


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_refund_line(self):
        self.ensure_one()
        product_move_line_ids = self.env['account.move.line'].sudo().search(
            [('move_id.partner_id', '=', self.picking_id.partner_id.id),
             ('move_id.move_type', '=', 'out_invoice'),
             ('product_id', '=', self.product_id.id),
             ('parent_state', '=', 'posted'),
             ('exclude_from_invoice_tab', '=', False),
             ])
        sale_price = 0.0
        discount_value = 0.0
        if product_move_line_ids:
            if self.company_id.customer_return_price_type == 'avg':
                total_qty = 0
                same_uom_product_move_line_ids = product_move_line_ids.filtered(
                    lambda l: l.product_uom_id == self.product_uom)
                other_product_move_line_ids = product_move_line_ids - same_uom_product_move_line_ids
                total_qty += sum(same_uom_product_move_line_ids.mapped("quantity"))
                for l in other_product_move_line_ids:
                    total_qty += l.product_uom_id._compute_quantity(l.quantity, self.product_uom)
                if float_compare(total_qty, 0, 5) > 0:
                    sale_price = abs(sum(product_move_line_ids.mapped("balance"))) / total_qty
            else:
                qty = product_move_line_ids[0].product_uom_id._compute_quantity(product_move_line_ids[0].quantity,
                                                                                self.product_uom)
                if float_compare(qty, 0, 5) > 0:
                    # check if discount applied get last price before discount
                    if 'sub_total_before_discount' in self.env['account.move.line']._fields:
                        sale_price = abs(product_move_line_ids[0].sub_total_before_discount / qty)
                        discount_value = product_move_line_ids[0].discount
                    else:
                        sale_price = abs(product_move_line_ids[0].balance / qty)
        refund_line_vals = {
            'product_id': self.product_id.id,
            'quantity': self.product_uom_qty,
            'product_uom_id': self.product_uom.id,
            'currency_id':self.picking_id.currency_id.id,
            'price_unit': self.env.company.currency_id._convert(
                        sale_price, self.picking_id.currency_id, self.company_id,
                        self.picking_id.date_done or fields.Date.today(), round=False),
            'account_id': self.product_id.product_tmpl_id.get_product_accounts()['income'].id,
            'display_type': False,
            'sale_line_ids': [(4, self.sale_line_id.id)] if self.sale_line_id else [],
        }
        if discount_value > 0.0 and self.company_id.customer_return_price_type == 'last_invoice':
            refund_line_vals['discount'] = discount_value
        return refund_line_vals

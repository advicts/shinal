# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Faslu Rahman(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
# from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
            # order.update({
            #     'amount_untaxed': amount_untaxed,
            #     'amount_tax': amount_tax,
            #     'amount_discount': amount_discount,
            #     'amount_total': amount_untaxed + amount_tax,
            # })

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,
                                     states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'), track_visibility='always')

    # @api.onchange('discount_type', 'discount_rate', 'order_line')
    # def supply_rate(self):

    #     for order in self:
    #         if order.discount_type == 'percent':
    #             for line in order.order_line:
    #                 line.discount = order.discount_rate
    #         else:
    #             total = discount = 0.0
    #             for line in order.order_line:
    #                 total += round((line.product_uom_qty * line.price_unit))
    #             if order.discount_rate != 0:
    #                 discount = (order.discount_rate / total) * 100
    #             else:
    #                 discount = order.discount_rate
    #             for line in order.order_line:
    #                 line.discount = discount

    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate,
        })
        return invoice_vals

    def button_dummy(self):

        self.supply_rate()
        return True

    def _get_invoiceable_lines(self, final=False,iscash=False):
        # raise UserError(str(iscash))
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.order_line.filtered(lambda r: r.product_id.x_studio_iscash == False):
            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)

        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)

    def _create_invoices(self, grouped=False, final=False, date=None):
            raise UserError(str(iscash))
        # for inv_count in 2:
        #     iscash=True
        #     if inv_count==2:
        #         iscash=False
        #     """
        #     Create the invoice associated to the SO.
        #     :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
        #                     (partner_invoice_id, currency)
        #     :param final: if True, refunds will be generated if necessary
        #     :returns: list of created invoices
        #     """
        #     copy1=self.create_inv_copy(grouped=False, final=False, date=None,iscash=True)

        #     copy2=self.create_inv_copy(grouped=False, final=False, date=None,iscash=False)

            
            
            
    def create_inv_copy(self, grouped=False, final=False, date=None,iscash=True): 
            if not self.env['account.move'].check_access_rights('create', False):
                try:
                    self.check_access_rights('write')
                    self.check_access_rule('write')
                except AccessError:
                    return self.env['account.move']

            # 1) Create invoices.
            invoice_vals_list = []
            invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
            for order in self:
                order = order.with_company(order.company_id)
                current_section_vals = None
                down_payments = order.env['sale.order.line']
                 
                invoice_vals = order._prepare_invoice()
                invoiceable_lines = order._get_invoiceable_lines(final,iscash)

                if not any(not line.display_type for line in invoiceable_lines):
                    continue

                invoice_line_vals = []
                down_payment_section_added = False
                for line in invoiceable_lines:
                    if not down_payment_section_added and line.is_downpayment:
                        # Create a dedicated section for the down payments
                        # (put at the end of the invoiceable_lines)
                        invoice_line_vals.append(
                            (0, 0, order._prepare_down_payment_section_line(
                                sequence=invoice_item_sequence,
                            )),
                        )
                        down_payment_section_added = True
                        invoice_item_sequence += 1
                    invoice_line_vals.append(
                        (0, 0, line._prepare_invoice_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    invoice_item_sequence += 1

                invoice_vals['invoice_line_ids'] += invoice_line_vals
                invoice_vals_list.append(invoice_vals)

            if not invoice_vals_list:
                raise self._nothing_to_invoice_error()

            # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
            if not grouped:
                new_invoice_vals_list = []
                invoice_grouping_keys = self._get_invoice_grouping_keys()
                invoice_vals_list = sorted(
                    invoice_vals_list,
                    key=lambda x: [
                        x.get(grouping_key) for grouping_key in invoice_grouping_keys
                    ]
                )
                for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                    origins = set()
                    payment_refs = set()
                    refs = set()
                    ref_invoice_vals = None
                    for invoice_vals in invoices:
                        if not ref_invoice_vals:
                            ref_invoice_vals = invoice_vals
                        else:
                            ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                        origins.add(invoice_vals['invoice_origin'])
                        payment_refs.add(invoice_vals['payment_reference'])
                        refs.add(invoice_vals['ref'])
                    ref_invoice_vals.update({
                        'ref': ', '.join(refs)[:2000],
                        'invoice_origin': ', '.join(origins),
                        'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                    })
                    new_invoice_vals_list.append(ref_invoice_vals)
                invoice_vals_list = new_invoice_vals_list

            # 3) Create invoices.

            # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
            # in a single invoice. Example:
            # SO 1:
            # - Section A (sequence: 10)
            # - Product A (sequence: 11)
            # SO 2:
            # - Section B (sequence: 10)
            # - Product B (sequence: 11)
            #
            # If SO 1 & 2 are grouped in the same invoice, the result will be:
            # - Section A (sequence: 10)
            # - Section B (sequence: 10)
            # - Product A (sequence: 11)
            # - Product B (sequence: 11)
            #
            # Resequencing should be safe, however we resequence only if there are less invoices than
            # orders, meaning a grouping might have been done. This could also mean that only a part
            # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
            if len(invoice_vals_list) < len(self):
                SaleOrderLine = self.env['sale.order.line']
                for invoice in invoice_vals_list:
                    sequence = 1
                    for line in invoice['invoice_line_ids']:
                        line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                        sequence += 1

            # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
            # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
            moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

            # 4) Some moves might actually be refunds: convert them if the total amount is negative
            # We do this after the moves have been created since we need taxes, etc. to know if the total
            # is actually negative or not
            if final:
                moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
            for move in moves:
                move.message_post_with_view('mail.message_origin_link',
                    values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                    subtype_id=self.env.ref('mail.mt_note').id
                )
            return moves


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0)

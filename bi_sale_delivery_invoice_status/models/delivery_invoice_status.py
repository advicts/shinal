# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class inherit_sale(models.Model):
	_inherit = "sale.order"


	is_partially_delivery = fields.Boolean(string="Partially Delivered",readonly=1,copy=False)
	is_fully_delivery = fields.Boolean(string="Fully Delivered",readonly=1,copy=False)
	is_partially_paid = fields.Boolean(string="Partially Paid",readonly=1,copy=False)
	is_fully_paid = fields.Boolean(string="Fully Paid",readonly=1,copy=False)
	advicts_amount_due = fields.Float(string="amount due")
	advicts_amount_paid = fields.Float(string="paid amount")



class inherit_stock_picking(models.Model):
	_inherit = "stock.picking"


	is_pick = fields.Boolean(string="Is Picking",compute="_compute_sale_fully_picking",store=True)

	@api.depends("state")
	def _compute_sale_fully_picking(self):
		for picking in self:
			picking.is_pick = False

			# اربط ال picking بال sale order
			order = self.env['sale.order'].search([('name', '=', picking.origin)], limit=1)
			if not order:
				continue

			# حساب الكمية المستلمة
			delivered_qty = 0.0
			for p in order.picking_ids:
				if p.state == 'done':
					for move in p.move_ids_without_package:
						for line in move.move_line_ids:
							delivered_qty += line.qty_done

			# الكمية المطلوبة
			total_qty = sum(order.order_line.mapped('product_uom_qty'))

			# منطق المقارنة
			if delivered_qty > 0 and delivered_qty < total_qty:
				order.is_partially_delivery = True
				order.is_fully_delivery = False

			if delivered_qty == total_qty and total_qty > 0:
				order.is_fully_delivery = True
				order.is_partially_delivery = False

			picking.is_pick = True


class inherit_invoicing(models.Model):
    _inherit = "account.move"

    iss_invoice = fields.Boolean(
        string="Is Invoice",
        compute="_compute_sale_invoice"
    )

    @api.depends("payment_state", "amount_residual", "state", "line_ids.amount_residual")
    def _compute_sale_invoice(self):
        for invoice in self:

            # Debug
            print("\n=========== DEBUG ===========")
            print("INVOICE:", invoice.name)
            print("TYPE:", invoice.move_type)
            print("STATE:", invoice.state)
            print("PAYMENT STATE:", invoice.payment_state)
            print("AMOUNT RESIDUAL:", invoice.amount_residual)
            print("LINE RESIDUAL SUM:", sum(invoice.line_ids.mapped('amount_residual')))
            print("INVOICE ORIGIN:", invoice.invoice_origin)
            print("================================\n")

            order = self.env['sale.order'].search([
                ('name', '=', invoice.invoice_origin)
            ], limit=1)

            invoice.iss_invoice = True

            if not order:
                continue

            if invoice.state != 'posted':
                continue

            # أهم تعديل هنا ↓↓
            if invoice.payment_state in ("in_payment", "partial", "paid"):

                order.is_partially_paid = True
                order.is_fully_paid = False

                total_due = sum(order.invoice_ids.mapped('amount_residual'))
                total = order.amount_total
                paid = total - total_due

                order.advicts_amount_due = total_due
                order.advicts_amount_paid = paid

                # دفعت بالكامل
                if abs(total_due) < 0.0001:
                    order.is_partially_paid = False
                    order.is_fully_paid = True

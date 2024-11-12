# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ProductAvgPrice(models.Model):
    _name = "account.move.line.avg.price"

    product_id = fields.Many2one(
        'product.product', 'Product', index=True, required=True)
    move_line_id = fields.Many2one(comodel_name="account.move.line")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    sale_price = fields.Monetary(currency_field='currency_id', string="AVG Price")


class Invoice(models.Model):
    _inherit = "account.move"

    product_move_line_ids = fields.Many2many(comodel_name="account.move.line", compute='_compute_product_avg_price')
    product_avg_price_ids = fields.Many2many(comodel_name="account.move.line.avg.price",
                                             compute='_compute_product_avg_price')
    picking_created_from = fields.Many2one(comodel_name="stock.picking")

    @api.depends('invoice_line_ids')
    def _compute_product_avg_price(self):
        for record in self:
            product_move_lines = []
            product_avg_lines = []
            for line in record.invoice_line_ids.filtered(lambda l: l.product_id):
                sale_price = 0.0
                product_move_line_ids = self.env['account.move.line'].sudo().search(
                    [('move_id.partner_id', '=', record.partner_id.id),
                     ('move_id.move_type', '=', 'out_invoice'),
                     ('product_id', '=', line.product_id.id),
                     ('parent_state', '=', 'posted'),
                     ('exclude_from_invoice_tab', '=',
                      False),

                     ])

                if product_move_line_ids:
                    product_move_lines = product_move_line_ids.ids
                    if line.company_id.customer_return_price_type == 'avg':
                        sale_price = abs(sum(product_move_line_ids.mapped("balance"))) / sum(
                            product_move_line_ids.mapped("quantity"))
                    else:
                        if 'sub_total_before_discount' in self.env['account.move.line']._fields:
                            sale_price = abs(
                                product_move_line_ids[0].sub_total_before_discount / product_move_line_ids[0].quantity)
                        else:
                            sale_price = abs(product_move_line_ids[0].balance / product_move_line_ids[0].quantity)

                product_avg_lines.append((0, 0, {'product_id': line.product_id.id,
                                                 'sale_price': sale_price}))

            record.product_avg_price_ids = product_avg_lines or False
            record.product_move_line_ids = [(6, 0, product_move_lines)]

    def action_view_invoice_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice Lines'),
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'view_id': self.env.ref('ejaf_customer_returns.customer_invoice_line_tree').id,
            'domain': [('id', 'in', self.product_move_line_ids.ids)],
            'context': dict(self._context,
                            create=False, edit=False)
        }

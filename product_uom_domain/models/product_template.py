# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    uom_sell_ids = fields.Many2many(comodel_name="uom.uom",
                                    string="Sell Unit Of Measures")
    uom_id_categ = fields.Many2one(
        comodel_name="uom.category", related="uom_id.category_id", store=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if not res:
            res = {}
        if self.product_id:
            if self.product_id.uom_sell_ids:
                res.update(
                    {'domain': {'product_uom': [('id', 'in', self.product_id.uom_sell_ids.ids)]}})
            else:
                res.update(
                    {'domain': {'product_uom': [('category_id', '=', self.product_id.uom_id_categ.id)]}})

        else:
            res.update({'domain': {'product_uom': [('id', 'in', [])]}})
        return res

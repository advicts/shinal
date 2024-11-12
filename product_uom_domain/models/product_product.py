# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    uom_sell_ids = fields.Many2many(comodel_name="uom.uom",
                                    string="Sell Unit Of Measures", related="product_tmpl_id.uom_sell_ids")

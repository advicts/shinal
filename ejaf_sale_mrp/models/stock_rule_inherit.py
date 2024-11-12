# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id,
                                       values, bom)
        res["sale_order_partner_id"] = (
            values.get("group_id").partner_id.id if values.get("group_id", False) else False
        )
        return res

# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_partner_id = fields.Many2one('res.partner', string='Customer')

    qty_of_scrap = fields.Float(string="QTY Scraped",compute='compute_scrap_ids_no', store=True)

    @api.depends('scrap_ids')
    def compute_scrap_ids_no(self):
        for scrap in self:
            if scrap.scrap_ids:
                for line in scrap.scrap_ids:
                    scrap.qty_of_scrap += line.scrap_qty
            else:
                scrap.qty_of_scrap = 0

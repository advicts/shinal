# -*- coding: utf-8 -*-
from odoo import fields, models, api


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = "stock.move.line"

    date = fields.Datetime(index=True)
    location_id = fields.Many2one(index=True)
    location_dest_id = fields.Many2one(index=True)
    state = fields.Selection(index=True)

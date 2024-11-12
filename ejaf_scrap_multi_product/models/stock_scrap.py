from odoo import models,fields


class StockScrap(models.Model):
    _inherit = 'stock.scrap'


    scrap_multi_product_id = fields.Many2one("scrap.multi.product")
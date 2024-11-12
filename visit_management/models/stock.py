from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    visit_id = fields.Many2one('visits.visit', string='Visit')

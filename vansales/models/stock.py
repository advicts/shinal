from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vansales_ref = fields.Char(string="Vansales Reference",copy=False)
    _sql_constraints = [('vansales_ref_uniq', 'unique (vansales_ref)',
                         "The Tablet Order ID should be unique")]
    partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    is_vansales = fields.Boolean('Is Vansales', default=False)
    vansales_version = fields.Char(string="Vansales App Version")

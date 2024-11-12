from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    zom_ref = fields.Char(string="Zom App Reference")
    _sql_constraints = [('zom_ref_uniq', 'unique (zom_ref)',
                         "The Tablet Order ID should be unique")]
    partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    is_zom_app = fields.Boolean('Is From APP', default=False)
    collection_center_id = fields.Many2one('collection.center',string='Collection Center',domain=[('active','=',True)])

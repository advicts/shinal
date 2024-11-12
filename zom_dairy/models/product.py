from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fixed_cost = fields.Float(string="Fixed Cost IQD",default=0,required=True)

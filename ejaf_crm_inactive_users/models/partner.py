from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_id = fields.Many2one('res.users', context={'active_test': False})

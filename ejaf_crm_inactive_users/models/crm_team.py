from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    user_id = fields.Many2one('res.users', context={'active_test': False})
    member_ids = fields.Many2many(context={'active_test': False})

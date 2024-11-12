from odoo import models, fields, api


class Payment(models.Model):
    _inherit = 'account.payment'

    visit_id = fields.Many2one('visits.visit', string='Visit')

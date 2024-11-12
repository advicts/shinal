from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_category_id = fields.Many2one('partner.category', compute='_compute_partner_category_id',
                                          string="Partner Category", store=True)

    @api.depends('partner_id')
    def _compute_partner_category_id(self):
        for rec in self:
            rec.partner_category_id = rec.partner_id.partner_category_id if rec.partner_id else False

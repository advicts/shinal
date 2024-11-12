from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_category_id = fields.Many2one('partner.category', compute='_compute_partner_category_id',
                                          string="Partner Category", store=True)

    @api.depends('partner_id')
    def _compute_partner_category_id(self):
        for rec in self:
            rec.partner_category_id = rec.partner_id.partner_category_id if rec.partner_id else False


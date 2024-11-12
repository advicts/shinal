from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    partner_category_id = fields.Many2one('partner.category',
                                          string="Partner Category", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['partner_category_id'] = ", s.partner_category_id as partner_category_id"
        groupby += ', s.partner_category_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby,
                                              from_clause)






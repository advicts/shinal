# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ProductMovesReportWizard(models.TransientModel):
    _name = "product.moves.report.wizard"

    def _get_default_date_from(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y-%m')
        return '{}-01'.format(year)

    def _get_default_date_to(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    date_from = fields.Date(string='Start Date', required=True, default=_get_default_date_from)
    date_to = fields.Date(string='End Date', required=True, default=_get_default_date_to)
    product_filter = fields.Selection(string="", selection=[('product', 'On One Product'),
                                                            ('all_product', 'On ALL Products'),
                                                            ('product_category', 'On Product Category'),
                                                            ], required=True, default='all_product')
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    product_categ_id = fields.Many2one(comodel_name="product.category", string="Product Category")
    location_id = fields.Many2one(comodel_name="stock.location", string="Location")
    is_all_internal_location = fields.Boolean(string="ALL Internal Locations")
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Customer Filter", )
    salesperson_ids = fields.Many2many(comodel_name="res.users", string="Salesperson Filter", context={'active_test': False} )

    @api.onchange('product_filter')
    def onchange_method(self):
        if self.product_filter == 'all_product':
            self.product_id = False
            self.product_categ_id = False

        elif self.product_filter == 'product_category':
            self.product_id = False
        else:
            self.product_categ_id = False

    def print_xlsx_report(self):
        """
         To get the date and print the report
         @return: return report
        """
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        if data['form']['product_id']:
            report = self.env['ir.actions.report']._get_report_from_name('product_moves_report.single_product_moves_report_xlsx')
        else:
            report = self.env['ir.actions.report']._get_report_from_name('product_moves_report.all_product_moves_report_xlsx')

        return {
            'data': data,
            'type': 'ir.actions.report',
            'report_name': report.report_name,
            'report_type': report.report_type,
            'report_file': report.report_file,
        }
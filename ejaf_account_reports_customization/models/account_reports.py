# -*- coding: utf-8 -*-

from odoo import models, api


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_milk_supplier = None

    @api.model
    def _get_options(self, previous_options=None):
        # OVERRIDE
        options = super(AccountReport, self)._get_options(previous_options)

        if not self.filter_milk_supplier:
            return options

        milk_supplier_options = ['Milk Supplier', 'Non Milk Supplier', 'All']

        # Add milk supplier options
        options['milk_supplier'] = True
        options['milk_supplier_ops'] = [{'id': o, 'name': o, 'selected': False} for o in milk_supplier_options]

        # Merge old options with default from this report
        if not previous_options:
            previous_options = {}

        for key, value in options.items():
            if key in ['milk_supplier_ops'] and key in previous_options and value is not None and previous_options[
                key] is not None:
                for index, item in enumerate(options[key]):
                    for previous_item in previous_options[key]:
                        if previous_item['id'] == item['id']:
                            options[key][index]['selected'] = previous_item['selected']
        return options

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('milk_supplier_ops'):
            ctx['milk_supplier_ops'] = options.get('milk_supplier_ops', [])
        return ctx

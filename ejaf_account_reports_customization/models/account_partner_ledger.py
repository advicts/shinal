# -*- coding: utf-8 -*-

from odoo import models, api


class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger'

    filter_milk_supplier = True

    @api.model
    def _get_options_domain(self, options):
        # OVERRIDE
        domain = super(AccountPartnerLedger, self)._get_options_domain(options)
        if options.get('milk_supplier_ops', False):
            d = []
            for o in options.get('milk_supplier_ops'):
                if o['name'] == 'All' and o['selected']:
                    d = ['|', ('partner_id.is_milk_supplier', '=', False),
                         ('partner_id.is_milk_supplier', '=', True)]
                    break

            if not d:
                for o in options.get('milk_supplier_ops'):
                    if o['name'] == 'Milk Supplier' and o['selected']:
                        if d:
                            d = ['|', ('partner_id.is_milk_supplier', '=', True)] + d
                        else:
                            d += [('partner_id.is_milk_supplier', '=', True)]
                    if o['name'] == 'Non Milk Supplier' and o['selected']:
                        if d:
                            d = ['|', ('partner_id.is_milk_supplier', '=', False)] + d
                        else:
                            d += [('partner_id.is_milk_supplier', '=', False)]
            domain += d
        return domain

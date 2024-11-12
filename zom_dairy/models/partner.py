import logging
from odoo import models, fields, api
from .couchdb import CouchDB
from functools import reduce


class Partner(models.Model):
    _inherit = 'res.partner'

    collection_center_id = fields.Many2one('collection.center', string='Collection Center', )
    partner_zone_id = fields.Many2one('partner.zone', string='Zone')
    partner_ref = fields.Char(string="Ref", readonly=True)
    is_milk_supplier = fields.Boolean(string="Milk Supplier")

    @api.model
    def create(self, vals_list):
        record = super(Partner, self).create(vals_list)
        if record.collection_center_id.code and record.partner_zone_id.code:
            record.write({
                'partner_ref': str(record.collection_center_id.code) + "/" + str(record.partner_zone_id.code) + "/" +
                               self.env['ir.sequence'].get(
                                   'partner.zone.seq')
            })
        elif record.collection_center_id.code and not record.record.partner_zone_id.code:
            record.write({
                'partner_ref': str(record.collection_center_id.code) + "/" +
                               self.env['ir.sequence'].get(
                                   'partner.zone.seq')
            })

        if record.partner_zone_id.code and not record.collection_center_id.code:
            record.write({
                'partner_ref': str(record.partner_zone_id.code) + "/" +
                               self.env['ir.sequence'].get(
                                   'partner.zone.seq')
            })
        try:
            self._zom_update_partner(CouchDB().partner_master(), record.id)
        except:
            return record
        return record

    def write(self, vals_list):
        for rec in self:
            record = super(Partner, self).write(vals_list)
            self._zom_update_partner(CouchDB().partner_master(), rec.id)
            return record

    def _zom_update_partner(self, db, partner_id):
        customer = self.env['res.partner'].browse(partner_id)
        doc_id = 'partner' + str(partner_id)
        doc = db.get(doc_id)
        invoices = self._get_invoices(customer)
        document = {
            '_id': doc_id,
            'user_id': customer.user_id.id,
            'type': 'partner',
            'id': customer.id,
            'is_milk_supplier': customer.is_milk_supplier,
            'name': customer.name,
            'city': customer.city,
            'display_name': customer.display_name,
            'email': customer.email,
            'lang': customer.lang,
            'mobile': customer.mobile,
            'parent_name': customer.parent_name,
            'partner_latitude': customer.partner_latitude,
            'partner_longitude': customer.partner_longitude,
            'category_id': customer.category_id.mapped('id'),
            'phone': str(customer.phone),
            'street': str(customer.street),
            'debit':reduce(lambda total,invoice: total + invoice['amount'], invoices,0),
            'credit':0,
            'total_invoiced': reduce(lambda total,invoice: total + invoice['amount'], invoices,0),
            'collection_center_id': customer.collection_center_id.id,
            'collection_center': customer.collection_center_id.name,
            'invoices': invoices
        }
        if doc:
            document['_rev'] = doc['_rev']
        doc_id, doc_rev = db.save(document)

    def _get_invoices(self, partner_id):
        supplier_invoices = self.env['account.move'].search(
            [('partner_id', '=', partner_id.id), ('payment_state', 'in', ['not_paid'])])
        # for line in supplier_invoices:
        #     line._auto_assign_outstanding_line()
        supplier_invoice_groups = self.env['account.move'].read_group(
            domain=[('partner_id', '=', partner_id.id),
                    ('move_type', 'in', ('in_invoice', 'in_refund')), ('payment_state', 'in', ['not_paid'])],
            fields=['invoice_date', 'amount_total_in_currency_signed'], groupby=['invoice_date']
        )
        inovices = []
        for group in supplier_invoice_groups:
            inovices.append({
                'date': group['invoice_date'],
                'amount': group['amount_total_in_currency_signed']
            })
        return inovices 

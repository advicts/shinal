import logging
from odoo import models, fields, api
from .couchdb import CouchDB
from datetime import datetime


import logging

_logger = logging.getLogger(__name__)


class ModifyVanSalesStockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _update_reserved_quantity(self,
                                  product_id,
                                  location_id,
                                  quantity,
                                  lot_id=None,
                                  package_id=None,
                                  owner_id=None,
                                  strict=False):
        record = super(ModifyVanSalesStockQuant,
                       self)._update_reserved_quantity(product_id, location_id,
                                                       quantity, lot_id,
                                                       package_id, owner_id,
                                                       strict)
        self.update_quant_product(CouchDB().product_master(),
                                  location_id.id,
                                  product_id.id)

        return record

    @api.model
    def _update_available_quantity(self,
                                   product_id,
                                   location_id,
                                   quantity,
                                   lot_id=None,
                                   package_id=None,
                                   owner_id=None,
                                   in_date=None):
        record = super(ModifyVanSalesStockQuant,
                       self)._update_available_quantity(
                           product_id, location_id, quantity, lot_id,
                           package_id, owner_id)
        self.update_quant_product(CouchDB().product_master(),
                                  location_id.id,
                                  product_id.id)

        return record

    def update_quant_product(self, db, location_id, product_id):
        # Search For All Locations ##
        search_stock_quants = self.env['stock.quant'].search(
            [('location_id', '=', location_id), ('product_id', '=', product_id)])
        doc_id = 'quant-' + str(product_id) + "-" + str(location_id)
        doc = db.get(doc_id)
        lots = {}
        for quant in search_stock_quants:
            doc_key = str(product_id)+"-"+str(location_id) + \
                "-"+str(quant.lot_id.id)
            if lots.get(doc_key):
                lots[doc_key]['quantity'] = lots[doc_key]['quantity']+quant.quantity
                lots[doc_key]['reserved_quantity'] = lots[doc_key]['reserved_quantity'] + \
                    quant.reserved_quantity
            else:
                lots[doc_key] = {
                    'lot_id': quant.lot_id.id,
                    'lot': quant.lot_id.name,
                    'lot_expiration_date': str(quant.lot_id.expiration_date),
                    'lot_removal_date': str(quant.lot_id.removal_date),
                    'quantity': quant.quantity,
                    'reserved_quantity': quant.reserved_quantity
                }
        quants_lst = list(lots.values())
        document = {
            '_id': doc_id,
            'type': 'quant',
            'product_id': product_id,
            'location_id': location_id,
            'update_date':datetime.timestamp(datetime.now())*1000,
            'quant': {
                'qty': sum(q['quantity'] for q in quants_lst),
                'reserved_quantity': sum(q['reserved_quantity'] for q in quants_lst),
                'lots': quants_lst
            }
        }
        if doc:
            document['_rev'] = doc['_rev']
        doc_id, doc_rev = db.save(document)

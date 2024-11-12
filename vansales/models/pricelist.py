from odoo import models, fields, api
from .couchdb import CouchDB
import json

class Pricelist(models.Model):
    _inherit = 'product.pricelist'


    def write(self, values):
        for rec in self:
            record = super(Pricelist, self).write(values)
            self.update_pricelist(CouchDB().product_master(),self.id)
            return record


    def update_pricelist(self, db,pricelist_id):
        pricelist = self.env['product.pricelist'].browse(pricelist_id)
        doc_id = 'pricelist' + str(pricelist_id)
        doc = db.get(doc_id)
        document={
            '_id':doc_id,
            'type':'pricelist',
            'id':pricelist.id,
            'display_name':pricelist.display_name,
            'name':pricelist.name,
            'currency_id':pricelist.currency_id.id,
            'currency_symbol':pricelist.currency_id.symbol,
            'currency':pricelist.currency_id.display_name,
            'discount_policy':pricelist.discount_policy,
            'item_ids':self.get_item_ids(pricelist.item_ids)           
        }
        if doc:
            document['_rev'] = doc['_rev']
        doc_id, doc_rev = db.save(document)


    def get_item_ids(self,item_ids):
        doc=[]
        for item in item_ids:
            doc.append({
                'id':item.id,
                'name':item.name,
                'applied_on':item.applied_on,
                'base':item.base,
                'categ_id':item.categ_id.id,
                'company_id':item.company_id.id,
                'compute_price':item.compute_price,
                'currency_id':item.currency_id.id,
                'currency_symbol':item.currency_id.symbol,
                'currency':item.currency_id.display_name,
                'date_end':str(item.date_end),
                'date_start':str(item.date_start),
                'fixed_price':item.fixed_price,
                'min_quantity':item.min_quantity,
                'percent_price':item.percent_price,
                'price':item.price,
                'price_discount':item.price_discount,
                'price_max_margin':item.price_max_margin,
                'price_min_margin':item.price_min_margin,
                'price_round':item.price_round,
                'price_surcharge':item.price_surcharge,
                'product_id':item.product_id.id,
                'product_tmpl_id':item.product_tmpl_id.id
            })

        return doc

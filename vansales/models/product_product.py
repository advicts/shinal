from odoo import models, fields, api
from .couchdb import CouchDB
import json


class Product(models.Model):
    _inherit = 'product.product'


    @api.model
    def create(self, vals):
      res = super().create(vals)
      if not self.env.context.get('import_file'):
        self.update_product(CouchDB().product_master(), res.id)
      return res

    def update_product_action(self):
        for rec in self:
            self.update_product(CouchDB().product_master(), rec.id)

    def unlink(self):
        for rec in self:
            res= super(Product, self).unlink()
            if res:
                self.unlink_product(CouchDB().product_master(),rec.id)
            return res


    def unlink_product(self, db, product_id):
        doc_id = 'product' + str(product_id)
        doc = db.get(doc_id)
        doc['_deleted'] = True
        doc_id, doc_rev = db.save(doc)

    def write(self, values):
        record = super(Product, self).write(values)
        if self.type == 'product':
            self.update_product(CouchDB().product_master(), self.id)

        return record
    def _get_product_lots(self,product_id):
        lots =self.env['stock.production.lot'].sudo().search([('product_id','=',product_id)])
        lot_lst=[]
        for lot in lots:
            lot_lst.append({
              'lot_id': lot.id,
              'lot': lot.name,
              'lot_expiration_date': str(lot.expiration_date),
              'lot_removal_date': str(lot.removal_date),
              'quantity': 0,
              'reserved_quantity': 0
          })
        return lot_lst
    def update_product(self, db, product_id):
        product = self.env['product.product'].browse(product_id)
        doc_id = 'product' + str(product.id)
        doc = db.get(doc_id)
        document = {
            '_id': doc_id,
            'type': 'product',
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'code': product.default_code,
            'active':product.active,
            'tracking':product.tracking,
            'display_name': {
                'en': product.with_context({
                    'lang': 'en_US'
                }).display_name,
                'ar': product.with_context({
                    'lang': 'ar_SY'
                }).display_name,
                'kr': product.display_name
            },
            'categ_id': product.categ_id.id,
            'categ': {
                'en': product.with_context({
                    'lang': 'en_US'
                }).categ_id.name,
                'ar': product.with_context({
                    'lang': 'ar_SY'
                }).categ_id.name,
                'kr': product.categ_id.name
            },
            'image_small': '',
            'uom_id': product.uom_id.id,
            'uom_categ_id': product.uom_id.category_id.id,
            'uom': {
                'en': product.with_context({
                    'lang': 'en_US'
                }).uom_id.name,
                'ar': product.with_context({
                    'lang': 'ar_SY'
                }).uom_id.name,
                'kr': product.uom_id.name
            },
            'default_uom': {
                'id': product.uom_id.id,
                'name': {
                    'en': product.uom_id.with_context({
                        'lang': 'en_US'
                    }).name,
                    'ar': product.uom_id.with_context({
                        'lang': 'ar_SY'
                    }).name,
                    'kr': product.uom_id.name
                },
                'rounding': product.uom_id.rounding,
                'factor': product.uom_id.factor,
                'factor_inv': product.uom_id.factor_inv,
                'uom_type': product.uom_id.uom_type,
                'category_id': product.uom_id.category_id.id,
                'active': product.uom_id.active
            },
            'list_price': product.lst_price,
            'name': {
                'en': product.with_context({
                    'lang': 'en_US'
                }).name,
                'ar': product.with_context({
                    'lang': 'ar_SY'
                }).name,
                'kr': product.name
            },
            'price': product.price,
            'barcode': product.barcode,
            'qty_available': product.qty_available,
            'display_price': product.lst_price,
            'uom_sell_ids': product.uom_sell_ids.mapped('id'),
            'lots':self._get_product_lots(product_id=product.id)
            # 'has_packages':True if product.packaging_ids else False,
            # 'packaging_ids':self.init_product_packages(product.packaging_ids)
        }

        if doc:
            document['_rev'] = doc['_rev']
        doc_id, doc_rev = db.save(document)

    def init_product_packages(self, packages):
        packageslst = []
        for package in packages:
            if package.active:
                doc = {
                    'id': package.id,
                    'barcode': package.barcode,
                    'display_name': package.display_name,
                    'name': package.name,
                    'package_price': package.package_price,
                    'product_id': package.product_id.id,
                    'product': package.product_id.name,
                    'uom_id': package.product_uom.id,
                    'uom': package.product_uom.name,
                    'qty': package.qty,
                }
                packageslst.append(doc)
        return packageslst

from openerp import models, fields, api, _
from datetime import date


class Product(models.Model):
    _inherit = 'product.template'

    first_level_minimum_qty = fields.Integer(string='First Level Min QTY')
    second_level_minimum_qty = fields.Integer(string='Second Level Min QTY')

    @api.model
    def send_product_minimum_qty_second_level_notify(self):
        discussion_subtype = self.env.ref('mail.mt_comment')
        products = self.env['product.template'].search([])
        access_group = self.env.ref(
            'ejaf_stock_qty_low_notify.second_level_minimum_qty_group')
        users = access_group.users
        partner_ids = [u.partner_id.id for u in users]
        for product in products:
            if product.second_level_minimum_qty and product.virtual_available and product.qty_available and (
                    product.virtual_available < product.second_level_minimum_qty or product.qty_available < product.second_level_minimum_qty):
                product.message_post(
                    partner_ids=partner_ids,
                    subject=_('Product Stock QTY Less Than  Second Level'),
                    body=_('Product %s  Stock QTY Less Than Minimum Second Level..') % (product.name),
                    subtype_id=discussion_subtype.id,
                )

    @api.model
    def send_product_minimum_qty_first_level_notify(self):
        discussion_subtype = self.env.ref('mail.mt_comment')
        products = self.env['product.template'].search([])
        access_group = self.env.ref(
            'ejaf_stock_qty_low_notify.first_level_minimum_qty_group')
        users = access_group.users
        partner_ids = [u.partner_id.id for u in users]
        for product in products:

            if product.virtual_available and product.first_level_minimum_qty and product.qty_available and (
                    product.virtual_available < product.first_level_minimum_qty or product.qty_available < product.first_level_minimum_qty):
                product.message_post(
                    partner_ids=partner_ids,
                    subject=_('Product Stock QTY Less Than  First Level'),
                    body=_('Product %s  Stock QTY Less Than Minimum First Level..') % (product.name),
                    subtype_id=discussion_subtype.id,
                )

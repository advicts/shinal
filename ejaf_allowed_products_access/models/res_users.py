# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    restriction_by = fields.Selection([('by_product', 'Products'), ('by_product_category', 'Product Categories')],
                                      default='by_product', string='Restriction By')
    allowed_product_ids = fields.Many2many('product.template', 'product_user_rel', 'product_id', 'user_id',
                                           string='Allowed Products')
    allowed_product_category_ids = fields.Many2many('product.category', 'category_user_rel', 'category_id', 'user_id',
                                                    string='Allowed Product Categories')

    @api.onchange('restriction_by','allowed_product_category_ids')
    def set_products(self):
        for record in self:
            record.allowed_product_ids = False
            if record.restriction_by and record.restriction_by == 'by_product_category' and record.allowed_product_category_ids:
                products = self.env['product.template'].sudo().search(
                    ['|', ('categ_id', 'in', record.allowed_product_category_ids.ids),
                     ('categ_id.parent_id', 'in', record.allowed_product_category_ids.ids)])
                record.allowed_product_ids = products.ids

from odoo import models,fields,api




class ScrapMultiProductsLine(models.Model):
    _name = "scrap.multi.product.line"


    scrap_multi_product_id = fields.Many2one("scrap.multi.product")
    location_id = fields.Many2one("stock.location",related="scrap_multi_product_id.location_id", string="Source Location")
    scrap_location_id = fields.Many2one("stock.location", related="scrap_multi_product_id.scrap_location_id",string="Scrap Location")
    product_id = fields.Many2one("product.product",string="Product",required=True)
    scrap_qty = fields.Float("Quantity",required=True)
    product_uom_id = fields.Many2one("uom.uom",required=True)
    product_uom_category_id = fields.Many2one("uom.category",related="product_id.uom_id.category_id")
    tracking = fields.Selection(related="product_id.tracking")
    lot_id = fields.Many2one("stock.production.lot",string="Lot/Serial")


    @api.onchange("product_id")
    def onchange_product_id(self):
        for rec in self:
            rec.product_uom_id = rec.product_id.uom_id.id


    

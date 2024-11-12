from odoo import models,fields,api




class ScrapMultiProducts(models.Model):
    _name = "scrap.multi.product"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char("Name")
    location_id = fields.Many2one("stock.location", string="Source Location",required=True, tracking=True)
    scrap_location_id = fields.Many2one("stock.location", string="Scrap Location",required=True, tracking=True)
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('done','Done')],string="State",default="draft", tracking=True)
    line_ids = fields.One2many("scrap.multi.product.line","scrap_multi_product_id",string="Scrap Line")
    stock_scrap_ids = fields.One2many("stock.scrap","scrap_multi_product_id",string="Scrap")
    available_product_ids = fields.Many2many('product.product',compute="_compute_available_product_ids")
    available_quant_ids = fields.Many2many('stock.quant',compute="_compute_available_product_ids")


    @api.onchange("location_id")
    def _compute_available_product_ids(self):
        for rec in self:
            quant_ids =self.env["stock.quant"].search([("location_id","=",rec.location_id.id),('product_id.type','in',('product','consu'))])
            rec.available_quant_ids = quant_ids.ids
            rec.available_product_ids = (quant_ids.mapped("product_id")).ids if quant_ids else False


    def action_confirmed(self):
        for rec in self:
            for scrap in rec.line_ids:
                self.env["stock.scrap"].sudo().create({
                    'name':rec.name,
                    'location_id':rec.location_id.id,
                    'scrap_location_id':rec.scrap_location_id.id,
                    'product_id':scrap.product_id.id,
                    'scrap_qty':scrap.scrap_qty,
                    'product_uom_id':scrap.product_uom_id.id,
                    'lot_id':scrap.lot_id.id if scrap.tracking != 'none' else False,
                    'scrap_multi_product_id':rec.id
                })
            rec.state="confirm"


    def action_view_scrap(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Scrap',
            'res_model': 'stock.scrap',
            'view_mode': 'tree,form',
            'domain': [('scrap_multi_product_id', '=', self.id)]
        }

    def action_validate(self):
        for rec in self:
            for scrap in rec.stock_scrap_ids:
                scrap.sudo().action_validate()
            rec.state='done'

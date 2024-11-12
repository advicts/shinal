from odoo import models, fields, _, api
from odoo.tools.safe_eval import safe_eval
import json


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    collection_center_id = fields.Many2one('collection.center', string='Collection Center',
                                           domain=[('active', '=', True)])
    is_external_purchase_order = fields.Boolean('Is External Purchase Order')
    is_internal_purchase_order = fields.Boolean('Is internal Purchase Order')
    po_ref = fields.Char('PO Ref')
    _sql_constraints = [('po_ref_uniq', 'unique (po_ref)',
                         "The Tablet Order ID should be unique")]
    partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    total_qty = fields.Float(string='Total Qty', compute='_calc_total_qty')

    def find_po_by_ref_using_barcode(self, barcode):
        po = self.search([("po_ref", "=", barcode)], limit=1)
        if not po:
            xmlid = "zom_dairy.purchase_order_find"
            action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
            context = safe_eval(action["context"])
            context.update(
                {
                    "default_state": "warning",
                    "default_status": _(
                        "Purchase Order with Internal Reference " "%s cannot be found"
                    )
                                      % barcode,
                }
            )
            action["context"] = json.dumps(context)
            return action
        xmlid = "zom_dairy.zom_dairy_external_purchase_order_action"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        res = self.env.ref("purchase.purchase_order_form", False)
        action["views"] = [(res and res.id or False, "form")]
        action["res_id"] = po.id
        return action

    @api.depends('order_line')
    def _calc_total_qty(self):
        for record in self:
            record.total_qty = sum(line.product_qty for line in record.order_line)

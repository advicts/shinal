from odoo import models, fields, api
from geopy import distance
from odoo.tools.safe_eval import safe_eval
import json


class SaleOrder(models.Model):
  _inherit = 'sale.order'

  vansales_ref = fields.Char(string="Vansales Reference", copy=False)
  _sql_constraints = [('vansales_ref_uniq', 'unique (vansales_ref)',
                       "The Tablet Order ID should be unique")]
  partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
  partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
  is_vansales = fields.Boolean('Is Vansales', default=False)
  vansales_version = fields.Char(string="Vansales App Version")
  user_id = fields.Many2one('res.users', string='Salesperson', index=True, domain=[])
  distance_geo_location = fields.Float(string='Distance Geo (km)',
                                       digits=(16, 2),
                                       compute="_compute_distance_geo_location")

  @api.depends('partner_latitude', 'partner_longitude')
  def _compute_distance_geo_location(self):
    for rec in self:
      order_location = (rec.partner_latitude, rec.partner_longitude)
      partner_location = (rec.partner_id.partner_latitude, rec.partner_id.partner_longitude)
      rec.distance_geo_location = distance.distance(order_location, partner_location).km

  def find_so_by_ref_using_barcode(self, barcode):
    so = self.search([("vansales_ref", "=", barcode)], limit=1)
    if not so:
      xmlid = "vansales.scan_order_find"
      action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
      context = safe_eval(action["context"])
      context.update(
          {
              "default_state": "warning",
              "default_status": _(
                  "Sale Order with Internal Reference " "%s cannot be found"
              )
                                % barcode,
          }
      )
      action["context"] = json.dumps(context)
      return action
    xmlid = "vansales.vansales_sale_order_action"
    action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
    res = self.env.ref("sale.view_order_form", False)
    action["views"] = [(res and res.id or False, "form")]
    action["res_id"] = so.id
    return action


class SaleOrderLine(models.Model):
  _inherit = 'sale.order.line'

  lot_id = fields.Many2one('stock.production.lot', string='Lot')



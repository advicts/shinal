from odoo import models, fields


class CollectionCenter(models.Model):
  _name = 'collection.center'
  _inherit = ['mail.thread']

  name = fields.Char("Name", required=True)
  code = fields.Char("Code", required=True)
  active = fields.Boolean(string='Active', default=True, track_visibility='onchange')
  receive_milk_operation_type_id = fields.Many2one('stock.picking.type',
                                                   string='Receive Milk Operation Type (Receipt)',
                                                   domain=[('code', '=', 'incoming')],
                                                   required=True)

  receive_milk_driver_operation_type_id = fields.Many2many(
      comodel_name='stock.picking.type',
      string='Receive Milk Operation Type (Driver)(Internal Transfer)',
      domain=[('code', '=', 'internal')],
      required=True)

  product_ids = fields.Many2many(
        string='Products', comodel_name='product.product',required=True)



  po_ids = fields.One2many('purchase.order','collection_center_id',string='Purchase Orders')
  payment_ids = fields.One2many('account.payment','collection_center_id',string='Payments')


  def action_view_purchase_order(self):
      for rec in self:
          return {
              'name': ('Purchase Orders'),
              'view_type': 'form',
              'view_mode': 'tree,form',
              'res_model': 'purchase.order',
              'type': 'ir.actions.act_window',
              'target': 'current',
              'domain': [('id', 'in', rec.po_ids.ids)],
          }


  def action_view_payments(self):
      for rec in self:
          return {
              'name': ('Payments'),
              'view_type': 'form',
              'view_mode': 'tree,form',
              'res_model': 'account.payment',
              'type': 'ir.actions.act_window',
              'target': 'current',
              'domain': [('id', 'in', rec.payment_ids.ids)],
          }

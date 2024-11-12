from odoo import http
from odoo.http import request
import logging
import base64

from odoo.tests import Form, tagged


class Return(http.Controller):

  @http.route('/vansales/action/return',
              methods=['POST'],
              type="json",
              auth="public",
              website=True,
              csrf=False)
  def action_return(self, **kw):
    request_body = request.jsonrequest
    if not request.httprequest.headers.get('authorization'):
      #  TODO Remove Static Authorization Token and add it INTO .env OR Remove Token And Check by Request IP..
      return {
          "status": 403,
          "message": "Authentication Errors : Set Authorization Code in Header",
          "data": False
      }
    if request.httprequest.headers[
        'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
      return {"status": 403, "message": "Authentication Errors : not authenticate", "data": False}
    logging.info(request_body)
    result = self.return_creator_action(request_body)
    return result

  def return_creator_action(self, request_body):
    user_setting = request.env['res.users.vansales'].sudo().search(
        [('user_id', '=', request_body['doc']['user_id'])], limit=1)
    logging.info(user_setting)
    order = request.env['stock.picking'].sudo().create({
        'picking_type_id':
            user_setting.return_stock_picking_type.id,
        'location_id':
            user_setting.return_stock_picking_type.default_location_src_id.id,
        'location_dest_id':
            user_setting.return_stock_picking_type.default_location_dest_id.id,
        'partner_id':
            request_body['doc']['partner']['id'],
        'currency_id':
            user_setting.default_currency_id.id,
        'vansales_ref':
            request_body['doc']['order_ref'],
        'is_vansales':
            True,
        'partner_latitude':
            request_body['other_info']['location']['latitude'],
        'partner_longitude':
            request_body['other_info']['location']['longitude'],
        'user_id':
            user_setting.user_id.id,
        'is_customer_return':
            True,

        # 'move_lines':
        'move_ids_without_package':
            self.initi_move_lines(request_body['doc']['cart'], user_setting),
    })
    try:
        if 'visit' in request_body['doc']['partner']:
            visit = request.env['visits.visit'].sudo().browse(request_body['doc']['partner']['visit']['visit_id'])
            order.visit_id=visit.id
    except:
        pass
    try:
      if 'note' in request_body['doc']:
        post_vars = {'subject': "Note", 'body': request_body['doc']['note']}
        order.message_post(type="comment", **post_vars)
      if 'image_note' in request_body['doc']:
        post_vars = {
            'subject':
                "Van Sales Attachment",
            'attachments': [(order.name + 'image.jpg',
                             base64.b64decode(request_body['doc']['image_note']['base64']))]
        }
        order.message_post(type="comment", **post_vars)
    except:
      pass
    order.sudo().action_assign()
    self.init_move_line_ids_without_package(order, request_body['doc']['cart'])
    self.validate_pickings(order, user_setting)
    self.create_credit_note(order, user_setting)

    return {'order_id': order.id, 'order_name': order.name}

  def initi_move_lines(self, lines, user_setting):
    arg_order_line = []
    for order_line in lines:
      order_line_values = {
          'name': order_line['product'],
          'product_id': order_line['product_id'],
          'location_id': user_setting.return_stock_picking_type.default_location_src_id.id,
          'location_dest_id': user_setting.return_stock_picking_type.default_location_dest_id.id,
          'product_uom': order_line['product_uom']['id'],
          'product_uom_qty': order_line['qty'],
      }
      arg_order_line.append((0, 0, order_line_values))
    return arg_order_line

  def init_move_line_ids_without_package(self, pick, lines):
    for order_line in lines:
      moveline = pick.move_line_ids_without_package.filtered(
          lambda p: p.product_id.id == order_line['product_id'] and p.qty_done == 0 and p.
          product_uom_id.id == order_line['product_uom']['id'])
      moveline.qty_done = order_line['qty']
      if "lot" in order_line:
        if order_line['lot'] and order_line['lot']['lot_id']:
          moveline.lot_id = order_line['lot']['lot_id']
      moveline._onchange_serial_number()

  def validate_pickings(self, pick, user_setting):
    if user_setting.is_return_validated:
      wiz_act = pick.sudo().button_validate()
      if wiz_act and isinstance(wiz_act, dict) and wiz_act.get('res_model'):
        if wiz_act["res_model"] == 'stock.immediate.transfer':
          request.env['stock.immediate.transfer'].sudo().create({
              'pick_ids': [(4, pick.id)]
          }).process()
        if wiz_act["res_model"] == 'expiry.picking.confirmation':
          wz_backorder_confirmation = Form(
              request.env['expiry.picking.confirmation'].sudo().with_context(
                  wiz_act['context'])).save()
          wz_backorder_confirmation.process()
      return {"picking_id": pick.id}

  def create_credit_note(self, pick, user_setting):
    if user_setting.is_return_validated:
      try:
        pick.create_refund_invoice()
        if pick.credit_note_id and user_setting.is_return_confirm_credit_note:
          pick.credit_note_id.company_id = user_setting.user_id.company_id.id
          pick.credit_note_id.action_post()
      except Exception as e:
        return {"error": e}

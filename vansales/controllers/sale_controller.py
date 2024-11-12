from odoo import http
from odoo.http import request
from odoo.tests import Form, tagged
import logging
import base64


class Sale(http.Controller):

  @http.route('/vansales/action/order',
              methods=['POST'],
              type="json",
              auth="public",
              website=True,
              csrf=False)
  def action_order(self, **kw):
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
    result = self.order_creator_action(request_body)
    return result

  def order_creator_action(self, request_body):
    user_setting = request.env['res.users.vansales'].sudo().search(
        [('user_id', '=', request_body['doc']['user_id'])], limit=1)
    partner = request.env['res.partner'].sudo().browse(request_body['doc']['partner']['id'])
    doc = {
        'partner_id': request_body['doc']['partner']['id'],
        'vansales_ref': request_body['doc']['order_ref'],
        'pricelist_id': partner.property_product_pricelist.id,
        'is_vansales': True,
        'partner_latitude': request_body['other_info']['location']['latitude'],
        'partner_longitude': request_body['other_info']['location']['longitude'],
        'warehouse_id': user_setting.warehouse_id.id,
        'user_id': user_setting.user_id.id,
        'team_id': user_setting.user_id.sale_team_id.id,
        'payment_term_id': partner.property_payment_term_id.id,
        'order_line': self.initi_order_line(request_body['doc']['cart'], user_setting),
    }
    if 'visit' in request_body['doc']['partner']:
      doc['visit_id'] = request_body['doc']['partner']['visit']['visit_id']
    order = request.env['sale.order'].sudo().create(doc)
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
    self.check_validate_order(order, user_setting)
    picking_result = self.check_validate_pickings(order, user_setting)
    try:
      self.check_validate_invoices(order, user_setting, request_body['doc']['is_paid'])
    except:
      pass
    return {'order_id': order.id, 'order_name': order.name, "delivery": picking_result}

  def initi_order_line(self, lines, user_setting):
    arg_order_line = []
    for order_line in lines:
      product = request.env['product.product'].sudo().browse(order_line['product_id'])
      order_line_values = {
          'product_id': product.id,
          'product_uom': order_line['product_uom']['id'],
          'product_uom_qty': order_line['qty'],
          'price_unit': order_line['price'],
      }
      if "is_free" in order_line and user_setting.analytic_tag_id:
        if order_line['is_free']:
          order_line_values['analytic_tag_ids'] = [(6, 0, [user_setting.analytic_tag_id.id])]
      try:
        if "discount" in order_line and order_line['discount'] > 0:
          order_line_values['discount'] = order_line['discount']
      except:
        pass
      if "lot" in order_line:
        if order_line['lot'] and order_line['lot']['lot_id']:
          order_line_values['lot_id'] = order_line['lot']['lot_id']

      if "promotion_id" in order_line and order_line["promotion_id"]:
        promotion = request.env['sale.promotion'].sudo().browse(order_line["promotion_id"])
        order_line_values['promotion_id'] = order_line["promotion_id"]
        try:
          if "discount" in order_line and order_line['discount'] > 0:
            order_line_values['analytic_tag_ids'] = [(6, 0, [promotion.analytic_tag_id.id])]
        except:
          pass
      arg_order_line.append((0, 0, order_line_values))
    return arg_order_line

  def check_validate_order(self, order, user_setting):
    if user_setting.is_sale_order:
      order.action_confirm()

  def check_validate_pickings(self, order, user_setting):
    if user_setting.is_delivered and order.picking_ids:
      pick = order.picking_ids
      pick.location_id = user_setting.default_location_src_id.id
      try:
        pick.sudo().action_assign()
        self.init_move_line_ids_without_package(pick=pick)
        wiz_act = pick.sudo().button_validate()
        if wiz_act and wiz_act.get('res_model'):
          if wiz_act["res_model"] == 'stock.immediate.transfer':
            wz_immediate_transfer = Form(
                request.env['stock.immediate.transfer'].sudo().with_context(
                    wiz_act['context'])).save()
            wz_immediate_transfer.process()
          elif wiz_act["res_model"] == 'stock.overprocessed.transfer':
            wz_overprocessed = Form(request.env['stock.overprocessed.transfer'].sudo().with_context(
                wiz_act['context'])).save()
            wz_overprocessed.process()
          elif wiz_act["res_model"] == 'stock.backorder.confirmation':
            wz_backorder_confirmation = Form(
                request.env['stock.backorder.confirmation'].sudo().with_context(
                    wiz_act['context'])).save()
            wz_backorder_confirmation.process()
        return {"picking_id": pick.id}
      except Exception as e:
        return {"error": e}


  def init_move_line_ids_without_package(self, pick):
    for line in pick.move_line_ids_without_package:
      if line.move_id.sale_line_id:
        if line.move_id.sale_line_id.lot_id:
          line.lot_id = line.move_id.sale_line_id.lot_id.id
          line._onchange_serial_number()



  def check_validate_invoices(self, order, user_setting, is_paid):
    if user_setting.is_invoiced or is_paid:
      invoice = order.sudo()._create_invoices()
      if invoice:
        invoice.journal_id = user_setting.sale_journal.id
        invoice.action_post()
        self.check_validate_payments(order, user_setting, invoice, is_paid)

  def check_validate_payments(self, order, user_setting, invoice, is_paid):
    if user_setting.is_paid_order or is_paid:
      res = invoice.action_register_payment()
      wz_payment = Form(request.env[res['res_model']].sudo().with_context(res['context'])).save()
      wz_payment.journal_id = user_setting.cash_journal.id
      wz_payment.action_create_payments()

  @http.route('/api/print/order',
              methods=['POST'],
              type="json",
              auth="public",
              website=True,
              csrf=False)
  def get_order_report(self, **kw):
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
    result = self._get_pdf_report(request_body)
    return result

  def _get_pdf_report(self, body):
    pdf = request.env.ref('sale.action_report_saleorder').sudo(2)._render_qweb_pdf(
        body['order_id'])[0]
    return {'doc': base64.b64encode(pdf)}

from odoo import http
from odoo.http import request
import logging


class Payment(http.Controller):

  @http.route('/vansales/action/payment',
              methods=['POST'],
              type="json",
              auth="public",
              website=True,
              csrf=False)
  def action_payment(self, **kw):
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
    result = self.payment_creator_action(request_body)
    return result

  def payment_creator_action(self, doc):
    user_setting = request.env['res.users.vansales'].sudo().search(
        [('user_id', '=', doc['user_id'])], limit=1)
    obj = {
        'partner_id': doc['doc']['partner']['id'],
        'user_id': user_setting.user_id.id,
        'invoice_user_id': user_setting.user_id.id,
        'company_id': user_setting.user_id.company_id.id,
        'payment_type': 'inbound',
        'partner_type': 'customer',
        'journal_id': user_setting.cash_journal.id,
        'currency_id': doc['doc']['currency_id'],
        'vansales_ref': doc['doc']['payment_ref'],
        'is_vansales': True,
        'partner_latitude': doc['other_info']['location']['latitude'],
        'partner_longitude': doc['other_info']['location']['longitude'],
        'payment_method_id': 2,
        'amount': doc['doc']['amount'],
        'ref': doc['doc']['note'],
    }
    try:
      if 'visit' in doc['doc']['partner']:
          visit = request.env['visits.visit'].sudo().browse(doc['doc']['partner']['visit']['visit_id'])
          obj['visit_id']=visit.id
    except:
        pass
    payment = request.env['account.payment'].sudo().create(obj)

    if user_setting.is_posted_payment:
        payment.action_post()

    return {'payment_id': payment.id, 'payment_name': payment.name}

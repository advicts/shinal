from odoo import http
from odoo.http import request


class PartnerLedgerController(http.Controller):

  @http.route('/api/partner_ledger',
              methods=['POST'],
              type="json",
              auth="public",
              website=True,
              csrf=False)
  def get_partner_ledger(self, **kw):
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
    result = self.get_partner_ledger_json(request_body['partner_id'], request_body['from_date'],
                                          request_body['to_date'])
    return result

  def get_partner_ledger_json(self, partner_id, from_date, to_date):
    partner = request.env['res.partner'].sudo().browse(partner_id)

    bal_moves = request.env['account.move.line'].sudo().search([('partner_id', '=', partner.id), ('parent_state', '=', 'posted'),
              ('account_id.internal_type', 'in', ['payable', 'receivable']),
              ('date', '<', from_date)], order='date asc')
    balance = sum(bal_moves.mapped('amount_currency'))

    domain = [('partner_id', '=', partner.id), ('parent_state', '=', 'posted'),
              ('account_id.internal_type', 'in', ['payable', 'receivable']),
              ('date', '>=', from_date), ('date', '<=', to_date)]
    moves = request.env['account.move.line'].sudo().search(domain, order='date asc')
    lines = []
    for move in moves:
      balance = balance+move.amount_currency 
      lines.append({
          'date': move.date,
          'date_maturity': move.date_maturity,
          'name': move.name,
          'move_id': move.move_id.name,
          'debit': abs(move.amount_currency) if move.debit>0 else 0,
          'credit':  abs(move.amount_currency) if move.credit>0 else 0,
          'matching_number': move.matching_number,
          'reconciled': move.reconciled,
          'amount_residual': move.amount_residual,
          'cumulated_balance': balance,
          'balance': move.balance
      })
    return {
        'partner_name': partner.name,
        'partner_phone': partner.phone,
        'from_date': from_date,
        'to_date': to_date,
        'debit': abs(balance) if move.debit>0 else 0,
        'credit': abs(balance) if move.credit>0 else 0,
        'lines': lines
    }

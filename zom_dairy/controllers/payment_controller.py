from odoo import http
from odoo.http import request
import logging


class Payment(http.Controller):
    @http.route('/api/action/payment',
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
                "message":
                "Authentication Errors : Set Authorization Code in Header",
                "data": False
            }
        if request.httprequest.headers[
                'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
            return {
                "status": 403,
                "message": "Authentication Errors : not authenticate",
                "data": False
            }
        logging.info(request_body)
        result = self.payment_creator_action(request_body)
        return result

    def payment_creator_action(self, doc):
        IQD = request.env['res.currency'].search([('name', '=', 'IQD')])
        user_setting = request.env['res.users.zom_dairy'].sudo().search(
            [('user_id', '=', doc['user_id'])], limit=1)
        payment = request.env['account.payment'].sudo().create({
            'partner_id':
            doc['partner']['id'],
            'user_id':
            user_setting.user_id.id,
            'payment_type':
            'outbound',
            'partner_type':
            'supplier',
            'currency_id':IQD.id,
            'zom_ref':
            doc['order_ref'],
            'is_zom_app':
            True,
            'partner_latitude':
            doc['other_info']['location']['latitude'],
            'partner_longitude':
            doc['other_info']['location']['longitude'],
        
            'journal_id':user_setting.cash_journal.id,
            'amount':
            doc['amount'],
            'ref':
            doc['note'],
        })
        payment.action_post()
        user_setting.update_partner(doc['partner']['id'])
        return {'payment_id': payment.id, 'payment_name': payment.name}

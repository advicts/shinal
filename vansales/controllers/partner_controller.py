from odoo import http
from odoo.http import request
import logging


class PartnerController(http.Controller):
    @http.route('/vansales/action/locationupdate',
                methods=['POST'],
                type="json",
                auth="public",
                website=True,
                csrf=False)
    def action_partner_location(self, **kw):
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
        result = self.update_location_action(request_body)
        return result

    def update_location_action(self, doc):
        partner = request.env['res.partner'].sudo().browse(doc['partner_id'])
        if partner:
            partner.partner_latitude = doc['other_info']['location'][
                'latitude']
            partner.partner_longitude = doc['other_info']['location'][
                'longitude']
            return {'partner': partner.id, 'status': 'done'}
        return {'partner': 0, 'status': 'failed'}

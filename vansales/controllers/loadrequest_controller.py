from odoo import http
from odoo.http import request
import base64


class LoadRequest(http.Controller):
    @http.route('/vansales/action/loadrequest',
                methods=['POST'],
                type="json",
                auth="public",
                website=True,
                csrf=False)
    def action_loadrequest(self, **kw):
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
        result = self.loadrequest_creator_action(request_body)
        return result

    def loadrequest_creator_action(self, request_body):
        user_setting = request.env['res.users.vansales'].sudo().search(
            [('user_id', '=', request_body['doc']['user_id'])],
            limit=1)
        order = request.env['stock.picking'].sudo().create({
            'picking_type_id':
            user_setting.load_request_stock_picking_type.id,
            'location_id':
            user_setting.load_request_stock_picking_type.default_location_src_id.id,
            'location_dest_id':
            user_setting.load_request_stock_picking_type.default_location_dest_id.id,
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
            # 'move_lines':
            'move_ids_without_package':
            self.inti_move_lines(request_body['doc']['cart'],user_setting),
        })
        try:
            if 'note' in request_body['doc']:
                post_vars = {'subject': "Note",
                            'body': request_body['doc']['note']}
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
        return {'order_id': order.id, 'order_name': order.name}

    def inti_move_lines(self, lines,user_setting):
        arg_order_line = []
        for order_line in lines:
            order_line_values = {
                'name': order_line['product'],
                'product_id': order_line['product_id'],
                'location_id':user_setting.load_request_stock_picking_type.default_location_src_id.id,
                'location_dest_id':user_setting.load_request_stock_picking_type.default_location_dest_id.id,
                'product_uom': order_line['product_uom']['id'],
                'product_uom_qty': order_line['qty'],
            }

            arg_order_line.append((0, 0, order_line_values))
        return arg_order_line

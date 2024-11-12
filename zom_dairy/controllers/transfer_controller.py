from odoo import http
from odoo.http import request
from odoo.tests import Form, tagged


class LoadRequest(http.Controller):
    @http.route('/api/action/transfer',
                methods=['POST'],
                type="json",
                auth="public",
                website=True,
                csrf=False)
    def action_transfer(self, **kw):
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
        result = self.transfer_creator_action(request_body)
        return result

    def transfer_creator_action(self, request_body):
        user_setting = request.env['res.users.zom_dairy'].sudo().search(
            [('user_id', '=', request_body['user_id'])],
            limit=1)
        receive_milk_driver_operation_type_id = request.env['stock.picking.type'].sudo().browse(request_body['driver']['id'])

        order = request.env['stock.picking'].sudo().create({
            'picking_type_id':
            receive_milk_driver_operation_type_id.id,
            'location_id':
            receive_milk_driver_operation_type_id.default_location_src_id.id,
            'location_dest_id':
            receive_milk_driver_operation_type_id.default_location_dest_id.id,
            'zom_ref':
            request_body['order_ref'],
            'is_zom_app':
            True,
            'partner_latitude':
            request_body['other_info']['location']['latitude'],
            'partner_longitude':
            request_body['other_info']['location']['longitude'],
            'user_id':
            user_setting.user_id.id,
            'move_ids_without_package':[(0, 0, {
                'name':request_body['product']['name'],
                'product_id': request_body['product']['id'],
                'product_uom': request_body['product']['uom_po_id'],
                'product_uom_qty': request_body['qty'],
                'location_id':receive_milk_driver_operation_type_id.default_location_src_id.id,
                'location_dest_id':receive_milk_driver_operation_type_id.default_location_dest_id.id,

            })]
        })
        order.action_confirm()
        self.check_validate_pickings(order)
        return {'order_id': order.id, 'order_name': order.name}


    def check_validate_pickings(self, pick):
        try:
            pick.sudo().action_assign()
            wiz_act = pick.sudo().button_validate()
            if wiz_act and wiz_act.get('res_model'):
                if wiz_act["res_model"] == 'stock.immediate.transfer':
                    wz_immediate_transfer = Form(
                        request.env['stock.immediate.transfer'].sudo(
                        ).with_context(wiz_act['context'])).save()
                    wz_immediate_transfer.process()
                elif wiz_act["res_model"] == 'stock.overprocessed.transfer':
                    wz_overprocessed = Form(
                        request.env['stock.overprocessed.transfer'].sudo(
                        ).with_context(wiz_act['context'])).save()
                    wz_overprocessed.process()
                elif wiz_act["res_model"] == 'stock.backorder.confirmation':
                    wz_backorder_confirmation = Form(
                        request.env['stock.backorder.confirmation'].sudo(
                        ).with_context(wiz_act['context'])).save()
                    wz_backorder_confirmation.process()
            return {"picking_id":pick.id}
        except Exception as e:
            return {"error":e}



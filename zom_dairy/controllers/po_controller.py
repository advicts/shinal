from odoo import http
from odoo.http import request
from odoo.tests import Form, tagged
import logging
from datetime import datetime



class Sale(http.Controller):
    @http.route('/api/action/order',
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
        result = self.order_creator_action(request_body)
        return result

    def order_creator_action(self, request_body):
        IQD = request.env['res.currency'].search([('name', '=', 'IQD')])
        user_setting = request.env['res.users.zom_dairy'].sudo().search(
            [('user_id', '=', request_body['user_id'])],
            limit=1)
        partner = request.env['res.partner'].sudo().browse(request_body['partner']['id'])

        order = request.env['purchase.order'].sudo().create({
            'partner_id':
            partner.id,
            'currency_id':IQD.id,
            'po_ref':
            request_body['order_ref'],
            'collection_center_id':user_setting.collection_center_id.id,
            'is_external_purchase_order':True,
            'partner_latitude':
            request_body['other_info']['location']['latitude'],
            'partner_longitude':
            request_body['other_info']['location']['longitude'],
            'picking_type_id':user_setting.collection_center_id.receive_milk_operation_type_id.id,
            'user_id':
            user_setting.user_id.id,
            'order_line':[(0, 0, {
                'product_id':request_body['product']['id'],
                'product_qty':request_body['qty'],
                'product_uom':request_body['product']['uom_po_id'],
                'price_unit':request_body['product']['standard_price'],
                'currency_id':IQD.id,

            })],
        }) 
        order.with_context(direct_approve=True).button_confirm()
        picking_result =self.check_validate_pickings(order)
        try:
          self.check_validate_invoices(order, user_setting)
        except:
          pass
        return {'order_id': order.id, 'order_name': order.name,"delivery":picking_result}


    def check_validate_pickings(self, order):
        if order.picking_ids:
            pick = order.picking_ids
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


    def check_validate_invoices(self, order, user_setting):
        order.sudo().action_create_invoice()
        logging.info(order.invoice_ids)
        if order.invoice_ids:
            for invoice in order.invoice_ids:
                invoice.invoice_date= datetime.today()
                invoice.action_post()

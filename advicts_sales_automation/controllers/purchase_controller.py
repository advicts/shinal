import json
from odoo import http
from odoo.http import request
from datetime import datetime

class PurchaseOrderAPI(http.Controller):

    @http.route('/api/purchaseorder/create', type='http', csrf=False, auth='user', methods=['POST'])
    def create_purchase_order(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            partner_no = payload.get('account_number', False)
            date_order = payload.get('order_date', False)
            origin = payload.get('origin', '')
            lines_data = payload.get('lines', [])

            partner = request.env['res.partner'].search([('ref', '=', partner_no)], limit=1)
            if not partner:
                response = {'code': 400, 'status': 'error', 'message': 'Invalid partner.'}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 400
                return response_obj

            purchase_order = request.env['purchase.order'].create({
                'partner_id': partner.id,
                'date_order': date_order,
                'origin': origin,
            })

            if purchase_order:
                lines_to_create = []
                for line_data in lines_data:
                    api_id = line_data.get('product')
                    product_product = request.env['product.product'].search([('api_id', '=', api_id)], limit=1)
                    if not product_product:
                        response = {'code': 400, 'status': 'error', 'message': 'Invalid product.'}
                        response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                        response_obj.status_code = 400
                        return response_obj
                    product_id = product_product.id

                    quantity = line_data.get('quantity', 0)
                    price = line_data.get('purchase_price', 0.0)

                    values = {
                        'order_id': purchase_order.id,
                        'product_id': product_id,
                        'product_qty': quantity,
                        'price_unit': price,
                        'date_planned': date_order,
                    }

                    lines_to_create.append((0, 0, values))

                purchase_order.write({'order_line': lines_to_create})
                purchase_order.button_confirm()

                response = {'code': 200, 'status': 'success', 'message': 'Purchase order created successfully.', 'order_id': purchase_order.id}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 200
                return response_obj

            else:
                response = {'code': 400, 'status': 'error', 'message': 'Failed to create purchase order.'}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 400
                return response_obj

        except Exception as e:
            response = {'code': 400, 'status': 'error', 'message': str(e)}
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

    @http.route('/api/purchaseorder/<int:purchase_order_id>', type='http', csrf=False, auth='user', methods=['GET'])
    def get_purchase_order_by_id(self, purchase_order_id, **kwargs):
        try:
            purchase_order = request.env['purchase.order'].browse(purchase_order_id)
            if purchase_order:
                
                date_order_str = purchase_order.date_order.strftime('%Y-%m-%d %H:%M:%S')

                purchase_order_data = {
                    'id': purchase_order.id,
                    'partner_id': purchase_order.partner_id.ref,
                    'date_order': date_order_str,
                    'origin': purchase_order.origin,
                    'lines': []
                }

                for line in purchase_order.order_line:
                    line_data = {
                        'product_id': line.product_id.api_id,
                        'product_qty': line.product_qty,
                        'price_unit': line.price_unit,
                        'date_planned': line.date_planned.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    purchase_order_data['lines'].append(line_data)

                response = {'code': 200, 'status': 'success', 'data': purchase_order_data}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 200
                return response_obj
            else:
                response = {'code': 404, 'status': 'error', 'message': 'Purchase order not found.'}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 404
                return response_obj
        except Exception as e:
            response = {'code': 400, 'status': 'error', 'message': str(e)}
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

    @http.route('/api/purchaseorder/list', type='http', auth='user', methods=['GET'])
    def get_purchase_order_list(self, **kwargs):
        try:
            page = int(kwargs.get('page', 1))
            page_size = int(kwargs.get('page_size', 10))
            offset = (page - 1) * page_size

            search_term = kwargs.get('search', '')
            domain = [('name', 'ilike', search_term)]

            order_by = kwargs.get('order_by', 'date_order')
            order_direction = kwargs.get('order_direction', 'asc')

            if order_direction not in ['asc', 'desc']:
                order_direction = 'asc'

            order = f'{order_by} {order_direction}'

            purchase_orders = request.env['purchase.order'].search(domain, offset=offset, limit=page_size, order=order)

            purchase_order_list = []
            for purchase_order in purchase_orders:
                date_order_str = purchase_order.date_order.strftime('%Y-%m-%d %H:%M:%S')

                purchase_order_data = {
                    'id': purchase_order.id,
                    'partner_id': purchase_order.partner_id.ref,
                    'date_order': date_order_str,
                    'origin': purchase_order.origin,
                    'lines': []
                }

                for line in purchase_order.order_line:
                    line_data = {
                        'product_id': line.product_id.api_id,
                        'product_qty': line.product_qty,
                        'price_unit': line.price_unit,
                        'date_planned': line.date_planned.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    purchase_order_data['lines'].append(line_data)

                purchase_order_list.append(purchase_order_data)

            total_count = request.env['purchase.order'].search_count(domain)

            response = {
                'code': 200,
                'status': 'success',
                'data': {
                    'purchase_orders': purchase_order_list,
                    'total_count': total_count
                }
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj

        except Exception as e:
            response = {'code': 400, 'status': 'error', 'message': str(e)}
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

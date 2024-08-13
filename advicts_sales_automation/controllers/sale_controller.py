import json
from odoo import http
from odoo.http import request
from datetime import timedelta
from datetime import datetime


class SaleOrderAPI(http.Controller):

    @http.route('/api/saleorder/create', type='http',csrf=False, auth='user', methods=['POST'])
    def create_sale_order(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            partner_no = payload.get('account_number', False)
            note = payload.get('note', '')     
            is_dropship_no = payload.get('is_dropshipping', False)
            source_name = payload.get('access_channel', 'pos')
            origin = payload.get('invoice_no') 
            date_order = payload.get('sale_date', False)

            is_dropship = False
            if is_dropship_no == 1:
                is_dropship = True

            lines_data = payload.get('lines', [])

            partner = request.env['res.partner'].search([('ref', '=', partner_no)], limit=1)
            if not partner:
                response= {'code': 400, 'status': 'error', 'message': 'Invalid partner.'} 
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 400
                return response_obj

            source_gate = request.env['utm.source'].search([('name', '=', source_name)], limit=1)
            if not source_gate:
                response = {'code': 400, 'status': 'error', 'message': 'Invalid source.'} 
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 400
                return response_obj

            partner_id = partner.id
            source_id = source_gate.id

            sale_order = request.env['sale.order'].create({
                'partner_id': partner_id,
                'date_order': date_order,
                'note': note,
                'origin': origin, 
                'source_id': source_id,  
            })

            if sale_order:
                lines_to_create = []
                for line_data in lines_data:
                    api_id = line_data.get('product')
                    product_product = request.env['product.product'].search([('api_id', '=', api_id)], limit=1)
                    if not product_product:
                        response= {'code': 400, 'status': 'error', 'message': 'Invalid product.'}  
                        response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                        response_obj.status_code = 400
                        return response_obj
                    product_id = product_product.id

                    quantity = line_data.get('quantity', 0)
                    price = line_data.get('sale_price', 0.0)
                    discount = line_data.get('discount', 0.0)
                    vendor_id = line_data.get('vendor_id', False)
                    purchase_price = line_data.get('purchase_price') 

                    values = {
                        'order_id': sale_order.id,
                        'product_id': product_id,
                        'product_uom_qty': quantity,
                        'price_unit': price,
                        'discount': discount,
                    }
                    if is_dropship:
                        values['purchase_price'] = purchase_price

                    lines_to_create.append((0, 0, values))

                sale_order.write({'order_line': lines_to_create})

                invoice_id=[]
                if is_dropship:
                    try:
                        sale_order.action_confirm()

                        for sale_order_line in sale_order.order_line:
                            for purchase_line in sale_order_line.purchase_line_ids:
                                purchase_line.write({'price_unit': sale_order_line.purchase_price})

                        for purchase_order in sale_order.order_line.mapped('purchase_line_ids.order_id'):
                            purchase_order.button_confirm()

                            for picking in purchase_order.picking_ids:
                                try:
                                    picking.action_set_quantities_to_reservation()
                                except:
                                    pass
                                picking.button_validate()

                        advance_payment_inv_model = request.env['sale.advance.payment.inv']
                        advance_payment_inv = advance_payment_inv_model.create({'sale_order_ids': [(4, sale_order.id)]})
                        advance_payment_inv.create_invoices()

                        invoice_id = sale_order.invoice_ids.ids
                        sale_invoice = request.env['account.move'].browse(invoice_id)
                        if not sale_invoice:
                            response={'code': 400 ,'status': 'error', 'message': 'Failed to create the invoice from the sale order.'}  
                            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                            response_obj.status_code = 400
                            return response_obj
                        sale_invoice.action_post()

                        for purchase_order in sale_order.order_line.mapped('purchase_line_ids.order_id'):

                            bill_id = purchase_order.action_create_invoice()
                            bill = request.env['account.move'].browse(bill_id.get('res_id'))
                            if not bill:
                                response= {'code': 400 ,'status': 'error', 'message': 'Failed to create the bill from the purchase order.'}
                                    
                                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                                response_obj.status_code = 400
                                return response_obj

                            invoice_date = datetime.date.today()
                            bill.write({'invoice_date': invoice_date})
                            bill.action_post()
                    except Exception as e:
                        response ={'code': 400 ,'status': 'error', 'message': str(e)}   
                         
                        response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                        response_obj.status_code = 400
                        return response_obj

                response = {'code': 200, 'status': 'success', 'message': 'Sale order created successfully.', 'order_id': sale_order.id}
                 
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 200
                return response_obj

            else:
                response ={'code': 400, 'status': 'error', 'message': 'Failed to create sale order.'}
                
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 400
                return response_obj
            
        except Exception as e:
            response= {'code': 400, 'status': 'error', 'message': str(e)} 
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

    # @http.route('/api/saleorder/update', type='json', auth='user', methods=['POST'])
    # def update_sale_order(self, **kwargs):
    #     # Add your code here
    #     pass

   
    @http.route('/api/saleorder/<int:sale_order_id>', type='http',csrf=False, auth='user', methods=['GET'])
    def get_sale_order_by_id(self, sale_order_id, **kwargs):
        try:
            sale_order = request.env['sale.order'].browse(sale_order_id)
            if sale_order:
                # Serialize sale order data
                date_order_str = sale_order.date_order.strftime('%Y-%m-%d %H:%M:%S')

                sale_order_data = {
                    'id': sale_order.id,
                    'partner_id': sale_order.partner_id.id,
                    'date_order': date_order_str,
                    'note': sale_order.note,
                    'invoice_no': sale_order.origin, 
                    'source_id': sale_order.source_id.id,
                    'lines': []
                }

                for line in sale_order.order_line:
                    line_data = {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'purchase_price': line.purchase_price
                    }
                    sale_order_data['lines'].append(line_data)

                response={'code': 200, 'status': 'success', 'data': sale_order_data}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 200
                return response_obj
            else:
                response={'code': 404, 'status': 'error', 'message': 'Sale order not found.'}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 404
                return response_obj
        except Exception as e:
            response={'code': 400, 'status': 'error', 'message': str(e)} 
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj



    @http.route('/api/saleorder/list', type='http', auth='user', methods=['GET'])
    def get_sale_order_list(self, **kwargs):
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

            sale_orders = request.env['sale.order'].search(domain, offset=offset, limit=page_size, order=order)
 

            sale_order_list = []
            for sale_order in sale_orders: 
                date_order_str = sale_order.date_order.strftime('%Y-%m-%d %H:%M:%S')

                sale_order_data = {
                    'id': sale_order.id,
                    'partner_id': sale_order.partner_id.id,
                    'date_order': date_order_str,
                    'note': sale_order.note,
                    'origin': sale_order.origin, 
                    'source_id': sale_order.source_id.id,
                    'lines': []
                }

                for line in sale_order.order_line:
                    line_data = {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'purchase_price': line.purchase_price
                    }
                    sale_order_data['lines'].append(line_data)

                sale_order_list.append(sale_order_data)

            total_count = request.env['sale.order'].search_count(domain)

            response= {
                'code': 200,
                'status': 'success',
                'data': {
                    'sale_orders': sale_order_list,
                    'total_count': total_count
                }
            } 
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj

        except Exception as e:
            response={'code': 400, 'status': 'error', 'message': str(e)} 
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj


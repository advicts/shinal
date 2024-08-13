from odoo import http
from odoo.http import request
from datetime import timedelta
from datetime import datetime
import datetime
import json
from datetime import datetime
from odoo import http
from odoo.http import request


class SaleOrderAPI(http.Controller):
 
    @http.route('/api/saleorder/create_update', type='json', auth='user', methods=['POST'])
    def create_update_sale_order_lines(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            sale_order_id = payload.get('id', False)
            partner_no = payload.get('account_number', False)
            note = payload.get('note', '')     
            is_dropship_no =payload.get('is_dropshipping', False)
            source_name =payload.get('access_channel', 'pos')
            origin =payload.get('invoice_no') 
            date_order = payload.get('sale_date', False)


            is_dropship =False

            if is_dropship_no==1:
                is_dropship=True
    
            lines_data = payload.get('lines', [])

            sale_order=[]
             
            sale_order = request.env['sale.order'].browse(sale_order_id)
            
            partner =request.env['res.partner'].search([('ref', '=', partner_no)], limit=1)
            if not partner:
                return {'code': 400 ,'status': 'error', 'message': 'Invalid partner .'}

            source_gate =request.env['utm.source'].search([('name', '=', source_name)], limit=1)
            if not source_gate:
                return {'code': 400 ,'status': 'error', 'message': 'Invalid source  .'}

            partner_id=partner.id
            source_id=source_gate.id
 
            if not sale_order: 
                    sale_order = request.env['sale.order'].create({
                        'partner_id': partner_id,
                        'date_order': date_order,
                        'note':note,
                        'origin':origin, 
                        'source_id':source_id,  

                    })
            else :
                  
                if partner_id:
                    sale_order.write({
                        'partner_id': partner_id,
                    })
                if note:
                    sale_order.write({
                        'note': note,
                    }) 
                if origin:
                    sale_order.write({
                        'origin': origin,
                    }) 
                if source_id:
                    sale_order.write({
                    'source_id':source_id
                    })
            

            if sale_order:
                lines_to_update = [] 
                existing_lines = sale_order.order_line
                
                for existing_line in existing_lines:
                    if existing_line.product_id.id not in [line_data.get('product') for line_data in lines_data]:
                        values = {
                            'product_uom_qty': 0,
                            'price_unit': 0,
                            'discount': 0,
                            # 'points':0 ,
                            # 'scheduled_date':date_order
                        }
                        lines_to_update.append((1, existing_line.id, values))
 
    
                for line_data in lines_data:
                    api_id = line_data.get('product')
                    productproduct =request.env['product.product'].search([('api_id', '=', api_id)], limit=1)
                    if not productproduct:
                        return {'code': 400 ,'status': 'error', 'message': 'Invalid product  .'}
                    product_id=productproduct.id



                    quantity = line_data.get('quantity', 0)
                    price = line_data.get('sale_price', 0.0)
                    
                    discount = line_data.get('discount', 0.0)
                    vendor_id = line_data.get('vendor_id', False)
                    purchase_price = line_data.get('purchase_price') 

                    # points = line_data.get('points', 0.0)

                    existing_line = existing_lines.filtered(lambda line: line.product_id.id == product_id)
                    if vendor_id:
                            product_template = request.env['product.template'].search([('product_variant_ids', 'in', [product_id])], limit=1)

                            if product_template:
                                supplier_info = product_template.seller_ids.filtered(lambda info: info.partner_id.id == vendor_id)
                                
                                if not supplier_info:
                                    supplier_info = request.env['product.supplierinfo'].create({
                                        'partner_id': vendor_id,
                                        'product_tmpl_id': product_template.id,
                                        'sequence': 1  
                                    })
                                sequence=2
                                for supplier in product_template.seller_ids:
                                    if supplier.partner_id == supplier_info.partner_id:
                                        supplier.sequence = 1
                                    else:
                                        supplier.sequence = sequence
                                        sequence +=1

                    if existing_line:
                        values = {
                            'product_uom_qty': quantity,
                            'price_unit': price,
                            'discount': discount,
                            # 'points':points ,
                            # 'scheduled_date':date_order
                        }
                        if is_dropship:
                            values['purchase_price'] = purchase_price
                        lines_to_update.append((1, existing_line.id, values)) 
                    else:
                        values = {
                            'order_id': sale_order.id,
                            'product_id': product_id,
                            'product_uom_qty': quantity,
                            'price_unit': price,
                            'discount': discount,
                            # 'points':points,
                            # 'scheduled_date':date_order

                        }
                        if is_dropship:
                            values['purchase_price'] = purchase_price
                        lines_to_update.append((0, 0, values)) 


                 
                sale_order.write({ 'order_line': lines_to_update})
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
                            return {'code': 400 ,'status': 'error', 'message': 'Failed to create the invoice from the sale order.'}
                        sale_invoice.action_post()

                        for purchase_order in sale_order.order_line.mapped('purchase_line_ids.order_id'):

                            bill_id = purchase_order.action_create_invoice()
                            bill = request.env['account.move'].browse(bill_id.get('res_id'))
                            if not bill:
                                return {'code': 400 ,'status': 'error', 'message': 'Failed to create the bill from the purchase order.'}
                            invoice_date = datetime.date.today()
                            bill.write({'invoice_date': invoice_date})
                            bill.action_post()
                    except Exception as e:
                        return {'code': 400 ,'status': 'error', 'message': str(e)}   
                    # return {
                    #     'status': 'Done',
                    #     'invoice_id':invoice_id
                    # }



                return {'code': 200,'status': 'success', 'message': 'Sale order lines updated successfully.','order_id':sale_order.id,'invoice_id':invoice_id}
           
            else:
                return {'code': 400 ,'status': 'error', 'message': 'Invalid Sale Order ID.'}
            
        except Exception as e:
            return {'code': 400 ,'status': 'error', 'message': str(e)}

    
    @http.route('/api/contact/create_update', type='json', auth='user', methods=['POST'])
    def create_update_res_partner(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            account_number = payload.get('account_number')
            business_name = payload.get('business_name')
            company_id = payload.get('company_id')
            primary_phone_number = payload.get('primary_phone_number')
            secondary_phone_number = payload.get('secondary_phone_number')
            email = payload.get('email')
            city_name = payload.get('city_name')
            address = payload.get('address')
            preferred_language = payload.get('preferred_language')
            business_type = payload.get('business_type')
            imei_code = payload.get('imei_code')
            longitude = payload.get('longitude')
            latitude = payload.get('latitude')
            access_channels = payload.get('access_channels')
            full_name = payload.get('full_name')
            # pricing_profile = payload.get('pricing_profile')
            # user_id = payload.get('user_id')
            


             
            Partner = request.env['res.partner']

            partner_vals = {}
            if business_name:
                partner_vals['name'] = business_name
            # if company_id:
            #     partner_vals['company_id'] = company_id   
            if primary_phone_number:
                partner_vals['phone'] = primary_phone_number
            if secondary_phone_number:
                partner_vals['mobile'] = secondary_phone_number
            if email:
                partner_vals['email'] = email
            if city_name:
                partner_vals['city'] = city_name
            if address:
                partner_vals['street'] = address
            if preferred_language:
                partner_vals['lang'] = preferred_language
            if business_type:
                partner_vals['function'] = business_type
            if imei_code:
                partner_vals['imei_code'] = imei_code
            if longitude:
                partner_vals['partner_longitude'] = longitude
            if latitude:
                partner_vals['partner_latitude'] = latitude
            if access_channels:
                partner_vals['access_channels'] = access_channels

            partner = Partner.search([('ref', '=', account_number)], limit=1)
            createorupdate="created"
            if partner: 
                createorupdate="updated"
                partner.write(partner_vals) 
            else: 
                createorupdate="created"
                partner_vals['ref'] = account_number
                partner = Partner.create(partner_vals)
            
            invoice_partner = Partner.search([('parent_id', '=', partner.id),('type', '=', 'invoice')], limit=1)
            if full_name:
                 
                if invoice_partner: 
                    invoice_partner.write({'name': full_name})
                else: 
                    invoice_partner_vals = {
                        'name': full_name,   
                        'parent_id': partner.id,
                        'type': 'invoice'
                    }
                    invoice_partner = Partner.create(invoice_partner_vals)
  
            return {
                    'code':200,
                    'message':'%s successful.' % createorupdate,
                    'error':'',
                    'data':{
                        'partner_id': partner.id,
                        'action': createorupdate,
                        'account_number': partner.ref,
                        'business_name': partner.name,
                        'full_name': invoice_partner.name,
                        'company_id': partner.company_id.id,
                        'primary_phone_number': partner.phone,
                        'secondary_phone_number': partner.mobile,
                        'email': partner.email,
                        'city_name': partner.city,
                        'address': partner.street,
                        'preferred_language': partner.lang,
                        'business_type': partner.function,
                        'imei_code': partner.imei_code,
                        'longitude': partner.partner_longitude,
                        'latitude': partner.partner_latitude,
                        'access_channels': partner.access_channels,
                    }
                }


        except Exception as e:
            return {
                    'code':400,
                    'message': '',
                    'error':str(e),
                    'data':{}
                    }
            

 
    @http.route('/api/product/create_update', type='json', auth='user', methods=['POST'])
    def create_update_product(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            api_id = payload.get('id', False)
            product_name = payload.get('product_name', False)
            category_name = payload.get('group', False)
            description = payload.get('description', '')
            price = payload.get('price', 0.0)
            
            
            Product = request.env['product.template']
            Category = request.env['product.category']

             
            category = Category.search([('name', '=', category_name)], limit=1)
            if not category:
                category = Category.create({'name': category_name})

            product_vals = {
                'name': product_name,
                'description': description,
                'list_price': price,
                'categ_id': category.id, 
            }

            product = Product.search([('api_id', '=', api_id)], limit=1)
            if product:
                product.write(product_vals)
                action = 'updated'
            else:
                product_vals['api_id'] = api_id
                product = Product.create(product_vals)
                action = 'created'

            return {
                'code': 200,
                'message': f'Product {action} successfully.',
                'error': '',
                'data': {
                    'product_id': product.id,
                    'action': action,
                    'id': product.api_id,
                    'name': product.name,
                    'description': product.description,
                    'price': product.list_price,
                    'group': category.name, 
                }
            }

        except Exception as e:
            return {
                'code': 400,
                'message': '',
                'error': str(e),
                'data': {}
            }



    @http.route('/api/create_withdraw_payment', type='json', auth='user', methods=['POST'])
    def create_withdraw_payment(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            customer_id = payload.get('customer_id', False)
            amount = payload.get('amount', False)
            date = payload.get('date', datetime.now().strftime('%Y-%m-%d'))
            ref = payload.get('ref')

            # Find the correct journal for withdrawals
            journal = request.env['account.journal'].sudo().search([('isfor_withdraw', '=', True)], limit=1)

            # Create payment
            if customer_id and amount and journal:
                payment_data = {
                    'partner_id': customer_id,
                    'payment_type': 'outbound',
                    'amount': amount,
                    'journal_id': journal.id,
                    'payment_method_line_id': journal.outbound_payment_method_line_ids[0].id,
                    'date': date,
                    'ref': ref,
                    'partner_type':'customer',
                    'currency_id':journal.currency_id.id,
                    'company_id': journal.company_id.id,
                    'is_internal_transfer': False, 
                }

                payment = request.env['account.payment'].sudo().create(payment_data)

                # Post the payment
                payment.action_post()

                return {'success': 'Payment created and posted successfully.', 'payment_id': payment.id}
            else:
                return {'error': 'Customer id, Amount, or Withdrawal journal is missing.'}
        except Exception as e:
            return {'error': str(e)}

 

    @http.route('/api/create_deposit_payment', type='json', auth='user', methods=['POST'])
    def create_deposit_payment(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            customer_id = payload.get('customer_id', False)
            amount = payload.get('amount', False)
            date = payload.get('date', datetime.now().strftime('%Y-%m-%d'))
            ref = payload.get('ref')

            # Find the correct journal for deposit
            journal = request.env['account.journal'].sudo().search([('isfor_deposit', '=', True)], limit=1)

            # Create payment
            if customer_id and amount and journal:
                payment_data = {
                    'partner_id': customer_id,
                    'payment_type': 'inbound',
                    'amount': amount,
                    'journal_id': journal.id,
                    'payment_method_line_id': journal.inbound_payment_method_line_ids[0].id,
                    'date': date,
                    'ref': ref,
                    'partner_type':'customer', 
                    'currency_id':journal.currency_id.id,
                    'company_id': journal.company_id.id,
                    'is_internal_transfer': False,
                }

                payment = request.env['account.payment'].sudo().create(payment_data)

                # Post the payment
                payment.action_post()

                return {'success': 'Payment created and posted successfully.', 'payment_id': payment.id}
            else:
                return {'error': 'Customer id, Amount, or Withdrawal journal is missing.'}
        except Exception as e:
            return {'error': str(e)}



    @http.route('/api/create_bank_statement_line', type='json', auth='user', methods=['POST'])
    def create_bank_statement_line(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            amount = payload.get('amount', False)
            date = payload.get('date', datetime.now().strftime('%Y-%m-%d'))
            payment_ref = payload.get('payment_ref')
 
            journal = request.env['account.journal'].sudo().search([('isfor_deposit', '=', True)], limit=1)

            # Check if the request is for creating account.bank.statement.line records
            if amount and journal:
                # Create account.bank.statement.line record 
                statement_data = {  
                    'amount': amount,
                    'journal_id': journal.id,
                    'payment_ref': payment_ref,
                    'date': date, 
                    'currency_id':journal.currency_id.id,
                    'company_id': journal.company_id.id,
                }
                statement_line = request.env['account.bank.statement.line'].sudo().create(statement_data)

                return {'success': 'Bank statement line created successfully.', 'statement_line_id': statement_line.id}
            else:
                return {'error': 'Invalid model or method specified in the request.'}
        except Exception as e:
            return {'error': str(e)}
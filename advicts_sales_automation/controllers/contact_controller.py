from odoo import http
from odoo.http import request
from datetime import timedelta
from datetime import datetime
import datetime
import json 
  

class ContactAPI(http.Controller):
   
    @http.route('/api/contact/create', type='http', csrf=False, auth='user', methods=['POST'])
    def create_res_partner(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            account_number = payload.get('account_number')
            business_name = payload.get('business_name')
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
            partner_type = payload.get('partner_type')
            cash_account_ids = payload.get('cash_account_ids')

            Partner = request.env['res.partner']
            AccountAccount = request.env['account.account']
            AccountJournal = request.env['account.journal']

            partner_check = Partner.search([('ref', '=', account_number)], limit=1)
            if partner_check:
                response = {
                    'code': 409,
                    'message': '',
                    'error': 'This contact already exists.',
                    'data': ''
                }

                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 409
                return response_obj

            partner_vals = {
                'ref': account_number,
                'name': business_name,
                'phone': primary_phone_number,
                'mobile': secondary_phone_number,
                'email': email,
                'city': city_name,
                'street': address,
                'lang': preferred_language,
                'function': business_type,
                'imei_code': imei_code,
                'partner_longitude': longitude,
                'partner_latitude': latitude,
                'access_channels': access_channels,
                'partner_type': partner_type
            }
            partner = Partner.create(partner_vals)

            if full_name:
                invoice_partner_vals = {
                    'name': full_name,
                    'parent_id': partner.id,
                    'type': 'invoice'
                }
                invoice_partner = Partner.create(invoice_partner_vals)

            journals = []
            if partner_type in ['sales_represent', 'casher']:
                for cash_account_id in cash_account_ids:
                    if cash_account_id:
                        existing_journal = AccountJournal.search([('api_id', '=', cash_account_id)], limit=1)
                        if existing_journal:
                            journals.append(existing_journal.id)
                            continue  # Skip to the next cash_account_id

                        existing_account = AccountAccount.search([('account_type', '=', 'asset_cash')], order='code desc', limit=1)
                        new_code = '101501'
                        if existing_account:
                            new_code = str(int(existing_account.code) + 1)
                        else:
                            new_code = '101501'

                        account_vals = {
                            'name': f"{partner.name}'s Account",
                            'code': new_code,
                            'account_type': 'asset_cash',
                        }
                        account = AccountAccount.create(account_vals)

                        existing_journal = AccountJournal.search([('code', 'like', 'CH%'), ('type', '=', 'cash')], order='code desc', limit=1)
                        new_journal_code = 'CH001'
                        if existing_journal:
                            last_code = existing_journal.code
                            last_seq = int(last_code.replace('CH', ''))
                            new_journal_seq = last_seq + 1
                            new_journal_code = f"CH{new_journal_seq:03d}"
                        else:
                            new_journal_code = 'CH001'

                        journal_vals = {
                            'name': f"{partner.name}'s Cash Journal",
                            'code': new_journal_code,
                            'type': 'cash',
                            'company_id': request.env.user.company_id.id,
                            'default_account_id': account.id,
                            'owner_id': partner.id,
                            'api_id': cash_account_id
                        }
                        journal = AccountJournal.create(journal_vals)
                        journals.append(journal.id)

            # partner.write({'cash_account_ids':journals.ids})
            existing_cash_journals = AccountJournal.search([('api_id', 'in', cash_account_ids)])
            existing_cash_account_ids = existing_cash_journals.mapped('api_id')

            response = {
                'code': 200,
                'message': 'Partner created successfully.',
                'error': '',
                'data': {
                    'partner_id': partner.id,
                    'action': 'created',
                    'account_number': partner.ref,
                    'business_name': partner.name,
                    'full_name': invoice_partner.name if full_name else '',
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
                    'partner_type': partner_type,
                    'cash_account_ids': existing_cash_account_ids
                }
            }

            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj
        except Exception as e:
            response = {
                'code': 400,
                'message': '',
                'error': str(e),
                'data': {}
            }

            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

    @http.route('/api/contact/update', type='http',csrf=False, auth='user', methods=['POST'])
    def update_res_partner(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            account_number = payload.get('account_number')
            business_name = payload.get('business_name')
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
            cash_account_ids = payload.get('cash_account_ids', [])
            partner_type = payload.get('partner_type')

            Partner = request.env['res.partner']
            AccountAccount = request.env['account.account']
            AccountJournal = request.env['account.journal']

            partner_vals = {}
            if business_name:
                partner_vals['name'] = business_name
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
            if partner_type:
                partner_vals['partner_type'] = partner_type

            partner = Partner.search([('ref', '=', account_number)], limit=1)
            if partner:
                partner.write(partner_vals) 
                action = 'updated'
            else: 
                response= {
                    'code': 404,
                    'message': '',
                    'error': 'This contact not found.',
                    'data':'' 
                }
                
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 404
                return response_obj

                # action = 'not_found'
                            
            invoice_partner = Partner.search([('parent_id', '=', partner.id)], limit=1) 
            if full_name:
                invoice_partner.name =full_name 
             

            journals = []


            for cash_account_id in cash_account_ids:
                if cash_account_id:
                    existing_journal = AccountJournal.search([('api_id', '=', cash_account_id)], limit=1)
                    if existing_journal:
                        if existing_journal.owner_id != partner.id:
                            existing_journal.write({'owner_id': partner.id})
                        journals.append(existing_journal.id)
                    else:
                        existing_account = AccountAccount.search([('account_type', '=', 'asset_cash')], order='code desc', limit=1)
                        new_code = '101501'
                        if existing_account:
                            new_code = str(int(existing_account.code) + 1)
                        else:
                            new_code = '101501'

                        account_vals = {
                            'name': f"{partner.name}'s Account",
                            'code': new_code,
                            'account_type': 'asset_cash',
                        }
                        account = AccountAccount.create(account_vals)

                        existing_journal = AccountJournal.search([('code', 'like', 'CH%'), ('type', '=', 'cash')], order='code desc', limit=1)
                        new_journal_code = 'CH001'
                        if existing_journal:
                            last_code = existing_journal.code
                            last_seq = int(last_code.replace('CH', ''))
                            new_journal_seq = last_seq + 1
                            new_journal_code = f"CH{new_journal_seq:03d}"
                        else:
                            new_journal_code = 'CH001'

                        journal_vals = {
                            'name': f"{partner.name}'s Cash Journal",
                            'code': new_journal_code,
                            'type': 'cash',
                            'company_id': request.env.user.company_id.id,
                            'default_account_id': account.id,
                            'owner_id': partner.id,
                            'api_id': cash_account_id
                        }
                        journal = AccountJournal.create(journal_vals)
                        journals.append(journal.id)

            existing_journals = AccountJournal.search([('owner_id', '=', partner.id)])
            for journal in existing_journals:
                if journal.api_id not in cash_account_ids:
                    journal.write({'owner_id': False})

            existing_cash_account_ids=False
            if cash_account_ids:
                existing_cash_journals = AccountJournal.search([('api_id', 'in', cash_account_ids)])
                existing_cash_account_ids = existing_cash_journals.mapped('api_id')
            
            response= {
                'code': 200,
                'message': f'Partner {action} successfully.',
                'error': '',
                'data': {
                    'partner_id': partner.id if partner else None,
                    'action': action,
                    'account_number': account_number,
                    'business_name': business_name,
                    'primary_phone_number': primary_phone_number,
                    'secondary_phone_number': secondary_phone_number,
                    'email': email,
                    'city_name': city_name,
                    'address': address,
                    'preferred_language': preferred_language,
                    'business_type': business_type,
                    'imei_code': imei_code,
                    'longitude': longitude,
                    'latitude': latitude,
                    'access_channels': access_channels,
                    'full_name':  invoice_partner.name if invoice_partner else '',
                    'cash_account_ids': existing_cash_account_ids 

                }
            } 
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj
        except Exception as e:
            response= {
                'code': 400,
                'message': '',
                'error': str(e),
                'data': {}
            }
            
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj



    @http.route('/api/contact/<string:account_number>', type='http', auth='user', methods=['GET'])
    def get_res_partner(self, account_number, **kwargs):
        try:
            partner = request.env['res.partner'].search([('ref', '=', account_number)], limit=1)

            if not partner:
                response= {
                    'code': 404,
                    'message': 'Contact not found.',
                    'error': '',
                    'data': {}
                }  
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 404
                return response_obj


            invoice_partner = request.env['res.partner'].search([('parent_id', '=', partner.id)], limit=1) 
            AccountJournal = request.env['account.journal']


            existing_cash_journals = AccountJournal.search([('owner_id', '=', partner.id)])
            existing_cash_account_ids = existing_cash_journals.mapped('api_id')
            
            response = {
                'code': 200,
                'message': 'Contact retrieved successfully.',
                'error': '',
                'data': {
                    'account_number':partner.ref,
                    'partner_id': partner.id,
                    'business_name': partner.name,
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
                    'full_name':  invoice_partner.name if invoice_partner else '',
                    'cash_account_ids':existing_cash_account_ids

                }
            }
             
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj

            # return res
        except Exception as e:
            response={
                'code': 400,
                'message': '',
                'error': str(e),
                'data': {}
            } 
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

 
    @http.route('/api/contact/list', type='http', auth='user', methods=['GET'])
    def list_res_partners(self, **params):
        try: 

            page = int(params.get('page', 1))
            page_size = int(params.get('page_size', 10))
            search_term = params.get('search', '')
 
            offset = (page - 1) * page_size
 
            domain = ['|', '|', '|', 
                    ('name', 'ilike', search_term),
                    ('phone', 'ilike', search_term),
                    ('mobile', 'ilike', search_term),
                    ('email', 'ilike', search_term)]
 
            total_count = request.env['res.partner'].search_count(domain)

            
            order_by = params.get('order_by', 'id')
            order_direction = params.get('order_direction', 'asc')

            if order_direction not in ['asc', 'desc']:
                order_direction = 'asc'
 
            order = f'{order_by} {order_direction}'

            partners = request.env['res.partner'].search(domain, offset=offset, limit=page_size, order=order)
            AccountJournal = request.env['account.journal']


            all_journals = AccountJournal.search([('owner_id', '!=', False)])
            journals_by_owner = {}
            for journal in all_journals:
                owner_id = journal.owner_id.id
                if owner_id not in journals_by_owner:
                    journals_by_owner[owner_id] = []
                journals_by_owner[owner_id].append(journal.api_id)


            data = []
            for partner in partners:
                invoice_partners = partner.child_ids.filtered(lambda x: x.type == 'invoice')
                invoice_partner_name = invoice_partners[0].name if invoice_partners else ''
                            
                existing_cash_account_ids = journals_by_owner.get(partner.id, [])

                data.append({
                    'account_number':partner.ref,
                    'partner_id': partner.id,
                    'business_name': partner.name,
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
                    'full_name':  invoice_partner_name ,
                    'cash_account_ids':existing_cash_account_ids
                })

            response={
                'code': 200,
                'message': 'Contact list retrieved successfully.',
                'error': '',
                'data': {
                    'total_count': total_count,
                    'data': data
                }
            }
            

            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj
        except Exception as e:
            response={
                'code': 400,
                'message': '',
                'error': str(e),
                'data': {}
            } 

            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj

import json
from odoo import http
from odoo.http import request

class JournalAPI(http.Controller):

    @http.route('/api/journal/create', type='http', csrf=False, auth='user', methods=['POST'])
    def create_journal(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            name = payload.get('name')
            code = payload.get('code')
            cash_account_id = payload.get('cash_account_id')

            owner_account_number = payload.get('owner_account_number')

            AccountJournal = request.env['account.journal']
            AccountAccount = request.env['account.account']
            Partner = request.env['res.partner']

            # Check if the owner (partner) exists
            partner_check = Partner.search([('ref', '=', owner_account_number)], limit=1)
            # if not partner_check:
            #     response = {
            #         'code': 409,
            #         'message': '',
            #         'error': 'This contact does not exist.',
            #         'data': ''
            #     }
            #     return request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})

            # Check if journal code already exists
            journal_check = AccountJournal.search(['|',('api_id','=',cash_account_id),('code', '=', code)], limit=1)
            if journal_check:
                response = {
                    'code': 409,
                    'message': '',
                    'error': 'This journal code already exists.',
                    'data': ''
                }
                 
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 409
                return response_obj

            # Get the highest existing account code for asset_cash type
            existing_account = AccountAccount.search([('account_type', '=', 'asset_cash')], order='code desc', limit=1)
            new_code = '101501'
            if existing_account:
                new_code = str(int(existing_account.code) + 1)
 
            # Create account.account
            account_vals = {
                'name': f"{name}'s Account",
                'code': new_code,
                'account_type': 'asset_cash',
            }
            account = AccountAccount.create(account_vals)

            # Create account.journal
            journal_vals = {
                'name': name,
                'code': code,
                'type': 'cash',
                'company_id': request.env.user.company_id.id,
                'default_account_id': account.id,
                'owner_id': partner_check.id if partner_check else '', 
                'api_id':cash_account_id
            }
            journal = AccountJournal.create(journal_vals)

            response = {
                'code': 200,
                'message': 'Journal created successfully.',
                'error': '',
                'data': {
                    'cash_account_id':cash_account_id,
                    'journal_id': journal.id,
                    'name': journal.name,
                    'code': journal.code,
                    'default_account_id': journal.default_account_id.id,
                    'owner_account_no': journal.owner_id.ref,
                }
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj
        except Exception as e:
            response = {
                'code': 500,
                'message': 'An error occurred.',
                'error': str(e),
                'data': ''
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 500
            return response_obj


    @http.route('/api/journal/update', type='http', csrf=False, auth='user', methods=['POST'])
    def update_journal(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            name = payload.get('name')
            code = payload.get('code') 
            owner_id = payload.get('owner_id')
            cash_account_id = payload.get('cash_account_id')


            AccountJournal = request.env['account.journal']

            # Check if journal exists
            journal = AccountJournal.search([('api_id', '=', cash_account_id)], limit=1)
            if not journal:
                response = {
                    'code': 404,
                    'message': '',
                    'error': 'Journal not found.',
                    'data': ''
                }
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 404
                return response_obj
            # Update journal
            journal.write({
                'name': name,
                'code': code, 
                'owner_id': owner_id,
                # 'is_for_api': True
            })

            response = {
                'code': 200,
                'message': 'Journal updated successfully.',
                'error': '',
                'data': {
                    'cash_account_id': journal.api_id,
                    'name': journal.name,
                    'code': journal.code,
                    'default_account_id': journal.default_account_id.id,
                    'owner_account_no': journal.owner_id.ref,
                }
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj
        except Exception as e:
            response = {
                'code': 500,
                'message': 'An error occurred.',
                'error': str(e),
                'data': ''
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 500
            return response_obj


    @http.route('/api/journal/<int:cash_account_id>', type='http', csrf=False, auth='user', methods=['GET'])
    def get_journal(self, cash_account_id, **kwargs):
        try:
            AccountJournal = request.env['account.journal']

            # Check if journal exists
            journal = AccountJournal.search([('api_id', '=', cash_account_id)], limit=1)
            if not journal:
                response = {
                    'code': 404,
                    'message': '',
                    'error': 'Journal not found.',
                    'data': ''
                }
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 404
                return response_obj


            response = {
                'code': 200,
                'message': 'Journal retrieved successfully.',
                'error': '',
                'data': {
                    'cash_account_id': journal.api_id,
                    'name': journal.name,
                    'code': journal.code,
                    'default_account_id': journal.default_account_id.id,
                    'owner_account_no': journal.owner_id.ref,
                }
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj

        except Exception as e:
            response = {
                'code': 500,
                'message': 'An error occurred.',
                'error': str(e),
                'data': ''
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 500
            return response_obj


    @http.route('/api/journal', type='http', csrf=False, auth='user', methods=['GET'])
    def get_all_journals(self, **params):
        try: 
            page = int(params.get('page', 1))
            page_size = int(params.get('page_size', 10))
            search_term = params.get('search', '')
 
            offset = (page - 1) * page_size

            domain = ['|', '|', '|', '|', '|', 
                    ('name', 'ilike', search_term),
                    ('code', 'ilike', search_term),
                    ('api_id', 'ilike', search_term),
                    ('default_account_id.name', 'ilike', search_term),
                    ('owner_id.ref', 'ilike', search_term),
                    ('owner_id.name', 'ilike', search_term)]
 
            total_count = request.env['account.journal'].search_count(domain)
            
            order_by = params.get('order_by', 'id')
            order_direction = params.get('order_direction', 'asc')

            if order_direction not in ['asc', 'desc']:
                order_direction = 'asc'
 
            order = f'{order_by} {order_direction}'

            AccountJournal = request.env['account.journal']
            journals = AccountJournal.search(domain, offset=offset, limit=page_size, order=order)

            journals_list = []
            for journal in journals:
                journals_list.append({
                    'cash_account_id': journal.api_id,
                    'name': journal.name,
                    'code': journal.code,
                    'default_account_id': journal.default_account_id.id,
                    'owner_account_no': journal.owner_id.ref if journal.owner_id else '',
                })

            response = {
                'code': 200,
                'message': 'Journals retrieved successfully.',
                'error': '',
                'data': journals_list,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
            }
            
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj
        except Exception as e:
            response = {
                'code': 500,
                'message': 'An error occurred.',
                'error': str(e),
                'data': ''
            }
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 500
            return response_obj
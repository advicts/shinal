from odoo import http
from odoo.http import request
import json
from odoo import http
from odoo.http import request
import json

class TransactionsController(http.Controller):


    @http.route('/api/transactions', type='http', csrf=False, auth='user', methods=['POST'])
    def handle_transaction(self, **kwargs):
        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
            transaction_type = payload.get('transaction_type')
            amount = payload.get('amount')
            from_cash_account_id = payload.get('from_cash_account_id')
            to_cash_account_id = payload.get('to_cash_account_id')

            partner_account_no = payload.get('partner_account_no') 

 
            if transaction_type not in [
                'investment', 'withdraw','cash_transfer', 'transfer_to_cashier', 'transfer_from_cashier', 
                'transfer_sales_rep','partner_payment','partner_payment','partner_withdraw','payment_supplier', 'withdraw_supplier', 
                'refund_merchant', 'reload_merchant', 'sales_rep_to_cashier']:
                response = {'code': 400, 'message': '', 'error': 'Invalid transaction type', 'data': {}}
                response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                response_obj.status_code = 400
                return response_obj



            if transaction_type=='investment': 

                capital_account_id = request.env['account.account'].search([('is_for_api','=',True),('account_type', '=', 'liability_current')], limit=1).id
                 
                from_journal_id = request.env['account.journal'].search([('api_id', '=',from_cash_account_id)], limit=1)
                from_default_account_id = from_journal_id.default_account_id.id
    

                if not from_journal_id or not capital_account_id or not from_default_account_id:
                    response = {'code': 400, 'message': '', 'error': 'Journal or accounts not found', 'data': {}}
                    response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                    response_obj.status_code = 400
                    return response_obj

                move = request.env['account.move'].create({
                    'journal_id': from_journal_id.id,
                    'line_ids': [
                        (0, 0, {
                            'account_id': from_default_account_id,
                            'debit': amount,
                            'credit': 0,
                        }),
                        (0, 0, {
                            'account_id': capital_account_id,
                            'debit': 0,
                            'credit': amount,
                        }),
                    ]
                })
                move.action_post()

            elif transaction_type=='withdraw': 

                drawings_account_id = request.env['account.account'].search([('is_for_api','=',True),('account_type', '=', 'equity')], limit=1).id
                
                from_journal_id = request.env['account.journal'].search([('api_id', '=',from_cash_account_id)], limit=1)
                from_default_account_id = from_journal_id.default_account_id.id

                if not from_journal_id or not drawings_account_id or not from_default_account_id:
                    response = {'code': 400, 'message': '', 'error': 'Journal or accounts not found', 'data': {}}
                    response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                    response_obj.status_code = 400
                    return response_obj

                move = request.env['account.move'].create({
                    'journal_id': from_journal_id.id,
                    'line_ids': [
                        (0, 0, {
                            'account_id': drawings_account_id,
                            'debit': amount,
                            'credit': 0,
                        }),
                        (0, 0, {
                            'account_id': from_default_account_id,
                            'debit': 0,
                            'credit': amount,
                        }),
                    ]
                })
                move.action_post()
            
            elif transaction_type=='cash_transfer':
                
                from_journal_id = request.env['account.journal'].search([('api_id', '=',from_cash_account_id)], limit=1)
                to_journal_id = request.env['account.journal'].search([('api_id', '=',to_cash_account_id)], limit=1)
 

                if not from_journal_id.default_account_id or not to_journal_id.default_account_id:
                    response = {'code': 400, 'message': '', 'error': 'Accounts not found', 'data': {}}
                    response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                    response_obj.status_code = 400
                    return response_obj

                payment = request.env['account.payment'].create({
                    'is_internal_transfer': True,
                    'amount': amount,
                    'payment_type': 'outbound',
                    'journal_id': from_journal_id.id,
                    'destination_journal_id': to_journal_id.id,
                    'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
                })
                payment.action_post()
             
            
            elif transaction_type=='partner_payment':
                 
                partner = request.env['res.partner'].search([('ref', '=', partner_account_no)], limit=1) 
                from_journal_id = request.env['account.journal'].search([('api_id', '=',from_cash_account_id)], limit=1)

                if not partner or not from_journal_id:
                    response = {'code': 400, 'message': '', 'error': 'Partner or Cash account not found', 'data': {}}
                    response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                    response_obj.status_code = 400
                    return response_obj
 
                payment = request.env['account.payment'].create({
                    'partner_id': partner.id,
                    'amount': amount,
                    'payment_type': 'outbound',
                    'payment_method_id': request.env.ref('account.account_payment_method_manual_out').id,
                    'journal_id': from_journal_id.id,
                })
                payment.action_post()
            elif transaction_type=='partner_withdraw':
                
                partner = request.env['res.partner'].search([('ref', '=', partner_account_no)], limit=1) 
                from_journal_id = request.env['account.journal'].search([('api_id', '=',from_cash_account_id)], limit=1)

                if not partner or not from_journal_id:
                    response = {'code': 400, 'message': '', 'error': 'Partner or Cash account not found', 'data': {}}
                    response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
                    response_obj.status_code = 400
                    return response_obj
 
                payment = request.env['account.payment'].create({
                    'partner_id': partner.id,
                    'amount': amount,
                    'payment_type': 'inbound',
                    'payment_method_id': request.env.ref('account.account_payment_method_manual_out').id,
                    'journal_id': from_journal_id.id,
                })
                payment.action_post()

            response = {'code': 200, 'message': 'Transaction Completed Successfully.', 'error': '', 'data': {}}
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 200
            return response_obj

        except Exception as e:
            response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
            response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
            response_obj.status_code = 400
            return response_obj


    # if True:
        # @http.route('/api/transactions/investment', type='http', csrf=False, auth='user', methods=['POST'])
        # def investment_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         cash_account_id = payload.get('cash_account_id')

        #         journal_id = request.env['account.journal'].search([('api_id', '=',cash_account_id)], limit=1).id
        #         capital_account_id = request.env['account.account'].search([('is_for_api','=',True),('account_type', '=', 'liability_current')], limit=1).id
        #         default_account_id = request.env['account.journal'].browse(journal_id).default_account_id.id

        #         if not journal_id or not capital_account_id or not default_account_id:
        #             response = {'code': 400, 'message': '', 'error': 'Journal or accounts not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         move = request.env['account.move'].create({
        #             'journal_id': journal_id,
        #             'line_ids': [
        #                 (0, 0, {
        #                     'account_id': default_account_id,
        #                     'debit': amount,
        #                     'credit': 0,
        #                 }),
        #                 (0, 0, {
        #                     'account_id': capital_account_id,
        #                     'debit': 0,
        #                     'credit': amount,
        #                 }),
        #             ]
        #         })
        #         move.action_post()
        #         response = {'code': 200, 'message': 'Investment transaction completed successfully.', 'error': '', 'data': {'move_id': move.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj

        # @http.route('/api/transactions/withdraw', type='http', csrf=False, auth='user', methods=['POST'])
        # def withdraw_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         cash_account_id = payload.get('cash_account_id')


        #         journal_id = request.env['account.journal'].search([('api_id', '=',cash_account_id)], limit=1).id
        #         drawings_account_id = request.env['account.account'].search([('is_for_api','=',True),('account_type', '=', 'equity')], limit=1).id
        #         cash_account_id = request.env['account.journal'].browse(journal_id).default_account_id.id

        #         if not journal_id or not drawings_account_id or not cash_account_id:
        #             response = {'code': 400, 'message': '', 'error': 'Journal or accounts not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         move = request.env['account.move'].create({
        #             'journal_id': journal_id,
        #             'line_ids': [
        #                 (0, 0, {
        #                     'account_id': drawings_account_id,
        #                     'debit': amount,
        #                     'credit': 0,
        #                 }),
        #                 (0, 0, {
        #                     'account_id': cash_account_id,
        #                     'debit': 0,
        #                     'credit': amount,
        #                 }),
        #             ]
        #         })
        #         move.action_post()
        #         response = {'code': 200, 'message': 'Withdraw transaction completed successfully.', 'error': '', 'data': {'move_id': move.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj

        # @http.route('/api/transactions/transfer_to_cashier', type='http', csrf=False, auth='user', methods=['POST'])
        # def transfer_to_cashier_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         cashier_journal_id = payload.get('cashier_id')
        #         cash_account_id = payload.get('cash_account_id')

        #         main_journal = request.env['account.journal'].search([('api_id', '=',cash_account_id)], limit=1).id

        #         cashier_journal = request.env['account.journal'].search([('id', '=', cashier_journal_id)], limit=1)

        #         if not main_journal.default_account_id or not cashier_journal.default_account_id:
        #             response = {'code': 400, 'message': '', 'error': 'Accounts not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'is_internal_transfer': True,
        #             'amount': amount,
        #             'payment_type': 'outbound',
        #             'journal_id': main_journal.id,
        #             'destination_journal_id': cashier_journal.id,
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
        #         })
        #         payment.action_post()
        #         response = {'code': 200, 'message': 'Transfer to cashier transaction completed successfully.', 'error': '', 'data': {'payment_id': payment.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj

        # @http.route('/api/transactions/transfer_from_cashier', type='http', csrf=False, auth='user', methods=['POST'])
        # def transfer_from_cashier_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         cashier_journal_id = payload.get('cashier_id')
        #         cash_account_id = payload.get('cash_account_id')

        #         main_journal = request.env['account.journal'].search([('api_id', '=',cash_account_id)], limit=1).id
        #         cashier_journal = request.env['account.journal'].search([('id', '=', cashier_journal_id)], limit=1)

        #         if not main_journal.default_account_id or not cashier_journal.default_account_id:
        #             response = {'code': 400, 'message': '', 'error': 'Accounts not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'is_internal_transfer': True,
        #             'amount': amount,
        #             'payment_type': 'outbound',
        #             'journal_id': cashier_journal.id,
        #             'destination_journal_id': main_journal.id,
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
        #         })
        #         payment.action_post()
        #         response = {'code': 200, 'message': 'Transfer from cashier transaction completed successfully.', 'error': '', 'data': {'payment_id': payment.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj


        # @http.route('/api/transactions/transfer_sales_rep', type='http', csrf=False, auth='user', methods=['POST'])
        # def transfer_sales_rep_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         sales_rep_id = payload.get('sales_rep_id')
        #         cashier_journal_id = payload.get('cashier_id')

        #         sales_rep_journal = request.env['account.journal'].search([('id', '=', sales_rep_id)], limit=1)
        #         cashier_journal = request.env['account.journal'].search([('id', '=', cashier_journal_id)], limit=1)

        #         if not cashier_journal or not sales_rep_journal:
        #             response = {'code': 400, 'message': '', 'error': 'Accounts not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         cashier_cash_account_id = cashier_journal.default_account_id.id
        #         sales_rep_cash_account_id = sales_rep_journal.default_account_id.id

        #         move = request.env['account.move'].create({
        #             'journal_id': request.env['account.journal'].search([('type', '=', 'cash')], limit=1).id,
        #             'line_ids': [
        #                 (0, 0, {
        #                     'account_id': cashier_cash_account_id,
        #                     'debit': 0,
        #                     'credit': amount,
        #                 }),
        #                 (0, 0, {
        #                     'account_id': sales_rep_cash_account_id,
        #                     'debit': amount,
        #                     'credit': 0,
        #                 }),
        #             ]
        #         })
        #         move.action_post()
        #         response = {'code': 200, 'message': 'Transfer to sales rep transaction completed successfully.', 'error': '', 'data': {'move_id': move.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj


        # @http.route('/api/transactions/payment_supplier', type='http', csrf=False, auth='user', methods=['POST'])
        # def payment_supplier_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         supplier_id = payload.get('supplier_id')
        #         cash_account_id = payload.get('cash_account_id')

            
        #         supplier = request.env['res.partner'].browse(supplier_id)
        #         if not supplier:
        #             response = {'code': 400, 'message': '', 'error': 'Supplier not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         main_journal = request.env['account.journal'].search([('api_id', '=',cash_account_id)], limit=1).id
        #         if not main_journal:
        #             response = {'code': 400, 'message': '', 'error': 'Main cash journal not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'partner_id': supplier_id,
        #             'amount': amount,
        #             'payment_type': 'outbound',
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_out').id,
        #             'journal_id': main_journal.id,
        #         })
        #         payment.action_post()
        #         response = {'code': 200, 'message': 'Payment to supplier transaction completed successfully.', 'error': '', 'data': {'payment_id': payment.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj


        # @http.route('/api/transactions/withdraw_supplier', type='http', csrf=False, auth='user', methods=['POST'])
        # def withdraw_supplier_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         supplier_id = payload.get('supplier_id')
                
        #         cash_account_id = payload.get('cash_account_id')

            

        #         supplier = request.env['res.partner'].browse(supplier_id)
        #         if not supplier:
        #             response = {'code': 400, 'message': '', 'error': 'Supplier not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         main_journal = request.env['account.journal'].search([('api_id', '=',cash_account_id)], limit=1).id
        #         if not main_journal:
        #             response = {'code': 400, 'message': '', 'error': 'Bank journal not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'partner_id': supplier_id,
        #             'amount': amount,
        #             'payment_type': 'inbound',
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
        #             'journal_id': main_journal.id,
        #         })
        #         payment.action_post()
        #         response = {'code': 200, 'message': 'Withdraw from supplier transaction completed successfully.', 'error': '', 'data': {'payment_id': payment.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj



        # @http.route('/api/transactions/refund_merchant', type='http', csrf=False, auth='user', methods=['POST'])
        # def refund_merchant_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         merchant_id = payload.get('merchant_id')
        #         cashier_journal_id = payload.get('cashier_id')


        #         merchant = request.env['res.partner'].browse(merchant_id)
        #         if not merchant:
        #             response = {'code': 400, 'message': '', 'error': 'Merchant not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         cash_journal = request.env['account.journal'].search([('id', '=', cashier_journal_id)], limit=1)
        #         if not cash_journal:
        #             response = {'code': 400, 'message': '', 'error': 'Cash journal not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'partner_id': merchant_id,
        #             'amount': amount,
        #             'payment_type': 'outbound',
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_out').id,
        #             'journal_id': cash_journal.id,
        #         })
        #         payment.action_post()
        #         response = {'code': 200, 'message': 'Refund to merchant transaction completed successfully.', 'error': '', 'data': {'payment_id': payment.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj



        # @http.route('/api/transactions/reload_merchant', type='http', csrf=False, auth='user', methods=['POST'])
        # def reload_merchant_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         merchant_id = payload.get('merchant_id')
        #         cashier_journal_id = payload.get('cashier_id')

        #         merchant = request.env['res.partner'].browse(merchant_id)
        #         if not merchant:
        #             response = {'code': 400, 'message': '', 'error': 'Merchant not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         cash_journal = request.env['account.journal'].search([('id', '=', cashier_journal_id)], limit=1)
        #         if not cash_journal:
        #             response = {'code': 400, 'message': '', 'error': 'Cash journal not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'partner_id': merchant_id,
        #             'amount': amount,
        #             'payment_type': 'inbound',
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
        #             'journal_id': cash_journal.id,
        #         })
        #         payment.action_post()
        #         response = {'code': 200, 'message': 'Reload to merchant transaction completed successfully.', 'error': '', 'data': {'payment_id': payment.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj
        
        # @http.route('/api/transactions/sales_rep_to_cashier', type='http', csrf=False, auth='user', methods=['POST'])
        # def transfer_sales_rep_to_cashier(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         sales_rep_journal_id = payload.get('sales_rep_id')
        #         cashier_journal_id = payload.get('cashier_id')

        #         sales_rep_journal = request.env['account.journal'].browse(sales_rep_journal_id)
        #         cashier_journal = request.env['account.journal'].browse(cashier_journal_id)

        #         if not sales_rep_journal or not cashier_journal:
        #             response = {'code': 400, 'message': '', 'error': 'Journals not found', 'data': {}}
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'is_internal_transfer': True,
        #             'amount': amount,
        #             'payment_type': 'outbound',
        #             'journal_id': sales_rep_journal.id,
        #             'destination_journal_id': cashier_journal.id,
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
        #         })
        #         payment.action_post()

        #         response = {'code': 200, 'message': 'Transfer from sales rep to cashier completed successfully.', 'error': '', 'data': {'payment_id': payment.id}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {'code': 400, 'message': '', 'error': str(e), 'data': {}}
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj


        # @http.route('/api/transactions/reload_sales_rep', type='http', csrf=False, auth='user', methods=['POST'])
        # def reload_sales_rep_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         sales_rep_journal_id = payload.get('sales_rep_journal_id')
        #         merchant_id = payload.get('merchant_id')

        #         merchant = request.env['res.partner'].browse(merchant_id)
        #         sales_rep_journal = request.env['account.journal'].browse(sales_rep_journal_id)

        #         if not merchant or not sales_rep_journal:
        #             response = {
        #                 'code': 400,
        #                 'message': '',
        #                 'error': 'Sales representative or merchant not found',
        #                 'data': {}
        #             }
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         payment = request.env['account.payment'].create({
        #             'is_internal_transfer': True,
        #             'amount': amount,
        #             'payment_type': 'outbound',
        #             'journal_id': sales_rep_journal.id,
        #             'destination_journal_id': merchant.id,
        #             'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
        #        })
        #         payment.action_post()

        #         response = {
        #             'code': 200,
        #             'message': 'Reload for sales representative completed successfully.',
        #             'error': '',
        #             'data': {'payment_id': payment.id}
        #         }
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {
        #             'code': 400,
        #             'message': '',
        #             'error': str(e),
        #             'data': {}
        #         }
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj


        # @http.route('/api/transactions/withdraw_emoney_cashier', type='http', csrf=False, auth='user', methods=['POST'])
        # def withdraw_emoney_cashier_transaction(self, **kwargs):
        #     try:
        #         payload = json.loads(request.httprequest.data.decode('utf-8'))
        #         amount = payload.get('amount')
        #         cashier_journal_id = payload.get('cashier_id')

        #         e_money_account_id = request.env['account.account'].search([('is_for_api', '=', True), ('code', '=', 'E_MONEY')], limit=1).id
        #         cashier_journal = request.env['account.journal'].browse(cashier_journal_id)

        #         if not e_money_account_id or not cashier_journal:
        #             response = {
        #                 'code': 400,
        #                 'message': '',
        #                 'error': 'Accounts not found',
        #                 'data': {}
        #             }
        #             response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #             response_obj.status_code = 400
        #             return response_obj

        #         move = request.env['account.move'].create({
        #             'journal_id': cashier_journal.id,
        #             'line_ids': [
        #                 (0, 0, {
        #                     'account_id': e_money_account_id,
        #                     'debit': 0,
        #                     'credit': amount,
        #                 }),
        #                 (0, 0, {
        #                     'account_id': cashier_journal.default_account_id.id,
        #                     'debit': amount,
        #                     'credit': 0,
        #                 }),
        #             ]
        #         })
        #         move.action_post()

        #         response = {
        #             'code': 200,
        #             'message': 'Withdrawal from e-money to cashier completed successfully.',
        #             'error': '',
        #             'data': {'move_id': move.id}
        #         }
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 200
        #         return response_obj

        #     except Exception as e:
        #         response = {
        #             'code': 400,
        #             'message': '',
        #             'error': str(e),
        #             'data': {}
        #         }
        #         response_obj = request.make_response(json.dumps(response), headers={'Content-Type': 'application/json'})
        #         response_obj.status_code = 400
        #         return response_obj
    
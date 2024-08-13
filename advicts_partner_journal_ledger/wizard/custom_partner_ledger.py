from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime
from markupsafe import Markup


class customPartnerLedger(models.TransientModel):
    _name = "custom.partner.ledger"
    _description = "custom Partner Ledger"

    date_from = fields.Date('Date From', required=True, default=datetime(datetime.now().year, 1, 1))
    date_to = fields.Date('Date To', required=True, default=fields.Date.today())
    partner_ids = fields.Many2many('res.partner', string='Partners', required=True)
    custom_currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    show_detials = fields.Boolean( string='Show Detials' )
    show_ConsoladetedEntries = fields.Boolean( string='Show Consolidated Entries' )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('Date From must be before Date To'))


    def print_report_action(self):
        selected_currency_id = self.custom_currency_id.id
        company_id=self.env.user.company_id
        company_currency = self.env.company.currency_id

        currency_ids = self.env['res.currency'].search([('id', '=', selected_currency_id)])
        currency_map = {}
        partners_data = []
        move_lines_for_balance=[]
        all_move_lines=[]
        for currency_id in currency_ids:
            for partner_id in self.partner_ids:
                currency_map[f"{partner_id.id}-{selected_currency_id}"] = {
                    'key': f'balance-{currency_id.id}',
                    'currency_id': currency_id, 
                    "current_balance": 0,
                    "init_balance": self.format_value(0, currency_id)
                }
                move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner_id.id), 
                ('move_id.state', '=', 'posted'), 
                ('journal_id.type', 'in', ['cash','sale','bank','purchase']),
                ('account_id.user_type_id', 'in', [9, 1]),
                # ('account_id.non_trade', '=', False),
                ], order="date,id")

                all_move_lines += move_lines
                if self.show_detials:
                    move_lines_for_balance = move_lines.filtered(lambda aml: aml.date < self.date_from)
                else:
                    move_lines_for_balance = move_lines


                init_balance=0

                for aml in move_lines_for_balance:
                    converted_debit = company_currency._convert(aml.debit, currency_id, company_id, aml.date)
                    converted_credit = company_currency._convert(aml.credit, currency_id, company_id, aml.date)  
                    init_balance += converted_debit - converted_credit

                currency_map[f"{partner_id.id}-{currency_id.id}"]['current_balance'] = init_balance
                currency_map[f"{partner_id.id}-{currency_id.id}"]['init_balance'] = self.format_value(init_balance, currency_id)
                
        
        for partner_id in self.partner_ids:
            partner_data = {
                    'id': str(partner_id.id),
                    'name': partner_id.name,
                    'moves': [],
            }
            if self.show_detials:
                if self.show_ConsoladetedEntries:
                    moves = self.env['account.move'].search([
                        ('partner_id', '=', partner_id.id),
                        ('date', '>=', self.date_from),
                        ('date', '<=', self.date_to),
                        ('state', '=', 'posted'),
                        ('journal_id.type', 'in', ['cash', 'sale', 'bank', 'purchase']),
                    ], order="date,id")
                    # move_lines = move_lines.filtered(lambda aml: aml.date >= self.date_from and aml.date <=self.date_to and aml.partner_id==partner_id)
                    for move in moves:
                        # try:
                            total_debit = sum(move.line_ids.filtered(lambda line: line.debit and line.account_id.user_type_id in [1,9]).mapped('debit'))
                            total_credit = sum(move.line_ids.filtered(lambda line: line.credit and line.account_id.user_type_id in [1,9]).mapped('credit'))
                            total_amount_currency = sum(move.line_ids.filtered(lambda line: line.account_id.user_type_id in [1,9]).mapped('amount_currency'))
                            first_line = next((line for line in move.line_ids if line.account_id.user_type_id in [1,9]), False)

                            converted_debit = company_currency._convert(total_debit, currency_id, company_id, move.date)
                            converted_credit = company_currency._convert(total_credit, currency_id, company_id, move.date) 

                            currency_map[f"{partner_id.id}-{selected_currency_id}"]['current_balance'] += (converted_debit-converted_credit)
                            invoice_id = move.id
                            

                            move_data = {
                                'ref': str(move.name),
                                'date': move.date,
                                'debit': self.format_value(converted_debit, currency_id),
                                'credit': self.format_value(converted_credit, currency_id),
                                'amount_currency': self.format_value(total_amount_currency, first_line.currency_id) if first_line else self.format_value(0, currency_id)
                            }
                            for currency_id in currency_ids:
                                move_data[currency_map[f"{partner_id.id}-{currency_id.id}"]['key']] = self.format_value(currency_map[f"{partner_id.id}-{currency_id.id}"]["current_balance"], currency_id)
                            partner_data['moves'].append(move_data)
                else: 

                    move_lines = self.env['account.move.line'].search([
                        ('partner_id', '=', partner_id.id), 
                        ('date', '>=', self.date_from), 
                        ('date', '<=', self.date_to), 
                        ('move_id.state', '=', 'posted'), 
                        ('journal_id.type', 'in', ['cash','sale','bank','purchase']),
                        ('account_id.user_type_id', 'in', [9, 1]), 
                        # ('account_id.non_trade', '=', False),
                    ], order="date,id")
                    # move_lines = move_lines.filtered(lambda aml: aml.date >= self.date_from and aml.date <=self.date_to and aml.partner_id==partner_id)
                    for aml in move_lines:
                        # try:
                            converted_debit = company_currency._convert(aml.debit, currency_id, company_id, aml.date)
                            converted_credit = company_currency._convert(aml.credit, currency_id, company_id, aml.date) 

                            currency_map[f"{partner_id.id}-{selected_currency_id}"]['current_balance'] += (converted_debit-converted_credit)
                            invoice_id = aml.move_id
                            

                            move_data = {
                                'ref':str(aml.move_name)+'  -  '+ str(aml.ref),
                                'date': aml.date,
                                'debit': self.format_value(converted_debit, currency_id),
                                'credit': self.format_value(converted_credit, currency_id),
                                'amount_currency': self.format_value(aml.amount_currency, aml.currency_id)
                            }
                            for currency_id in currency_ids:
                                move_data[currency_map[f"{partner_id.id}-{currency_id.id}"]['key']] = self.format_value(currency_map[f"{partner_id.id}-{currency_id.id}"]["current_balance"], currency_id)
                            partner_data['moves'].append(move_data)

            partners_data.append(partner_data)

        for partner_id in self.partner_ids:
            for currency_id in currency_ids:
                current_currency_balance = currency_map[f"{partner_id.id}-{currency_id.id}"]['current_balance']

        report_data = {
            'date_to': self.date_to,
            'date_from': self.date_from,
            'currency_map': currency_map,
            'active_currency_ids': currency_ids.mapped(lambda currency_id: {'name': currency_id.name, 'key': f"balance-{currency_id.id}", 'id': str(currency_id.id), 'symbol': currency_id.symbol}),
            'data': partners_data,
        }
        return self.env.ref('advicts_partner_journal_ledger.custom_partner_ledger_report_action').report_action(self, data=report_data) 


    def format_value(self, value, currency_id, figure_type='monetary', blank_if_zero=False):
        report = self.env['account.report']
        return {
            'value': report.format_value(value, currency_id,  blank_if_zero=blank_if_zero),
            'style': 'color: red;' if value < 0 else '',
        }
    




              
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from datetime import datetime
from markupsafe import Markup


class customjournalLedger(models.TransientModel):
    _name = "custom.journal.ledger"
    _description = "custom journal Ledger"

    date_from = fields.Date('Date From', required=True, default=datetime(datetime.now().year, 1, 1))
    date_to = fields.Date('Date To', required=True, default=fields.Date.today())
    journal_ids = fields.Many2many('account.journal', string='journals', required=True)
    custom_currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

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
        journals_data = []
        all_move_lines=[]
        for currency_id in currency_ids:
            for journal_id in self.journal_ids:
                currency_map[f"{journal_id.id}-{selected_currency_id}"] = {
                    'key': f'balance-{currency_id.id}',
                    'currency_id': currency_id, 
                    "current_balance": 0,
                    "init_balance": self.format_value(0, currency_id)
                }
                move_lines = self.env['account.move.line'].search([
                ('journal_id', '=', journal_id.id), 
                ('move_id.state', '=', 'posted'), 
                ('account_id.account_type', 'in', ['asset_cash']), 
                # ('account_id.non_trade', '=', False),
                ], order="date,id")

                all_move_lines += move_lines

                move_lines_for_balance = move_lines.filtered(lambda aml: aml.date < self.date_from)

                init_balance=0

                for aml in move_lines_for_balance:
                    converted_debit = company_currency._convert(aml.debit, currency_id, company_id, aml.date)
                    converted_credit = company_currency._convert(aml.credit, currency_id, company_id, aml.date)  
                    init_balance += converted_debit - converted_credit

                currency_map[f"{journal_id.id}-{currency_id.id}"]['current_balance'] = init_balance
                currency_map[f"{journal_id.id}-{currency_id.id}"]['init_balance'] = self.format_value(init_balance, currency_id)
                

        for journal_id in self.journal_ids:
            journal_data = {
                'id': str(journal_id.id),
                'name': journal_id.name,
                'moves': [],
            }
            move_lines = self.env['account.move.line'].search([
                ('journal_id', '=', journal_id.id), 
                ('date', '>=', self.date_from), 
                ('date', '<=', self.date_to), 
                ('move_id.state', '=', 'posted'), 
                ('account_id.account_type', 'in', ['asset_cash']), 
                # ('account_id.non_trade', '=', False),
            ], order="date,id")
            # move_lines = move_lines.filtered(lambda aml: aml.date >= self.date_from and aml.date <=self.date_to and aml.journal_id==journal_id)
            for aml in move_lines:
                # try:
                    converted_debit = company_currency._convert(aml.debit, currency_id, company_id, aml.date)
                    converted_credit = company_currency._convert(aml.credit, currency_id, company_id, aml.date) 

                    currency_map[f"{journal_id.id}-{selected_currency_id}"]['current_balance'] += (converted_debit-converted_credit)
                    invoice_id = aml.move_id
                    

                    move_data = {
                        'ref': aml.ref,
                        'destination_journal':aml.payment_id.destination_journal_id.name,
                        'partner':aml.partner_id.name,
                        'date': aml.date,
                        'debit': self.format_value(converted_debit, currency_id),
                        'credit': self.format_value(converted_credit, currency_id),
                        'amount_currency': self.format_value(aml.amount_currency, aml.currency_id)
                    }
                    for currency_id in currency_ids:
                        move_data[currency_map[f"{journal_id.id}-{currency_id.id}"]['key']] = self.format_value(currency_map[f"{journal_id.id}-{currency_id.id}"]["current_balance"], currency_id)
                    journal_data['moves'].append(move_data)
                # except:
                    # pass
            journals_data.append(journal_data)

        for journal_id in self.journal_ids:
            for currency_id in currency_ids:
                current_currency_balance = currency_map[f"{journal_id.id}-{currency_id.id}"]['current_balance']

        report_data = {
            'date_to': self.date_to,
            'date_from': self.date_from,
            'currency_map': currency_map,
            'active_currency_ids': currency_ids.mapped(lambda currency_id: {'name': currency_id.name, 'key': f"balance-{currency_id.id}", 'id': str(currency_id.id), 'symbol': currency_id.symbol}),
            'data': journals_data,
        }
        return self.env.ref('advicts_partner_journal_ledger.custom_journal_ledger_report_action').report_action(self, data=report_data) 


    def format_value(self, value, currency_id, figure_type='monetary', blank_if_zero=False):
        report = self.env['account.report']
        return {
            'value': report.format_value(value, currency_id, figure_type=figure_type, blank_if_zero=blank_if_zero),
            'style': 'color: red;' if value < 0 else '',
        }
    




              
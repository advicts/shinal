# -*- coding: utf-8 -*-
import base64

from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def format_currency_amount(self, amount, currency_id):
        pre = currency_id.position == 'before'
        symbol = u'{symbol}'.format(symbol=currency_id.symbol or '')
        return u'{pre}{0}{post}'.format(amount, pre=symbol + " " if pre else '', post=" " + symbol if not pre else '')

    def send_whatsapp_msg(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        append_signature = ICPSudo.get_param('whatsapp_integration_account.ac_append_signature')
        chatter_log = ICPSudo.get_param('whatsapp_integration_account.ac_chatter_log')
        attachment = ICPSudo.get_param('whatsapp_integration_account.ac_attachment')
        message_type = ICPSudo.get_param('whatsapp_integration_account.ac_message_type')
        invoice_line_str = None
        attachment_ids = None
        message_in = None
        partner_id = self.partner_id
        invoice_ref = self.name
        company = self.company_id.name
        amount = self.amount_total
        due_amount = self.amount_residual
        currency_id = self.currency_id
        invoice_date = self.invoice_date
        invoice_date = invoice_date.strftime('%d %b %Y')
        amount_total = self.format_currency_amount(amount=amount, currency_id=currency_id)
        due_amount = self.format_currency_amount(amount=due_amount, currency_id=currency_id)

        if message_type == 'detail':
            message = 'Dear, ' + partner_id.name + '\n\nHere is your invoice *' + str(invoice_ref) + '* from ' + str(
                company) + ' on *' + invoice_date + '* , Please remit payment at your earliest convenience.'
            message_in = '<i class="fa fa-whatsapp text-success" aria-hidden="true"> <em>WhatsApp Message</em></i><br/>'
            message_in += 'Dear, ' + partner_id.name + '<br/><br/>Here is your invoice <b>' + str(
                invoice_ref) + '</b> from ' + str(
                company) + ' on ' + invoice_date + ', Please remit payment at your earliest convenience.'
            invoice_line_str = message
            for invoice_line_item in self.invoice_line_ids:
                product = invoice_line_item.product_id.name_get()[0][1]
                quantity = invoice_line_item.quantity
                uom = invoice_line_item.product_uom_id.name
                price = invoice_line_item.price_unit
                currency_id = invoice_line_item.currency_id
                price_unit = self.format_currency_amount(amount=price, currency_id=currency_id)
                discount = invoice_line_item.discount

                invoice_line_str += '\n\n*' + product + '* \n*Qty:* ' + str(quantity) + " " + uom
                message_in += '<br/><br/><b>' + product + '</b><br/><b>Qty:</b> ' + str(quantity) + " " + uom

                if discount > 0.0:
                    invoice_line_str += '\n*Discount:* ' + str(discount) + '%'
                    message_in += '<br/><b>Discount:</b> ' + str(discount) + '%'
                invoice_line_str += '\n*Price:* ' + str(price_unit) + '\n___________'
                message_in += '<br/><b>Price:</b> ' + str(price_unit) + '<br/>___________'

            invoice_line_str += '\n*Total Amount:* ' + str(amount_total)
            invoice_line_str += '\n*Amount Due:* ' + str(due_amount)
            invoice_line_str += '\n*Payment Terms:* ' + str(
                self.invoice_payment_term_id.name if self.invoice_payment_term_id else '-')
            invoice_line_str += '\n*Invoice Date:* ' + str(invoice_date if invoice_date else '-')
            message_in += '<br/><b>Total Amount:</b> ' + str(amount_total)
            message_in += '<br/><b>Amount Due:</b> ' + str(due_amount)
            message_in += '<br/><b>Payment Terms:</b> ' + str(
                self.invoice_payment_term_id.name if self.invoice_payment_term_id else '-')
            message_in += '<br/><b>Invoice Date:</b> ' + str(invoice_date if invoice_date else '-')

        if message_type == 'short':
            include_product_details = ICPSudo.get_param('whatsapp_integration_account.ac_include_product_details')
            include_payment_terms = ICPSudo.get_param('whatsapp_integration_account.ac_include_payment_terms')
            include_total_details = ICPSudo.get_param('whatsapp_integration_account.ac_include_total_details')
            include_invoice_date = ICPSudo.get_param('whatsapp_integration_account.ac_include_invoice_date')

            message = 'Dear, ' + partner_id.name + '\n\nHere is your invoice *' + str(invoice_ref) + '* from ' + str(
                company) + ' on *' + invoice_date + '* , Please remit payment at your earliest convenience.'
            message_in = '<i class="fa fa-whatsapp text-success" aria-hidden="true"> <em>WhatsApp Message</em></i><br/>'
            message_in += 'Dear, ' + partner_id.name + '<br/><br/>Here is your invoice <b>' + str(
                invoice_ref) + '</b> from ' + str(
                company) + ' on ' + invoice_date + ' , Please remit payment at your earliest convenience.'

            invoice_line_str = message

            if include_product_details:
                for invoice_line_item in self.invoice_line_ids:
                    product = invoice_line_item.product_id.name_get()[0][1]
                    quantity = invoice_line_item.quantity
                    uom = invoice_line_item.product_uom_id.name
                    price = invoice_line_item.price_unit
                    currency_id = invoice_line_item.currency_id
                    price_unit = self.format_currency_amount(amount=price, currency_id=currency_id)
                    discount = invoice_line_item.discount

                    invoice_line_str += '\n\n*' + product + '* \n*Qty:* ' + str(quantity) + " " + uom
                    message_in += '<br/><br/><b>' + product + '</b><br/><b>Qty:</b> ' + str(quantity) + " " + uom

                    if discount > 0.0:
                        invoice_line_str += '\n*Discount:* ' + str(discount) + '%'
                        message_in += '<br/><b>Discount:</b> ' + str(discount) + '%'
                    invoice_line_str += '\n*Price:* ' + str(price_unit) + '\n___________'
                    message_in += '<br/><b>Price:</b> ' + str(price_unit) + '<br/>___________'

            if include_total_details:
                invoice_line_str += '\n*Total Amount:* ' + str(amount_total)
                invoice_line_str += '\n*Amount Due:* ' + str(due_amount)
                message_in += '<br/><b>Total Amount:</b> ' + str(amount_total)
                message_in += '<br/><b>Amount Due:</b> ' + str(due_amount)

            if include_payment_terms:
                invoice_line_str += '\n*Payment Terms:* ' + str(
                    self.invoice_payment_term_id.name if self.invoice_payment_term_id else '-')
                message_in += '<br/><b>Payment Terms:</b> ' + str(
                    self.invoice_payment_term_id.name if self.invoice_payment_term_id else '-')

            if include_invoice_date:
                invoice_line_str += '\n*Invoice Date:* ' + str(invoice_date if invoice_date else '-')
                message_in += '<br/><b>Invoice Date:</b> ' + str(invoice_date if invoice_date else '-')

        if append_signature:
            invoice_line_str += '\n\n' + self.env.user.whatsapp_signature if self.env.user.whatsapp_signature else ""
        if attachment:
            report_template = self.env['ir.actions.report'].sudo().search(
                [('model', '=', 'account.move'), ('report_type', '=', 'qweb-pdf'),
                 ('report_name', '=', 'account.report_invoice_with_payments')], limit=1)
            report_name = self.name
            report = report_template

            report_service = report.report_name

            if report.report_type in ['qweb-html', 'qweb-pdf']:
                result, format = report._render_qweb_pdf([self.id])
            else:
                res = report._render([self.id])
                if not res:
                    raise UserError(_('Unsupported report type %s found.', report.report_type))
                result, format = res

            result = base64.b64encode(result)
            if not report_name:
                report_name = 'report.' + report_service
            ext = "." + format
            if not report_name.endswith(ext):
                report_name += ext
            attach_fname, attach_datas = (report_name, result)
            attachment_ids = []
            Attachment = self.env['ir.attachment']
            data_attach = {
                'name': attach_fname,
                'datas': attach_datas,
                'res_model': 'mail.compose.message',
                'res_id': 0,
                'type': 'binary',
            }
            attachment_ids.append(Attachment.create(data_attach).id)

        res = self.env['message.popup.wizard'].create({
            'recipient_ids': self.partner_id.ids,
            'single_recipient_number': self.partner_id.mobile,
            'message': invoice_line_str,
            'attachment_ids': [(6, 0, attachment_ids)] if attachment_ids else [],
            'model_name': 'account.move',
            'chatter_message': message_in,
            'chatter_res_id': self.id,
            'message_chatter_log': True if chatter_log else False
        }).id

        return {
            'name': 'Compose a Message and Send',
            'view_mode': 'form',
            'res_model': 'message.popup.wizard',
            'type': 'ir.actions.act_window',
            'res_id': res,
            'target': 'new',
        }


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def format_currency_amount(self, amount, currency_id):
        pre = currency_id.position == 'before'
        symbol = u'{symbol}'.format(symbol=currency_id.symbol or '')
        return u'{pre}{0}{post}'.format(amount, pre=symbol + " " if pre else '', post=" " + symbol if not pre else '')

    def send_whatsapp_msg(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        append_signature = ICPSudo.get_param('whatsapp_integration_account.ac_append_signature')
        chatter_log = ICPSudo.get_param('whatsapp_integration_account.ac_chatter_log')
        attachment = ICPSudo.get_param('whatsapp_integration_account.ac_attachment')
        attachment_ids = None
        partner_id = self.partner_id
        company = self.company_id.name
        payment_ref = self.name
        amount = self.amount
        currency_id = self.currency_id
        amount = self.format_currency_amount(amount=amount, currency_id=currency_id)

        message = 'Dear, ' + partner_id.name + '\n\nThank you for your payment. Here is your payment receipt *' + str(
            payment_ref) + '* amounting to *' + str(amount) + '* from ' + str(company) + '.'

        message_in = '<i class="fa fa-whatsapp text-success" aria-hidden="true"> <em>WhatsApp Message</em></i><br/>'
        message_in += 'Dear, ' + partner_id.name + '<br/><br/>Thank you for your payment. Here is your payment ' \
                                                   'receipt <b>' + str(payment_ref) + '</b> amounting to <b>' + str(
            amount) + '</b> from ' + str(company) + '.'

        if append_signature:
            message += '\n\n' + self.env.user.whatsapp_signature if self.env.user.whatsapp_signature else ""
        if attachment:
            report_template = self.env['ir.actions.report'].sudo().search(
                [('model', '=', 'account.payment'), ('report_type', '=', 'qweb-pdf'),
                 ('report_name', '=', 'account.report_payment_receipt')], limit=1)
            report_name = self.name
            report = report_template

            report_service = report.report_name

            if report.report_type in ['qweb-html', 'qweb-pdf']:
                result, format = report._render_qweb_pdf([self.id])
            else:
                res = report._render([self.id])
                if not res:
                    raise UserError(_('Unsupported report type %s found.', report.report_type))
                result, format = res

            result = base64.b64encode(result)
            if not report_name:
                report_name = 'report.' + report_service
            ext = "." + format
            if not report_name.endswith(ext):
                report_name += ext
            attach_fname, attach_datas = (report_name, result)
            attachment_ids = []
            Attachment = self.env['ir.attachment']
            data_attach = {
                'name': attach_fname,
                'datas': attach_datas,
                'res_model': 'mail.compose.message',
                'res_id': 0,
                'type': 'binary',
            }
            attachment_ids.append(Attachment.create(data_attach).id)

        res = self.env['message.popup.wizard'].create({
            'recipient_ids': self.partner_id.ids,
            'single_recipient_number': self.partner_id.mobile,
            'message': message,
            'attachment_ids': [(6, 0, attachment_ids)] if attachment_ids else [],
            'model_name': 'account.payment',
            'chatter_message': message_in,
            'chatter_res_id': self.id,
            'message_chatter_log': True if chatter_log else False
        }).id

        return {
            'name': 'Compose a Message and Send',
            'view_mode': 'form',
            'res_model': 'message.popup.wizard',
            'type': 'ir.actions.act_window',
            'res_id': res,
            'target': 'new',
        }

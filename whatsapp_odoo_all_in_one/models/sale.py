# -*- coding: utf-8 -*-
import base64

from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def format_currency_amount(self, amount, currency_id):
        pre = currency_id.position == 'before'
        symbol = u'{symbol}'.format(symbol=currency_id.symbol or '')
        return u'{pre}{0}{post}'.format(amount, pre=symbol + " " if pre else '', post=" " + symbol if not pre else '')

    def send_whatsapp_msg(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        append_signature = ICPSudo.get_param('whatsapp_integration_sale.append_signature')
        chatter_log = ICPSudo.get_param('whatsapp_integration_sale.chatter_log')
        attachment = ICPSudo.get_param('whatsapp_integration_sale.attachment')
        message_type = ICPSudo.get_param('whatsapp_integration_sale.message_type')
        order_line_str = None
        attachment_ids = None
        message_in = None
        partner_id = self.partner_id
        order_ref = self.name
        company = self.company_id.name
        amount = self.amount_total
        currency_id = self.currency_id
        date_order = self.date_order.date()
        order_date = date_order.strftime('%d %b %Y')
        amount_total = self.format_currency_amount(amount=amount, currency_id=currency_id)

        if message_type == 'detail':
            message = 'Dear, ' + partner_id.name + '\n\nHere is the order *' + str(
                order_ref) + '* amounting in ' + '*' + str(amount_total) + '* from ' + str(
                company) + ' on *' + order_date + '* , following is your order details.'
            message_in = '<i class="fa fa-whatsapp text-success" aria-hidden="true"> <em>WhatsApp Message</em></i><br/>'
            message_in += 'Dear, ' + partner_id.name + '<br/><br/>Here is the order <b>' + str(
                order_ref) + '</b> amounting in <b>' + str(amount_total) + '</b> from ' + str(
                company) + ' on ' + order_date + ', following is your order details.'
            order_line_str = message
            for order_line_item in self.order_line:
                product = order_line_item.product_id.name_get()[0][1]
                quantity = order_line_item.product_uom_qty
                price = order_line_item.price_unit
                currency_id = order_line_item.currency_id
                price_unit = self.format_currency_amount(amount=price, currency_id=currency_id)

                discount = order_line_item.discount
                order_line_str += '\n\n*' + product + '* \n*Qty:* ' + str(quantity)
                message_in += '<br/><br/><b>' + product + '</b><br/><b>Qty:</b> ' + str(quantity)

                if discount > 0.0:
                    order_line_str += '\n*Discount:* ' + str(discount) + '%'
                    message_in += '<br/><b>Discount:</b> ' + str(discount) + '%'
                order_line_str += '\n*Price:* ' + str(price_unit) + '\n___________'
                message_in += '<br/><b>Price:</b> ' + str(price_unit) + '<br/>___________'

            order_line_str += '\n*Total Amount:* ' + str(amount_total)
            order_line_str += '\n*Payment Terms:* ' + str(self.payment_term_id.name if self.payment_term_id else '-')
            message_in += '<br/><b>Total Amount:</b> ' + str(amount_total)
            message_in += '<br/><b>Payment Terms:</b> ' + str(
                self.payment_term_id.name if self.payment_term_id else '-')

        if message_type == 'short':
            include_product_details = ICPSudo.get_param('whatsapp_integration_sale.include_product_details')
            include_payment_terms = ICPSudo.get_param('whatsapp_integration_sale.include_payment_terms')
            include_total_details = ICPSudo.get_param('whatsapp_integration_sale.include_total_details')

            message = 'Dear, ' + partner_id.name + '\n\nHere is the order *' + str(
                order_ref) + '* amounting in ' + '*' + str(amount_total) + '* from ' + str(
                company) + ' on *' + order_date + '* is ready for review.'
            message_in = '<i class="fa fa-whatsapp text-success" aria-hidden="true"> <em>WhatsApp Message</em></i><br/>'
            message_in += 'Dear, ' + partner_id.name + '<br/><br/>Here is the order <b>' + str(
                order_ref) + '</b> amounting in <b>' + str(amount_total) + '</b> from ' + str(
                company) + ' on ' + order_date + ' is ready for review.'

            order_line_str = message

            if include_product_details:
                for order_line_item in self.order_line:
                    product = order_line_item.product_id.name_get()[0][1]
                    quantity = order_line_item.product_uom_qty
                    price = order_line_item.price_unit
                    currency_id = order_line_item.currency_id
                    price_unit = self.format_currency_amount(amount=price, currency_id=currency_id)

                    discount = order_line_item.discount
                    order_line_str += '\n\n*' + product + '* \n*Qty:* ' + str(quantity)
                    message_in += '<br/><br/><b>' + product + '</b><br/><b>Qty:</b> ' + str(quantity)

                    if discount > 0.0:
                        order_line_str += '\n*Discount:* ' + str(discount) + '%'
                        message_in += '<br/><b>Discount:</b> ' + str(discount) + '%'
                    order_line_str += '\n*Price:* ' + str(price_unit) + '\n___________'
                    message_in += '<br/><b>Price:</b> ' + str(price_unit) + '<br/>___________'

            if include_total_details:
                order_line_str += '\n*Total Amount:* ' + str(amount_total)
                message_in += '<br/><b>Total Amount:</b> ' + str(amount_total)

            if include_payment_terms:
                order_line_str += '\n*Payment Terms:* ' + str(self.payment_term_id.name)
                message_in += '<br/><b>Payment Terms:</b> ' + str(self.payment_term_id.name)

        if append_signature:
            order_line_str += '\n\n' + self.env.user.whatsapp_signature if self.env.user.whatsapp_signature else ""
        if attachment:
            report_template = self.env['ir.actions.report'].sudo().search(
                [('model', '=', 'sale.order'), ('report_type', '=', 'qweb-pdf'),
                 ('report_name', '=', 'sale.report_saleorder')], limit=1)
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
            'message': order_line_str,
            'attachment_ids': [(6, 0, attachment_ids)] if attachment_ids else [],
            'model_name': 'sale.order',
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

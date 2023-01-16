# -*- coding: utf-8 -*-
import base64

import pytz

from odoo import models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def send_whatsapp_msg(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        append_signature = ICPSudo.get_param('whatsapp_integration_stock.st_append_signature')
        chatter_log = ICPSudo.get_param('whatsapp_integration_stock.st_chatter_log')
        attachment = ICPSudo.get_param('whatsapp_integration_stock.st_attachment')
        message_type = ICPSudo.get_param('whatsapp_integration_stock.st_message_type')

        order_line_str = None
        attachment_ids = None
        message_in = None
        partner_id = self.partner_id
        order_ref = self.name
        company = self.company_id.name
        schedule_date = False
        date_done = False
        user_time_zone = pytz.timezone(self.env.user.partner_id.tz)
        if self.scheduled_date:
            user_time = pytz.utc.localize(self.scheduled_date, is_dst=False)
            schedule_date = user_time.astimezone(user_time_zone)
        if self.date_done:
            user_time = pytz.utc.localize(self.date_done, is_dst=False)
            date_done = user_time.astimezone(user_time_zone)

        if message_type == 'detail':
            message = 'Dear, ' + partner_id.name + '\n\nHere is the delivery order *' + str(
                order_ref) + '* from ' + str(company) + ' , following is your delivery order details.'
            message_in = '<i class="fa fa-whatsapp text-success" aria-hidden="true"> <em>WhatsApp Message</em></i><br/>'

            message_in += 'Dear, ' + partner_id.name + '<br/><br/>Here is the delivery order <b>' + str(
                order_ref) + '</b> from ' + str(company) + ', following is your delivery order details.'
            order_line_str = message

            for moves in self.move_ids_without_package:
                product = moves.product_id.name_get()[0][1]
                quantity = moves.product_uom_qty
                uom = moves.product_uom.name

                order_line_str += '\n\n*' + product + '* \n*Qty:* ' + str(quantity) + " " + uom + '\n___________'
                message_in += '<br/><br/><b>' + product + '</b><br/><b>Qty:</b> ' + str(
                    quantity) + " " + uom + '<br/>___________'

            order_line_str += '\n*Scheduled Date:* ' + str(schedule_date or '-')
            order_line_str += '\n*Effective Date:* ' + str(date_done or '-')
            order_line_str += '\n*Shipping Policy:* ' + str(
                dict(self._fields['move_type'].selection).get(self.move_type) if self.move_type else '-')
            message_in += '<br/><b>Scheduled Date:</b> ' + str(schedule_date or '-')
            message_in += '<br/><b>Effective Date:</b> ' + str(date_done or '-')
            message_in += '<br/><b>Shipping Policy:</b> ' + str(
                dict(self._fields['move_type'].selection).get(self.move_type) if self.move_type else '-')

        if message_type == 'short':
            include_product_details = ICPSudo.get_param('whatsapp_integration_stock.st_include_product_details')
            include_shipping_policy = ICPSudo.get_param('whatsapp_integration_stock.st_include_shipping_policy')
            include_scheduled_date = ICPSudo.get_param('whatsapp_integration_stock.st_include_scheduled_date')
            include_date_done = ICPSudo.get_param('whatsapp_integration_stock.st_include_date_done')

            message = 'Dear, ' + partner_id.name + '\n\nHere is the delivery order *' + str(
                order_ref) + '* from ' + str(company) + ' , following is your delivery order details.'
            message_in = '<i class="fa fa-whatsapp text-success" aria-hidden="true"> <em>WhatsApp Message</em></i><br/>'
            message_in += 'Dear, ' + partner_id.name + '<br/><br/>Here is the delivery order <b>' + str(
                order_ref) + '</b> from ' + str(company) + ', following is your delivery order details.'
            order_line_str = message

            if include_product_details:
                for moves in self.move_ids_without_package:
                    product = moves.product_id.name_get()[0][1]
                    quantity = moves.product_uom_qty
                    uom = moves.product_uom.name

                    order_line_str += '\n\n*' + product + '* \n*Qty:* ' + str(quantity) + " " + uom + '\n___________'
                    message_in += '<br/><br/><b>' + product + '</b><br/><b>Qty:</b> ' + str(
                        quantity) + " " + uom + '<br/>___________'

            if include_scheduled_date:
                order_line_str += '\n*Scheduled Date:* ' + str(schedule_date or '-')
                message_in += '<br/><b>Scheduled Date:</b> ' + str(schedule_date or '-')

            if include_date_done:
                order_line_str += '\n*Effective Date:* ' + str(date_done or '-')
                message_in += '<br/><b>Effective Date:</b> ' + str(date_done or '-')

            if include_shipping_policy:
                order_line_str += '\n*Shipping Policy:* ' + str(
                    dict(self._fields['move_type'].selection).get(self.move_type) if self.move_type else '-')
                message_in += '<br/><b>Shipping Policy:</b> ' + str(
                    dict(self._fields['move_type'].selection).get(self.move_type) if self.move_type else '-')

        if append_signature:
            order_line_str += '\n\n' + self.env.user.whatsapp_signature if self.env.user.whatsapp_signature else ""
        if attachment:
            report_template = self.env['ir.actions.report'].sudo().search(
                [('model', '=', 'stock.picking'), ('report_type', '=', 'qweb-pdf'),
                 ('report_name', '=', 'stock.report_deliveryslip')], limit=1)
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
            'model_name': 'stock.picking',
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

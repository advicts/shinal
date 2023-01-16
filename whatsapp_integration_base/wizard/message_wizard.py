# -*- coding: utf-8 -*-
import json

import phonenumbers
import requests
from phonenumbers import carrier, number_type, NumberParseException

from odoo import models, fields, api
from odoo.exceptions import UserError


class MessageWizard(models.TransientModel):
    _name = "message.popup.wizard"

    recipient_ids = fields.Many2many("res.partner", string='Message Recipients')
    multi_recipient = fields.Boolean()
    message = fields.Text(
        default=lambda self: "\n\n" + self.env.user.whatsapp_signature if self.env.user.whatsapp_signature else "")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    single_recipient_number = fields.Char()
    message_chatter_log = fields.Boolean('Log the Message in Chatter')
    model_name = fields.Char()
    chatter_message = fields.Text()
    chatter_res_id = fields.Integer()
    no_mobile = fields.Boolean()

    @api.onchange('recipient_ids')
    def change_recipient(self):
        if self.recipient_ids:
            no_of_rec = len(self.recipient_ids.ids)
            last_rec = self.recipient_ids[no_of_rec - 1]
            if last_rec.mobile:
                self.no_mobile = False
            else:
                self.no_mobile = True

    def check_authentication(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        instance_id = ICPSudo.get_param('whatsapp_integration_base.instance_id')
        whatsapp_token = ICPSudo.get_param('whatsapp_integration_base.whatsapp_token')

        url = "https://api.chat-api.com/instance" + instance_id + "/status?token=" + whatsapp_token

        response = (requests.get(url)).text
        response = json.loads(response)
        status = None
        if response:
            status = response['accountStatus'] if 'accountStatus' in response else ''
        if status == 'authenticated':
            return True
        else:
            return False

    def send_message(self):
        if self.check_authentication():
            ICPSudo = self.env['ir.config_parameter'].sudo()
            instance_id = ICPSudo.get_param('whatsapp_integration_base.instance_id')
            whatsapp_token = ICPSudo.get_param('whatsapp_integration_base.whatsapp_token')

            url = "https://api.chat-api.com/instance" + instance_id + "/sendMessage?token=" + whatsapp_token

            recipient_ids = self.recipient_ids
            message = self.message
            single_recipient_number = self.single_recipient_number
            if single_recipient_number:
                single_recipient_number = single_recipient_number.replace(" ", "")
            data = {}
            status = False
            for recipient in recipient_ids:
                if recipient.mobile or self.single_recipient_number:
                    try:
                        is_valid = carrier._is_mobile(
                            number_type(phonenumbers.parse(recipient.mobile or self.single_recipient_number)))
                    except NumberParseException:
                        raise UserError("Invalid Phone Number for " + recipient.name)
                    if not is_valid:
                        raise UserError("Invalid Phone Number for " + recipient.name)
                    else:
                        mobile = single_recipient_number if single_recipient_number else recipient.mobile
                        if mobile[0] == '+':
                            mobile = mobile[1:]
                        if message:
                            data = {
                                'phone': mobile,
                                'body': message
                            }
                            response = requests.post(url, data)
                            response = response.json()
                            if response['sent']:
                                status = True
                            else:
                                raise UserError("Message Sending Failed for " + recipient.name + "!")

                    if self.attachment_ids:
                        for attachment in self.attachment_ids:
                            att = "data:" + attachment['mimetype'] + ";base64," + (attachment['datas']).decode('utf-8')
                            data = {
                                'phone': mobile,
                                'body': att,
                                'filename': attachment.name
                            }
                            file_url = "https://api.chat-api.com/instance" + instance_id + "/sendFile?token=" + whatsapp_token

                            response = requests.post(file_url, data)
                            if response.status_code == 200:
                                status = True
                            else:
                                raise UserError("Message attachment Sending Failed for " + recipient.name + "!")

                    if status and self.message_chatter_log:
                        model_name = self.model_name if self.model_name else 'res.partner'
                        message_chatter = self.chatter_message if self.chatter_message else '<i class="fa fa-whatsapp '\
                                                                                            'text-success" ' \
                                                                                            'aria-hidden="true"> ' \
                                                                                            '<em>WhatsApp ' \
                                                                                            'Message</em></i><br/>' + \
                                                                                            self.message
                        res_id = self.chatter_res_id if self.chatter_res_id else recipient.id
                        attachment_ids = self.attachment_ids.ids if self.attachment_ids else []
                        self.env['mail.message'].create(
                            {'body': message_chatter, 'model': model_name, 'res_id': res_id,
                             'message_type': 'comment', 'attachment_ids': attachment_ids})

                else:
                    raise UserError("Invalid Phone Number for " + recipient.name)

        else:
            raise UserError("WhatsApp is not active now!")

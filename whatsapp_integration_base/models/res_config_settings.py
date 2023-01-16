# -*- coding: utf-8 -*-
import json

import requests

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    instance_id = fields.Char('WhatsApp Instance ID')
    whatsapp_token = fields.Char('WhatsApp Token')
    authenticated = fields.Selection([('fail', 'Fail'), ('success', 'Success')], string="Login Authentication")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('whatsapp_integration_base.instance_id', self.instance_id)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_base.whatsapp_token', self.whatsapp_token)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_base.authenticated', self.authenticated)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        instance_id = ICPSudo.get_param('whatsapp_integration_base.instance_id')
        whatsapp_token = ICPSudo.get_param('whatsapp_integration_base.whatsapp_token')
        authenticated = ICPSudo.get_param('whatsapp_integration_base.authenticated') or 'fail'
        res.update(
            instance_id=instance_id,
            whatsapp_token=whatsapp_token,
            authenticated=authenticated,
        )
        return res

    def get_qr_code(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        instance_id = ICPSudo.get_param('whatsapp_integration_base.instance_id')
        whatsapp_token = ICPSudo.get_param('whatsapp_integration_base.whatsapp_token')

        url = "https://api.chat-api.com/instance" + instance_id + "/status?token=" + whatsapp_token

        response = (requests.get(url)).text
        response = json.loads(response)

        res = self.env['qr.popup.wizard'].create({'qr_code': response['qrCode'].split(',')[1]}).id

        return {
            'name': 'QR Code',
            'view_mode': 'form',
            'res_model': 'qr.popup.wizard',
            'type': 'ir.actions.act_window',
            'res_id': res,
            'target': 'new',
        }

    def whatsapp_logout(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        instance_id = ICPSudo.get_param('whatsapp_integration_base.instance_id')
        whatsapp_token = ICPSudo.get_param('whatsapp_integration_base.whatsapp_token')

        url = "https://api.chat-api.com/instance" + instance_id + "/logout?token=" + whatsapp_token
        response = (requests.get(url)).text
        response = json.loads(response)
        if response['result']:
            self.env['ir.config_parameter'].set_param('whatsapp_integration_base.authenticated', 'fail')


class QRWizard(models.TransientModel):
    _name = "qr.popup.wizard"

    qr_code = fields.Image()

    def check_authentication(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        instance_id = ICPSudo.get_param('whatsapp_integration_base.instance_id')
        whatsapp_token = ICPSudo.get_param('whatsapp_integration_base.whatsapp_token')

        url = "https://api.chat-api.com/instance" + instance_id + "/status?token=" + whatsapp_token

        response = (requests.get(url)).text
        response = json.loads(response)

        status = response['accountStatus']

        if status == 'got qr code':
            self.env['ir.config_parameter'].set_param('whatsapp_integration_base.authenticated',
                                                      'fail')
        else:
            self.env['ir.config_parameter'].set_param('whatsapp_integration_base.authenticated',
                                                      'success')

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ac_append_signature = fields.Boolean('WhatsApp Signature')
    ac_chatter_log = fields.Boolean('Chatter Log')
    ac_attachment = fields.Boolean('Invoice/ Payment Attachment')
    ac_message_type = fields.Selection([('detail', 'Detailed Message'), ('short', 'Short Message')],
                                       string='Message Type')
    ac_include_product_details = fields.Boolean('Product Details')
    ac_include_invoice_date = fields.Boolean('Invoice Date')
    ac_include_payment_terms = fields.Boolean('Payment Terms')
    ac_include_total_details = fields.Boolean("Total Amount")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_append_signature',
                                                  self.ac_append_signature)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_chatter_log', self.ac_chatter_log)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_attachment', self.ac_attachment)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_message_type', self.ac_message_type)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_include_product_details',
                                                  self.ac_include_product_details)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_include_invoice_date',
                                                  self.ac_include_invoice_date)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_include_payment_terms',
                                                  self.ac_include_payment_terms)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_account.ac_include_total_details',
                                                  self.ac_include_total_details)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ac_append_signature = ICPSudo.get_param('whatsapp_integration_account.ac_append_signature')
        ac_chatter_log = ICPSudo.get_param('whatsapp_integration_account.ac_chatter_log')
        ac_attachment = ICPSudo.get_param('whatsapp_integration_account.ac_attachment')
        ac_message_type = ICPSudo.get_param('whatsapp_integration_account.ac_message_type')
        ac_include_product_details = ICPSudo.get_param('whatsapp_integration_account.ac_include_product_details')
        ac_include_invoice_date = ICPSudo.get_param('whatsapp_integration_account.ac_include_invoice_date')
        ac_include_payment_terms = ICPSudo.get_param('whatsapp_integration_account.ac_include_payment_terms')
        ac_include_total_details = ICPSudo.get_param('whatsapp_integration_account.ac_include_total_details')
        res.update(
            ac_append_signature=ac_append_signature,
            ac_chatter_log=ac_chatter_log,
            ac_attachment=ac_attachment,
            ac_message_type=ac_message_type,
            ac_include_product_details=ac_include_product_details,
            ac_include_invoice_date=ac_include_invoice_date,
            ac_include_payment_terms=ac_include_payment_terms,
            ac_include_total_details=ac_include_total_details,
        )
        return res

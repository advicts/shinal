# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pu_append_signature = fields.Boolean('WhatsApp Signature')
    pu_chatter_log = fields.Boolean('Chatter Log')
    pu_attachment = fields.Boolean('Purchase Order Attachment')
    pu_message_type = fields.Selection([('detail', 'Detailed Message'), ('short', 'Short Message')], string='Message Type')
    pu_include_product_details = fields.Boolean('Product Details')
    pu_include_order_deadline = fields.Boolean('Order Deadline')
    pu_include_payment_terms = fields.Boolean('Payment Terms')
    pu_include_total_details = fields.Boolean("Total Amount")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_append_signature',
                                                  self.pu_append_signature)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_chatter_log', self.pu_chatter_log)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_attachment', self.pu_attachment)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_message_type', self.pu_message_type)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_include_product_details',
                                                  self.pu_include_product_details)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_include_order_deadline',
                                                  self.pu_include_order_deadline)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_include_payment_terms',
                                                  self.pu_include_payment_terms)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_purchase.pu_include_total_details',
                                                  self.pu_include_total_details)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        pu_append_signature = ICPSudo.get_param('whatsapp_integration_purchase.pu_append_signature')
        pu_chatter_log = ICPSudo.get_param('whatsapp_integration_purchase.pu_chatter_log')
        pu_attachment = ICPSudo.get_param('whatsapp_integration_purchase.pu_attachment')
        pu_message_type = ICPSudo.get_param('whatsapp_integration_purchase.pu_message_type')
        pu_include_product_details = ICPSudo.get_param('whatsapp_integration_purchase.pu_include_product_details')
        pu_include_order_deadline = ICPSudo.get_param('whatsapp_integration_purchase.pu_include_order_deadline')
        pu_include_payment_terms = ICPSudo.get_param('whatsapp_integration_purchase.pu_include_payment_terms')
        pu_include_total_details = ICPSudo.get_param('whatsapp_integration_purchase.pu_include_total_details')
        res.update(
            pu_append_signature=pu_append_signature,
            pu_chatter_log=pu_chatter_log,
            pu_attachment=pu_attachment,
            pu_message_type=pu_message_type,
            pu_include_product_details=pu_include_product_details,
            pu_include_order_deadline=pu_include_order_deadline,
            pu_include_payment_terms=pu_include_payment_terms,
            pu_include_total_details=pu_include_total_details,
        )
        return res

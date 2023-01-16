# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    append_signature = fields.Boolean('WhatsApp Signature')
    chatter_log = fields.Boolean('Chatter Log')
    attachment = fields.Boolean('Sale Order Attachment')
    message_type = fields.Selection([('detail', 'Detailed Message'), ('short', 'Short Message')], default='detail')
    include_product_details = fields.Boolean('Product Details')
    include_payment_terms = fields.Boolean('Payment Terms')
    include_total_details = fields.Boolean("Total Amount")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('whatsapp_integration_sale.append_signature', self.append_signature)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_sale.chatter_log', self.chatter_log)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_sale.attachment', self.attachment)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_sale.message_type', self.message_type)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_sale.include_product_details',
                                                  self.include_product_details)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_sale.include_payment_terms',
                                                  self.include_payment_terms)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_sale.include_total_details',
                                                  self.include_total_details)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        append_signature = ICPSudo.get_param('whatsapp_integration_sale.append_signature')
        chatter_log = ICPSudo.get_param('whatsapp_integration_sale.chatter_log')
        attachment = ICPSudo.get_param('whatsapp_integration_sale.attachment')
        message_type = ICPSudo.get_param('whatsapp_integration_sale.message_type')
        include_product_details = ICPSudo.get_param('whatsapp_integration_sale.include_product_details')
        include_payment_terms = ICPSudo.get_param('whatsapp_integration_sale.include_payment_terms')
        include_total_details = ICPSudo.get_param('whatsapp_integration_sale.include_total_details')
        res.update(
            append_signature=append_signature,
            chatter_log=chatter_log,
            attachment=attachment,
            message_type=message_type,
            include_product_details=include_product_details,
            include_payment_terms=include_payment_terms,
            include_total_details=include_total_details,
        )
        return res

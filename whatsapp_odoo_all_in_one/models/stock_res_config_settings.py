# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    st_append_signature = fields.Boolean('WhatsApp Signature')
    st_chatter_log = fields.Boolean('Chatter Log')
    st_attachment = fields.Boolean('Delivery Order Attachment')
    st_message_type = fields.Selection([('detail', 'Detailed Message'), ('short', 'Short Message')], string='Message Type')
    st_include_product_details = fields.Boolean('Product Details')
    st_include_shipping_policy = fields.Boolean('Shipping Policy')
    st_include_scheduled_date = fields.Boolean("Scheduled Date")
    st_include_date_done = fields.Boolean("Effective Date")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_append_signature', self.st_append_signature)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_chatter_log', self.st_chatter_log)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_attachment', self.st_attachment)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_message_type', self.st_message_type)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_include_product_details',
                                                  self.st_include_product_details)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_include_shipping_policy',
                                                  self.st_include_shipping_policy)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_include_scheduled_date',
                                                  self.st_include_scheduled_date)
        self.env['ir.config_parameter'].set_param('whatsapp_integration_stock.st_include_date_done',
                                                  self.st_include_date_done)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        st_append_signature = ICPSudo.get_param('whatsapp_integration_stock.st_append_signature')
        st_chatter_log = ICPSudo.get_param('whatsapp_integration_stock.st_chatter_log')
        st_attachment = ICPSudo.get_param('whatsapp_integration_stock.st_attachment')
        st_message_type = ICPSudo.get_param('whatsapp_integration_stock.st_message_type')
        st_include_product_details = ICPSudo.get_param('whatsapp_integration_stock.st_include_product_details')
        st_include_shipping_policy = ICPSudo.get_param('whatsapp_integration_stock.st_include_shipping_policy')
        st_include_scheduled_date = ICPSudo.get_param('whatsapp_integration_stock.st_include_scheduled_date')
        st_include_date_done = ICPSudo.get_param('whatsapp_integration_stock.st_include_date_done')
        res.update(
            st_append_signature=st_append_signature,
            st_chatter_log=st_chatter_log,
            st_attachment=st_attachment,
            st_message_type=st_message_type,
            st_include_product_details=st_include_product_details,
            st_include_shipping_policy=st_include_shipping_policy,
            st_include_scheduled_date=st_include_scheduled_date,
            st_include_date_done=st_include_date_done,
        )
        return res

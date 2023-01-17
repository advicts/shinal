from odoo import api, models

class Partner(models.Model):
    _inherit = 'res.partner'

    def open_whatsapp_phone(self):
        # Construct the WhatsApp URL with the phone number as the send_to parameter
        url = 'https://wa.me/{}'.format(self.phone.replace(' ', ''))

        # Open the URL in a new tab
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def open_whatsapp_mobile(self):
        # Construct the WhatsApp URL with the mobile number as the send_to parameter
        url = 'https://wa.me/{}'.format(self.mobile.replace(' ', ''))

        # Open the URL in a new tab
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

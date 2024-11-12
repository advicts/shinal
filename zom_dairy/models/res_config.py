from email.policy import default
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    zom_app_url = fields.Char(config_parameter='web.zom_app_url',string = 'Zom App Url', help='connect odoo with odoo db', copy=True, default='', store=True)


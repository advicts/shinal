
from odoo import fields, models, api, _


class PartnerCategory(models.Model):
    _name = 'partner.category'

    name = fields.Char("Name", required=True)

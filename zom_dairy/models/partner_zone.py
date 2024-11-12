from odoo import api, fields, models


class PartnerZone(models.Model):
    _name = 'partner.zone'
    _rec_name = 'name'

    name = fields.Char()
    code = fields.Char(string="Code")

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        if self.partner_id:
            self.partner_id.update_partner_doc()
        return res

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_draft(self):
        if not self.env.user.has_group(
                'ejaf_account_journal_access.group_cashier_reset_draft'):
            raise AccessError(_("You don't have the access rights to Reset Draft."))
        res = super(AccountPayment, self).action_draft()
        return res

    def unlink(self):
        if not self.env.user.has_group(
                'ejaf_account_journal_access.group_cashier_delete'):
            raise AccessError(_("You don't have the access rights to Delete  Payment."))
        return super(AccountPayment, self).unlink()




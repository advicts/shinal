from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_draft(self):
        for rec in self:
            if rec.move_type == 'entry' and not rec.env.user.has_group(
                    'ejaf_account_journal_access.group_journal_reset_draft'):
                raise AccessError(_("You don't have the access rights to Reset Draft."))
            res = super(AccountMove, self).button_draft()
        return res

    def unlink(self):
        for rec in self:
            if rec.move_type == 'entry' and not rec.env.user.has_group(
                    'ejaf_account_journal_access.group_journal_delete'):
                raise AccessError(_("You don't have the access rights to Delete Entry."))
        return super(AccountMove, self).unlink()

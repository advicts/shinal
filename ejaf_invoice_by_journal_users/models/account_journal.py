from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _limited_journal_groups(self):
        limited_journal_groups = self.env.ref('ejaf_invoice_by_journal_users.restricted_journal_group').id
        groups = self.env['res.groups'].search([('id', 'in', [limited_journal_groups])])
        return [('groups_id', 'in', groups.ids)]

    user_ids = fields.Many2many('res.users', 'user_journal_group_rel','user_id','journal_id',string='Allow Access Users', domain=_limited_journal_groups)

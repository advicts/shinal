from odoo import api, models, tools


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        """
        Inherit Check method to create a Readonly User
        """
        ret = super(IrModelAccess, self).check(model, mode=mode, raise_exception=raise_exception)
        if self.check_groups('simple_readonly_user.group_simple_readonly_user'):
            if mode != 'read':
                return False
        return ret

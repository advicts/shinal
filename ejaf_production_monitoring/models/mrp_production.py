from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    monitor_count = fields.Integer(compute="compute_monitor_count")

    def check_production_monitor(self):
        for rec in self:
            if self.env['production.monitoring'].search_count(
                    [('mo_id', '=', rec.id), ('is_confirmed', '!=', True)]) > 0:
                raise ValidationError(
                    _('You can Not Validate Or Confirm  Mrp  Before Close All Production Monitor.'))

    def validate_mrp(self):
        self.check_production_monitor()
        return super(MrpProduction, self).validate_mrp()

    def action_confirm(self):
        self.check_production_monitor()
        return super(MrpProduction, self).action_confirm()

    def compute_monitor_count(self):
        for rec in self:
            rec.monitor_count = self.env['production.monitoring'].search_count(
                [('mo_id', '=', rec.id)])

    def open_production_monitoring(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "ejaf_production_monitoring.production_monitoring_action_view")

        action['domain'] = [('mo_id', '=', self.id)]
        return action

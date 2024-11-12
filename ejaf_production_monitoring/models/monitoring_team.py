# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MonitoringTeam(models.Model):
    _name = 'monitoring.team'
    _rec_name = 'name'
    _description = 'Production Monitoring Types'

    name = fields.Char()
    active = fields.Boolean('Active', default=True, copy=False)
    close_issue_count = fields.Integer(compute="compute_close_issue_count")

    def compute_close_issue_count(self):
        for rec in self:
            rec.close_issue_count = self.env['production.monitoring'].search_count(
                [('type_id', '=', rec.id), ('is_confirmed', '=', True),('is_final_stage', '=', True)])

    def action_view_p_m(self):
        return {
            'name': 'Production Monitoring',
            'type': 'ir.actions.act_window',
            'res_model': 'production.monitoring',
            'view_mode': 'kanban,tree,form',
            'domain': [('type_id', '=', self.id)],
        }

    def action_view_p_m_close(self):
        return {
            'name': 'Closed Production Monitoring',
            'type': 'ir.actions.act_window',
            'res_model': 'production.monitoring',
            'view_mode': 'kanban,tree,form',
            'domain': [('type_id', '=', self.id), ('is_confirmed', '=', True), ('is_final_stage', '=', True)],

        }

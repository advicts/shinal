from odoo import models, fields, api
from datetime import datetime

class ProjectTask(models.Model):
    _inherit = 'project.task'

    date_create = fields.Date(string='Date of Create', default=fields.Date.context_today)
    date_finish = fields.Date(string='Date of Finish')

    @api.model
    def create(self, vals):
        # Set the create date when the task is created
        vals['date_create'] = fields.Date.context_today(self)
        return super(ProjectTask, self).create(vals)

    def write(self, vals): 
        if 'stage_id' in vals: 
            finished_stages = self.env['project.task.type'].search([('is_finished', '=', True)]) 
            if vals['stage_id'] in finished_stages.ids:
                vals['date_finish'] = fields.Date.context_today(self)

        return super(ProjectTask, self).write(vals)

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_finished = fields.Boolean(string='Is Finished', default=False)

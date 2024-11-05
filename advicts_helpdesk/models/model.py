from odoo import models, fields, api
from datetime import datetime

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    date_create = fields.Date(string='Date of Create', default=fields.Date.context_today)
    date_finish = fields.Date(string='Date of Finish')

    @api.model
    def create(self, vals):
        # Set the create date when the ticket is created
        vals['date_create'] = fields.Date.context_today(self)
        return super(HelpdeskTicket, self).create(vals)

    def write(self, vals): 
        if 'stage_id' in vals: 
            # Get the finished stages for helpdesk tickets
            finished_stages = self.env['helpdesk.stage'].search([('is_finished', '=', True)]) 
            if vals['stage_id'] in finished_stages.ids:
                vals['date_finish'] = fields.Date.context_today(self)

        return super(HelpdeskTicket, self).write(vals)

class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    is_finished = fields.Boolean(string='Is Finished', default=False)

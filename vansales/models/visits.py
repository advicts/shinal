from odoo import models, fields, api


class Visits(models.Model):
    
    _name = "vansale.visit"
    _description = "Visits"
    _order = 'date desc, id desc'

    name = fields.Char('Name', required=True,index=True,copy=False, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Customer',required=True, index=True)
    date = fields.Datetime(string='Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    note = fields.Text(string="Notes",required=True)
    vansales_ref = fields.Char(string="Vansales Reference",copy=False)
    _sql_constraints = [('vansales_ref_uniq', 'unique (vansales_ref)',
                         "The Tablet Order ID should be unique")]
    partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    is_vansales = fields.Boolean('Is Vansales', default=False)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vansale.visit') or '/'
        return super(Visits, self).create(vals)



from copy import copy
from odoo import models, fields, api


class VisitsVisit(models.Model):
  _name = 'visits.visit'
  _inherit = ['mail.thread']

  name = fields.Char(string="Code", index=True, default='New', copy=False)
  partner_id = fields.Many2one('res.partner',
                               string='Customer',
                               required=True,
                               track_visibility='onchange')

  salesperson_id = fields.Many2one('res.users', string='SalesPerson', track_visibility='onchange')
  visiting_date = fields.Date('Visiting Date',
                              default=fields.Datetime.now,
                              track_visibility='onchange')
  visiting_day = fields.Selection([('Monday', 'Monday'), ('Tuesday', 'Tuesday'),
                                   ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'),
                                   ('Friday', 'Friday'), ('Saturday', 'Saturday'),
                                   ('Sunday', 'Sunday')],
                                  'Visiting Day',
                                  index=True,
                                  default='Monday')
  start_date = fields.Datetime('Start Date')
  end_date = fields.Datetime('End Date')
  rate_visit = fields.Integer('Rate', track_visibility='onchange')
  visit_notes = fields.Char('Note')
  visit_planning_id = fields.Many2one('visits.planning', string='Visit Planning')
  state = fields.Selection([
      ('draft', 'Draft'),
      ('confirmed', 'Confirmed'),
      ('canceled', 'Canceled'),
      ('done', 'Done'),
      ('inprogress', 'Inprogress'),
      ('postponed', 'Postponed'),
  ],
                           string='Status',
                           readonly=True,
                           copy=False,
                           index=True,
                           track_visibility='onchange',
                           default='draft')
  visit_status = fields.Selection(
      [
          ('success', 'Successful visit'),
          ('failed', 'Failed visit'),
      ],
      string='Visit Status',
      copy=False,
      index=True,
      track_visibility='onchange',
  )
  orders_ids = fields.One2many('sale.order', 'visit_id', string='Orders')
  payment_ids = fields.One2many('account.payment', 'visit_id', string="Payments")
  return_ids = fields.One2many('stock.picking', 'visit_id', string="Returns")



  @api.model
  def create(self, vals):
    if vals.get('name', 'New') == 'New':
      vals['name'] = self.env['ir.sequence'].next_by_code('visits.visit') or '/'
    return super(VisitsVisit, self).create(vals)

  def action_view_orders(self):
    for rec in self:
      orders = self.mapped('orders_ids')
      return {
          'name': ('Sales Orders'),
          'view_type': 'form',
          'view_mode': 'tree,form',
          'res_model': 'sale.order',
          'type': 'ir.actions.act_window',
          'target': 'current',
          'context': {
              'default_partner_id': rec.partner_id.id,
              'default_visit_id': rec.id
          },
          'domain': [('id', 'in', orders.ids)],
      }
  def action_view_payments(self):
    for rec in self:
      payment_ids = self.mapped('payment_ids')
      return {
          'name': ('Payments'),
          'view_type': 'form',
          'view_mode': 'tree,form',
          'res_model': 'account.payment',
          'type': 'ir.actions.act_window',
          'target': 'current',
          'context': {
              'default_partner_id': rec.partner_id.id,
              'default_visit_id': rec.id
          },
          'domain': [('id', 'in', payment_ids.ids)],
      }

  def action_view_returns(self):
    for rec in self:
      return_ids = self.mapped('return_ids')
      return {
          'name': ('Return'),
          'view_type': 'form',
          'view_mode': 'tree,form',
          'res_model': 'stock.picking',
          'type': 'ir.actions.act_window',
          'target': 'current',
          'context': {
              'default_partner_id': rec.partner_id.id,
              'default_visit_id': rec.id
          },
          'domain': [('id', 'in', return_ids.ids)],
      }


  def action_confirmed(self):
    for rec in self:
      return rec.write({'state': 'confirmed'})

  def action_canceled(self):
    for rec in self:
      return rec.write({'state': 'canceled'})

  def action_done(self):
    for rec in self:
      return rec.write({'state': 'done'})

  def _check_visiting_date(self):
    visit_ids = self.search([("visiting_date", "<", fields.Date.today()),
                             ("state", "=", "confirmed")])
    if visit_ids:
      visit_ids.write({'state': 'done', 'visit_status': 'failed'})

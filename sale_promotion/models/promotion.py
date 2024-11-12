from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SalePromotion(models.Model):
  _name = 'sale.promotion'
  _order = 'id'

  name = fields.Char('Promotion Name', required=True, states={'closed': [('readonly', True)]})
  active = fields.Boolean('Active', default=True)
  default_currency_id = fields.Many2one('res.currency',
                                        string="Default Currency",
                                        required=True,
                                        default=lambda self: self.env.company.currency_id)

  state = fields.Selection([
      ('draft', ' New'),
      ('running', 'Running'),
      ('closed', 'Closed'),
  ],
                           string='Status',
                           copy=False,
                           index=True,
                           default='draft')
  start_at = fields.Datetime(string='Start at', states={'closed': [('readonly', True)]})
  end_at = fields.Datetime(string='End at', states={'closed': [('readonly', True)]})
  analytic_tag_id = fields.Many2one(string="Analytic Tag",
                                    comodel_name='account.analytic.tag',
                                    required=True)
  description = fields.Text(string="Description")

  ##################################################################################
  ## Rule Based on User
  ##################################################################################
  users_rule_based_on = fields.Selection([
      ('all', ' All Salespersons'),
      ('specific_teams', 'Specific Teams'),
      ('specific_user', 'Specific Salespersons'),
  ],
                                         string='User Rule Based on',
                                         copy=False,
                                         index=True,
                                         default='all',
                                         states={'closed': [('readonly', True)]})
  specific_team_ids = fields.Many2many('crm.team',
                                       string="Specific Teams",
                                       states={'closed': [('readonly', True)]})

  specific_user_ids = fields.Many2many('res.users',
                                       string="Specific Salespersons",
                                       states={'closed': [('readonly', True)]})
  ##############################################################################
  ## Rule Based on Customer
  ##################################################################################
  partner_rule_based_on = fields.Selection([
      ('all', ' All Customers'),
      ('specific_customer_category', 'Specific Customer Category'),
  ],
                                           string='Customer Rule Based on',
                                           copy=False,
                                           index=True,
                                           default='all',
                                           states={'closed': [('readonly', True)]})
  customer_category_ids = fields.Many2many(string='Customer Category',
                                           comodel_name='res.partner.category')

  ##############################################################################
  # Rule Based on Products
  ##############################################################################
  product_rule_based_on = fields.Selection([
      ('all', ' All Products'),
      ('specific_product_category', 'Specific Category'),
      ('specific_product_templates', 'Specific Product Templates'),
      ('specific_product', 'Specific Products'),
  ],
                                           string='Product Rule Based on',
                                           copy=False,
                                           index=True,
                                           default='all',
                                           states={'closed': [('readonly', True)]})

  specific_categ_ids = fields.Many2many('product.category',
                                        string="Specific Category",
                                        states={'closed': [('readonly', True)]})

  specific_product_ids = fields.Many2many('product.product',
                                          string="Specific Products",
                                          states={'closed': [('readonly', True)]})
  specific_product_temp_ids = fields.Many2many('product.template',
                                               string="Specific Product Templates",
                                               states={'closed': [('readonly', True)]})

  ##########################################################################################
  applied_on = fields.Selection([('total_order', 'Total Order'), ('order_lines', 'Order Lines')],
                                "Apply On",
                                default='total_order',
                                required=True,
                                help='promotion applicable on selected option',
                                states={'closed': [('readonly', True)]})
  reward_by = fields.Selection([('discounts', 'Discount'), ('discount_lines', 'Discount Lines'),
                                ('reward_product', 'Reward Product')],
                               "Reward by",
                               default='discounts',
                               required=True,
                               states={'closed': [('readonly', True)]})

  min_quantity = fields.Float('Min. Quantity', default=0, states={'closed': [('readonly', True)]})

  min_amount = fields.Float('Min. Amount', default=0, states={'closed': [('readonly', True)]})

  product_discounts_ids = fields.One2many('sale.promotion.discounts',
                                          'promotion_id',
                                          string='Discount Lines',
                                          states={'closed': [('readonly', True)]})

  product_rewards_ids = fields.One2many('sale.promotion.rewards',
                                        'promotion_id',
                                        string='Rewards',
                                        states={'closed': [('readonly', True)]})

  discount_type = fields.Selection([('fixed_amount', 'Fixed Amount'),
                                    ('percentage', 'Percentage %')],
                                   "Apply Discount",
                                   default='percentage',
                                   states={'closed': [('readonly', True)]})
  discount_fixed_amount = fields.Float('Discount Fixed Amount',
                                       default=0,
                                       states={'closed': [('readonly', True)]})
  discount_percentage = fields.Float('Discount Percentage',
                                     default=10,
                                     states={'closed': [('readonly', True)]})

  global_discount_product_id = fields.Many2one(
      string='Global Discount Product',
      comodel_name="product.product",
  )
  order_line_ids = fields.One2many('sale.order.line', 'promotion_id', string='Order Lines')

  def action_confirm(self):
    for rec in self:
      rec.state = 'running'

  def action_close(self):
    for rec in self:
      rec.state = 'closed'

  @api.onchange('applied_on')
  def _onchange_(self):
    self.reward_by = 'discounts'

  def _auto_close_promotion(self):
    to_be_closed = self.search([('state', '!=', 'closed'),
                                ('end_date', '<', fields.Datetime.today())])
    if to_be_closed:
      for rec in to_be_closed:
        rec.state = 'closed'

  @api.constrains('min_quantity')
  def _constrains_min_quantity(self):
    if self.applied_on == 'order_lines' and self.min_quantity == 0:
      raise ValidationError("can not set Min Qty to zero")


class SalePromotionDiscounts(models.Model):
  _name = 'sale.promotion.discounts'
  _order = 'sequence'

  sequence = fields.Integer(string='Sequence', default=1)
  promotion_id = fields.Many2one('sale.promotion', string='Promotion')
  discount_type = fields.Selection(
      [('fixed_amount', 'Fixed Amount'), ('percentage', 'Percentage %')],
      "Apply Discount",
      default='percentage',
  )
  amount = fields.Float('Discount', default=10, required=True)


class SalePromotionReward(models.Model):
  _name = 'sale.promotion.rewards'
  _order = 'sequence'

  sequence = fields.Integer(string='Sequence', default=1)
  promotion_id = fields.Many2one('sale.promotion', string='Promotion')
  product_id = fields.Many2one('product.product', string="Specific Product", required=True)
  product_uom_id = fields.Many2one('uom.uom', string="UOM", required=True)
  qty = fields.Float('Qty', default=1, required=True)

  @api.onchange('product_id')
  def _onchange_product_id(self):
    res = {}
    if self.product_id:
      if self.product_id.uom_sell_ids:
        res.update({'domain': {'product_uom_id': [('id', 'in', self.product_id.uom_sell_ids.ids)]}})
      else:
        res.update(
            {'domain': {
                'product_uom_id': [('category_id', '=', self.product_id.uom_id_categ.id)]
            }})

    else:
      res.update({'domain': {'product_uom_id': [('id', 'in', [])]}})
    return res

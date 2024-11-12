from odoo import models, api, fields, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    salesperson_id = fields.Many2one('res.users', string="Salesperson", compute="_compute_salesperson_id", store=True)

    @api.depends('sale_id')
    def _compute_salesperson_id(self):
        for rec in self:
            if rec.sale_id and rec.sale_id.user_id:
                rec.salesperson_id = rec.sale_id.user_id.id


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def _get_default_scrap_location_id(self):
        company_id = self.env.context.get('default_company_id') or self.env.company.id
        return self.env['stock.location'].search(
            [('scrap_location', '=', True), ('company_id', 'in', [company_id, False])], limit=1).id

    free_product = fields.Boolean(string='Free Product', copy=False, default=False)
    free_product_location_id = fields.Many2one(
        'stock.location', 'Free Product Location', default=_get_default_scrap_location_id,
        domain="[('scrap_location', '=', True), ('company_id', 'in', [company_id, False])]",
        states={'done': [('readonly', True)]}, check_company=True)

    @api.onchange('free_product_location_id')
    def _fill_scrap_location(self):
        for scrap in self:
            if scrap.free_product_location_id:
                scrap.scrap_location_id = scrap.free_product_location_id.id

    def do_scrap(self):
        for scrap in self:
            if not scrap.free_product:
                return super(StockScrap, self).do_scrap()
            else:
                self._check_company()
                for scrap in self:
                    scrap.name = self.env['ir.sequence'].next_by_code('stock.scrap.free') or _('New')
                    move = self.env['stock.move'].create(scrap._prepare_move_values())
                    # master: replace context by cancel_backorder
                    move.with_context(is_scrap=True)._action_done()
                    scrap.write({'move_id': move.id, 'state': 'done'})
                    scrap.date_done = fields.Datetime.now()
                return True

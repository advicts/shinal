# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.sql import column_exists, create_column


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    production_date = fields.Datetime(string="Production Date")


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_generate_serial(self):
        res = super().action_generate_serial()
        if self.lot_producing_id:
            self.lot_producing_id.production_date = self.date_planned_start
        return res

class StockInventory(models.Model):
    _inherit = 'stock.quant'

    expiration_date = fields.Datetime(related='lot_id.expiration_date', string='Expiration Date', store=True)
    production_date = fields.Datetime(related='lot_id.production_date', string='Production Date', store=True)
    force_inventory_date = fields.Date(default=fields.Date.today(),
                                       help="Force the inventory moves and accounting entries to a given date",
                                       )

    @api.model
    def _get_inventory_fields_write(self):
        res = super(StockInventory, self)._get_inventory_fields_write()
        res.append('force_inventory_date')
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super(StockInventory, self)._get_inventory_move_values(qty, location_id, location_dest_id, out=out)
        res['date'] = self.force_inventory_date
        return res


    def _auto_init(self):
        if not column_exists(self.env.cr, "stock_quant", "expiration_date"):
            create_column(self.env.cr, "stock_quant", "expiration_date", "VARCHAR")
        if not column_exists(self.env.cr, "stock_quant", "production_date"):
            create_column(self.env.cr, "stock_quant", "production_date", "VARCHAR")
        return super()._auto_init()


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        """ Overridden to Force  date of move and lines.
        """
        result = super(StockMove, self)._action_done(cancel_backorder)
        moves = self.filtered(lambda m: m.state == 'done')
        if moves:
            for move in moves:
                print("move.date: ", move.date)
                # move_date = move.inventory_id.force_inventory_date or move.picking_id.scheduled_date
                # if move_date:
                #     move.sudo().write({"date": move_date})
                #     move_lines = move.move_line_ids
                #     move_lines.sudo().write({"date": move_date})
        return result

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                  cost):
        """ Overridden to Force  date of move entry.
        """
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        if move_lines:
            move_date = self.inventory_id.force_inventory_date or self.picking_id.scheduled_date or self._context.get(
                'force_period_date', fields.Date.context_today(self))

            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': move_date,
                'ref': description,
                'stock_move_id': self.id,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'move_type': 'entry',
            })
            new_account_move._post()

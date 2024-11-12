# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    inline_lot_number = fields.Boolean(string='Inline Lot Number')

    @api.onchange('code')
    def onchange_type_code(self):
        if self.code != 'internal':
            self.inline_lot_number = False


class StockMove(models.Model):
    _inherit = 'stock.move'

    allowed_lot_ids = fields.Many2many('stock.production.lot', 'move_lot_rel', 'move_id', 'lot_id', string='Allowed Lots', compute='get_allowed_lots')
    inline_lot_number = fields.Boolean(related='picking_id.picking_type_id.inline_lot_number', string='Inline Lot Number')

    @api.depends('picking_code', 'location_id', 'product_id', 'company_id')
    def get_allowed_lots(self):
        for move in self:
            if move.picking_code in ['internal']:
                allowed_lots = self.env['stock.production.lot']
                product_lots = self.env['stock.production.lot'].search([('product_id', '=', move.product_id.id), ('company_id', '=', move.company_id.id)])
                if product_lots:
                    allowed_lots = self.env['stock.quant'].search([('product_id', '=', move.product_id.id),
                                      ('lot_id', 'in', product_lots.ids),
                                      ('quantity', '!=', 0),
                                      ('location_id', '=', move.location_id.id)]).mapped('lot_id')
            else:
                allowed_lots = self.env['stock.production.lot'].search([('product_id', '=', move.product_id.id), ('company_id', '=', move.company_id.id)])
            move.allowed_lot_ids = [(6, 0, allowed_lots.ids)]

    @api.onchange('lot_ids')
    def _onchange_lot_ids(self):
        if self.picking_code not in ['internal']:
            return super()._onchange_lot_ids()

    def _action_confirm(self, merge=True, merge_into=False):
        if all(mv.inline_lot_number for mv in self):
            merge = False
        return super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)

    def _set_lot_ids(self):
        super(StockMove, self)._set_lot_ids()
        for move in self:
            if move.product_id.tracking != 'lot' or not move.inline_lot_number:
                continue

            if len(move.lot_ids) > 1:
                raise ValidationError(_("Select one lot number for each move of [%s]." % (move.product_id.display_name)))

            move_lines_commands = []
            if move.picking_type_id.show_reserved is False:
                mls = move.move_line_nosuggest_ids
            else:
                mls = move.move_line_ids
            mls = mls.filtered(lambda ml: ml.lot_id)
            for ml in mls:
                if ml.qty_done and ml.lot_id not in move.lot_ids:
                    move_lines_commands.append((2, ml.id))
            ls = move.move_line_ids.lot_id
            for lot in move.lot_ids:
                if lot not in ls:
                    move_line_vals = self._prepare_move_line_vals(quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = move.product_id.uom_id.id
                    move_line_vals['qty_done'] = move.product_uom_qty or 1
                    move_lines_commands.append((0, 0, move_line_vals))
                else:
                    move_line = move.move_line_ids.filtered(lambda line: line.lot_id.id == lot.id)
                    move_line.qty_done = move.product_uom_qty or 1
            move.write({'move_line_ids': move_lines_commands})

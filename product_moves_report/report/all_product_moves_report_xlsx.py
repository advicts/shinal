# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import fields, models, _
import pytz
from pytz import timezone

_logger = logging.getLogger(__name__)


class AllProductMovesReportXlsx(models.AbstractModel):
    _name = 'report.product_moves_report.all_product_moves_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        """ Draw the excel report """
        partner_ids = data['form']['partner_ids']
        salesperson_ids = data['form']['salesperson_ids']

        move_line_obj = self.env['stock.move.line']
        product_obj = self.env['product.product']
        product_categ_obj = self.env['product.category']
        user_tz = timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        date_from = fields.Datetime.from_string(data['form']['date_from'])
        date_to = fields.Datetime.from_string(data['form']['date_to'])
        location_id = data['form']['location_id']
        product_categ_id = data['form']['product_categ_id']
        is_all_internal_location = data['form']['is_all_internal_location']

        date_only_to_dt = user_tz.localize(datetime.combine(date_from, datetime.min.time()))
        user_tz_date_from = date_only_to_dt.astimezone(pytz.utc)
        localize_utc_date_from = user_tz_date_from.replace(tzinfo=None)

        date_from = fields.Datetime.to_string(localize_utc_date_from)
        date_to_only_to_dt = user_tz.localize(datetime.combine(date_to, datetime.max.time()))
        user_tz_date_to = date_to_only_to_dt.astimezone(pytz.utc)
        localize_utc_date_to = user_tz_date_to.replace(tzinfo=None)

        date_to = fields.Datetime.to_string(localize_utc_date_to)
        sheet = workbook.add_worksheet('sheet')

        header_format = workbook.add_format({
            'bold': 1,
            'border': 2,
            'align': 'left',
            'valign': 'vcenter',
            'color': 'blue',
        })

        left_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'bold': 1,
            'border': 1,
            'bg_color': 'silver',

        })

        center_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'bold': 1,
            'border': 1,
            'bg_color': 'silver',

        })

        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 30)
        sheet.set_column('L:L', 30)
        sheet.set_column('M:M', 30)

        # Header of Report data ,titles

        sheet.merge_range("A2:L2", _(self.env.user.company_id.name), header_format)
        sheet.merge_range("A4:L4", _("Product Moves In Details Report"), header_format)
        sheet.merge_range("A6:F6", _(data['form']['date_from'] + " / " + data['form']['date_to']), left_format)
        if not is_all_internal_location:
            sheet.write("A8", _("Location"), left_format)
            sheet.merge_range("B8:F8", _(location_id[1]), left_format)
        sheet.merge_range("A10:B10", _(" "), center_format)
        sheet.write('C10', _('Initial Balance'), center_format)
        sheet.merge_range("D10:E10", _("Incoming"), center_format)
        sheet.merge_range("F10:H10", _("Outgoing"), center_format)
        sheet.write("I10", _("The Balance"), left_format)
        sheet.merge_range("J10:L10", _("Products on The Road"), center_format)
        sheet.write("M10", _("Expected Quantity"), center_format)

        sheet.merge_range("A11:B11", _("Category"), center_format)
        sheet.write("C11", _(""), center_format)
        sheet.write("D11", _("Incoming Shipment"), center_format)
        sheet.write("E11", _("Incoming from Internal Transfer"), center_format)
        sheet.write("F11", _("Out From Transfer"), center_format)
        sheet.write("G11", _("Outgoing Sale"), center_format)
        sheet.write("H11", _("Other Outgoings"), center_format)
        sheet.write("I11", _(" "), center_format)
        sheet.write("J11", _("Purchasing Balance"), center_format)
        sheet.write("K11", _("Incoming From Internal Transfer"), center_format)
        sheet.write("L11", _("outgoing sale"), center_format)
        sheet.write("M11", _(" "), center_format)

        if is_all_internal_location:
            internal_locations = self.env['stock.location'].sudo().search([('usage', '=', 'internal')])
        else:
            internal_locations = self.env['stock.location'].sudo().browse(location_id[0])

        col = 0
        row = 11
        all_total_incoming_initial_balance = 0.0
        all_total_incoming_shipment = 0.0
        all_total_incoming_internal_transfers = 0.0
        all_total_out_from_transfer_balance = 0.0
        all_total_outgoing_sale = 0.0
        all_total_other_outgoings = 0.0
        all_total_incoming_shipment_on_the_road = 0.0
        all_total_incoming_internal_transfers_on_the_road = 0.0
        all_total_outgoing_sales_on_road = 0.0
        all_total_balance = 0.0
        all_total_expected_qty = 0.0

        for location in internal_locations:
            domain = ['|', ('location_id', '=', location.id), ('location_dest_id', '=', location.id),
                      ('state', '=', 'done'), ('date', '>=', date_from), ('date', '<=', date_to)]

            if product_categ_id:
                product_categ_ids = product_categ_obj.sudo().browse([product_categ_id[0]])
            else:
                product_categ_ids = product_categ_obj.sudo().search([])
            if partner_ids:
                domain.append(('picking_id.partner_id', 'in', partner_ids))
            if salesperson_ids:
                domain.append(('picking_id.salesperson_id.id', 'in', salesperson_ids))

            all_move_lines = move_line_obj.sudo().search(domain)
            all_move_lines_category = all_move_lines.sudo().mapped('product_id.categ_id')
            if list(set(all_move_lines_category.ids) & set(product_categ_ids.ids)):
                if is_all_internal_location:
                    sheet.merge_range(row, col, row, col + 12, location.display_name, header_format)
                    row += 1

            for category in product_categ_ids:
                total_incoming_initial_balance = 0.0
                total_incoming_shipment = 0.0
                total_incoming_internal_transfers = 0.0
                total_out_from_transfer_balance = 0.0
                total_outgoing_sale = 0.0
                total_other_outgoings = 0.0
                total_incoming_shipment_on_the_road = 0.0
                total_incoming_internal_transfers_on_the_road = 0.0
                total_outgoing_sales_on_road = 0.0
                total_balance = 0.0
                total_expected_qty = 0.0

                if category.id in all_move_lines_category.ids:

                    category_lines = all_move_lines.sudo().filtered(lambda l: l.product_id.categ_id.id == category.id)
                    category_products = category_lines.sudo().mapped('product_id')

                    sheet.merge_range(row, col, row, col + 12, category.name, left_format)
                    row += 1

                    for product in category_products:
                        product_lines = category_lines.sudo().filtered(lambda l: l.product_id.id == product.id
                                                                                 and l.state == 'done')

                        # Incoming
                        incoming_initial_balance = self.get_initial_balance(location.id, date_from, product)

                        incoming_lines = product_lines.sudo().filtered(lambda l: l.location_dest_id.id == location.id
                                                                                 and (
                                                                                             l.picking_id.picking_type_code == 'incoming')
                                                                                 or l.location_id.usage in ['supplier',
                                                                                                            'inventory'])
                        incoming_shipment = sum(line.product_uom_id._compute_quantity(line.qty_done,
                                                                                      line.product_id.uom_id) for line
                                                in incoming_lines)
                        incoming_internal_transfers = sum(line.product_uom_id._compute_quantity(line.qty_done,
                                                                                                line.product_id.uom_id)
                                                          for line in
                                                          product_lines.sudo().filtered(
                                                              lambda l: l.location_dest_id.id == location.id
                                                                        and (l.location_id.usage in ['transit',
                                                                                                     'internal']
                                                                             or l.picking_id.picking_type_code == 'internal')))

                        # Outgoing (delivery Orders)

                        out_from_transfer_balance = sum(line.product_uom_id._compute_quantity(line.qty_done,
                                                                                              line.product_id.uom_id)
                                                        for line in product_lines.sudo().filtered(
                            lambda l: l.location_id.id == location.id
                                      and (l.location_dest_id.usage in ['transit', 'internal']
                                           and l.picking_id.picking_type_code == 'internal')))
                        outgoing_lines = product_lines.sudo().filtered(lambda l: l.location_id.id == location.id
                                                                                 and (l.location_dest_id.usage in [
                            'customer', 'supplier']
                                                                                      and l.picking_id.picking_type_code == 'outgoing'))
                        outgoing_sale = sum(line.product_uom_id._compute_quantity(line.qty_done,
                                                                                  line.product_id.uom_id) for line in
                                            outgoing_lines)
                        other_outgoings = sum(line.product_uom_id._compute_quantity(line.qty_done,
                                                                                    line.product_id.uom_id) for line in
                                              product_lines.sudo().filtered(lambda l: l.location_id.id == location.id
                                                                                      and l.location_dest_id.usage == 'inventory'))

                        # Incoming products on the Road

                        incoming_lines_on_the_road = move_line_obj.sudo().search(
                            [('location_dest_id', '=', location.id),
                             ('state', 'not in', ['done', 'cancel']),
                             ('date', '>', date_from),
                             ('date', '<=', date_to),
                             ('product_id', '=', product.id),
                             '|',
                             ('location_id.usage', '=', 'supplier'),
                             ('location_id.usage', '=', 'inventory')]
                            )
                        # _logger.debug("///////////////////////incoming_lines_on_the_road %s", incoming_lines_on_the_road)

                        incoming_shipment_on_the_road = sum(line.product_uom_id._compute_quantity(line.product_uom_qty,
                                                                                                  line.product_id.uom_id)
                                                            for line in incoming_lines_on_the_road) \
                            if incoming_lines_on_the_road else 0.0

                        incoming_internal_lines_on_the_road = move_line_obj.sudo().search(
                            [('location_dest_id', '=', location.id),
                             ('state', 'not in', ['done', 'cancel']),
                             ('date', '>', date_from),
                             ('date', '<=', date_to),
                             ('product_id', '=', product.id),
                             '|',
                             ('location_id.usage', '=', 'internal'),
                             ('location_id.usage', '=', 'transit'),
                             ])

                        incoming_internal_transfers_on_the_road = sum(
                            line.product_uom_id._compute_quantity(line.product_uom_qty,
                                                                  line.product_id.uom_id) for line in
                            incoming_internal_lines_on_the_road)
                        outgoing_sales_on_road_lines = move_line_obj.sudo().search([('location_id', '=', location.id),
                                                                                    ('state', 'not in',
                                                                                     ['done', 'cancel']),
                                                                                    ('date', '>', date_from),
                                                                                    ('date', '<=', date_to),
                                                                                    ('product_id', '=', product.id),
                                                                                    ('location_dest_id.usage', 'in',
                                                                                     ['customer', 'supplier']),
                                                                                    (
                                                                                    'picking_id.picking_type_code', '=',
                                                                                    'outgoing'),
                                                                                    ])
                        outgoing_sales_on_road = sum(line.product_uom_id._compute_quantity(line.product_uom_qty,
                                                                                           line.product_id.uom_id) for
                                                     line in outgoing_sales_on_road_lines) \
                            if outgoing_sales_on_road_lines else 0.0

                        the_balance = (incoming_initial_balance + incoming_shipment + incoming_internal_transfers) - \
                                      (out_from_transfer_balance + outgoing_sale + other_outgoings)
                        expected_qty = the_balance + incoming_shipment_on_the_road + incoming_internal_transfers_on_the_road \
                                       - outgoing_sales_on_road

                        sheet.merge_range(row, col, row, col + 1, product.with_context(lang=self.env.user.lang).name)
                        sheet.write(row, col + 2, incoming_initial_balance)
                        sheet.write(row, col + 3, incoming_shipment)
                        sheet.write(row, col + 4, incoming_internal_transfers)
                        sheet.write(row, col + 5, out_from_transfer_balance)
                        sheet.write(row, col + 6, outgoing_sale)
                        sheet.write(row, col + 7, other_outgoings)
                        sheet.write(row, col + 8, the_balance)
                        sheet.write(row, col + 9, incoming_shipment_on_the_road)
                        sheet.write(row, col + 10, incoming_internal_transfers_on_the_road)
                        sheet.write(row, col + 11, outgoing_sales_on_road)
                        sheet.write(row, col + 12, expected_qty)

                        total_incoming_initial_balance += incoming_initial_balance
                        total_incoming_shipment += incoming_shipment
                        total_incoming_internal_transfers += incoming_internal_transfers
                        total_out_from_transfer_balance += out_from_transfer_balance
                        total_outgoing_sale += outgoing_sale
                        total_other_outgoings += other_outgoings
                        total_incoming_shipment_on_the_road += incoming_shipment_on_the_road
                        total_incoming_internal_transfers_on_the_road += incoming_internal_transfers_on_the_road
                        total_outgoing_sales_on_road += outgoing_sales_on_road
                        total_balance += the_balance
                        total_expected_qty += expected_qty
                        row += 1

                    sheet.merge_range(row, col, row, col + 1, _("Total"), center_format)
                    sheet.write(row, col + 2, total_incoming_initial_balance, center_format)
                    sheet.write(row, col + 3, total_incoming_shipment, center_format)
                    sheet.write(row, col + 4, total_incoming_internal_transfers, center_format)
                    sheet.write(row, col + 5, total_out_from_transfer_balance, center_format)
                    sheet.write(row, col + 6, total_outgoing_sale, center_format)
                    sheet.write(row, col + 7, total_other_outgoings, center_format)
                    sheet.write(row, col + 8, total_balance, center_format)
                    sheet.write(row, col + 9, total_incoming_shipment_on_the_road, center_format)
                    sheet.write(row, col + 10, total_incoming_internal_transfers_on_the_road, center_format)
                    sheet.write(row, col + 11, total_outgoing_sales_on_road, center_format)
                    sheet.write(row, col + 12, total_expected_qty, center_format)

                    all_total_incoming_initial_balance += total_incoming_initial_balance
                    all_total_incoming_shipment += total_incoming_shipment
                    all_total_incoming_internal_transfers += total_incoming_internal_transfers
                    all_total_out_from_transfer_balance += total_out_from_transfer_balance
                    all_total_outgoing_sale += total_outgoing_sale
                    all_total_other_outgoings += total_other_outgoings
                    all_total_incoming_shipment_on_the_road += total_incoming_shipment_on_the_road
                    all_total_incoming_internal_transfers_on_the_road += total_incoming_internal_transfers_on_the_road
                    all_total_outgoing_sales_on_road += total_outgoing_sales_on_road
                    all_total_balance += total_balance
                    all_total_expected_qty += total_expected_qty
                    row += 2

            sheet.merge_range(row, col, row, col + 1, _("Total"), center_format)
            sheet.write(row, col + 2, all_total_incoming_initial_balance, center_format)
            sheet.write(row, col + 3, all_total_incoming_shipment, center_format)
            sheet.write(row, col + 4, all_total_incoming_internal_transfers, center_format)
            sheet.write(row, col + 5, all_total_out_from_transfer_balance, center_format)
            sheet.write(row, col + 6, all_total_outgoing_sale, center_format)
            sheet.write(row, col + 7, all_total_other_outgoings, center_format)
            sheet.write(row, col + 8, all_total_balance, center_format)
            sheet.write(row, col + 9, all_total_incoming_shipment_on_the_road, center_format)
            sheet.write(row, col + 10, all_total_incoming_internal_transfers_on_the_road, center_format)
            sheet.write(row, col + 11, all_total_outgoing_sales_on_road, center_format)
            sheet.write(row, col + 12, all_total_expected_qty, center_format)

    def get_initial_balance(self, location, date_to, product):
        result = 0.0

        query = """
            select c.product_id as product_id, c.product_uom_id as product_uom_id, c.location_id as location_id, sum(c.qty) as product_qty 
            from (
            (select a.product_id , a.product_uom_id as product_uom_id, a.location_dest_id as location_id, sum(a.qty_done) as qty 
            from stock_move_line as a where  date < %s and a.location_dest_id = %s and 
            state = 'done' and product_id = %s group by a.product_id, a.product_uom_id, a.location_dest_id) 
            union (select b.product_id ,b.product_uom_id as product_uom_id, b.location_id, (sum(b.qty_done) * -1) as qty 
            from stock_move_line as b where 
            date < %s and b.location_id = %s and state = 'done' and product_id = %s
            group by b.product_id, b.product_uom_id, b.location_id)) 
            as c group by c.product_id, c.product_uom_id, c.location_id order by c.product_id, c.location_id
            """

        self.env.cr.execute(query, (date_to, location, product.id, date_to, location, product.id))
        res_all = self.env.cr.dictfetchall()
        for record in res_all:
            if record['product_uom_id'] == product.uom_id.id:
                result += record['product_qty']
            else:
                uom_obj = self.env['uom.uom'].browse(record['product_uom_id'])
                result += uom_obj._compute_quantity(record['product_qty'],
                                                    product.uom_id)
        return result

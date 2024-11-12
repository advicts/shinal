#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import fields, models, _
import pytz
from pytz import timezone


_logger = logging.getLogger(__name__)


class SingleProductMovesReportXlsx(models.AbstractModel):
    _name = 'report.product_moves_report.single_product_moves_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        """ Draw the excel report """
        move_line_obj = self.env['stock.move.line']
        product_obj = self.env['product.product']
        user_tz = timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        date_from = fields.Datetime.from_string(data['form']['date_from'])
        date_to = fields.Datetime.from_string(data['form']['date_to'])
        product_id = data['form']['product_id']
        location_id = data['form']['location_id']
        partner_ids = data['form']['partner_ids']
        user_objects = data['form']['salesperson_ids']
        salesperson_ids = user_objects
        is_all_internal_location = data['form']['is_all_internal_location']
        date_only_to_dt = user_tz.localize(datetime.combine(date_from, datetime.min.time()))
        user_tz_date_from = date_only_to_dt.astimezone(pytz.utc)
        localize_utc_date_from = user_tz_date_from.replace(tzinfo=None)

        date_from = fields.Datetime.to_string(localize_utc_date_from)
        date_to_only_to_dt = user_tz.localize(datetime.combine(date_to, datetime.max.time()))
        user_tz_date_to = date_to_only_to_dt.astimezone(pytz.utc)
        localize_utc_date_to = user_tz_date_to.replace(tzinfo=None)

        date_to = fields.Datetime.to_string(localize_utc_date_to )
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
            'border': 2,
            'bg_color': 'gray',

        })

        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)

        # Header of Report data ,titles
        product = product_obj.browse(product_id[0])

        sheet.merge_range("A1:F1", _(self.env.user.company_id.name), header_format)
        sheet.merge_range("A3:F3", _(
            "Product Moves In Details Report From ( %s to %s )" % (data['form']['date_from'], data['form']['date_to'])),
                          header_format)
        sheet.write("A5", _("Period"), left_format)
        sheet.merge_range("B5:F5", _(date_from + "-" + date_to), left_format)
        sheet.write("A6", _("Product"), left_format)
        sheet.merge_range("B6:C6", _(product.with_context(lang=self.env.user.lang).name), left_format)
        sheet.write("D6", _("Product Reference"), left_format)
        sheet.merge_range("E6:F6", _(product.default_code), left_format)
        if not is_all_internal_location:
            sheet.write("A7", _("Location"), left_format)
            sheet.merge_range("B7:F7", _(location_id[1]), left_format)
        sheet.write("A9", _("Date"), left_format)
        sheet.write("B9", _(""), left_format)
        sheet.write("C9", _("Operation Type"), left_format)
        sheet.write("D9", _("Reference"), left_format)
        sheet.write("E9", _("Source Document"), left_format)
        sheet.write("F9", _("Sales Price"), left_format)
        sheet.write("G9", _("Unit of Measure"), left_format)
        sheet.write("H9", _("Incoming"), left_format)
        sheet.write("I9", _("Outgoing"), left_format)
        sheet.write("J9", _("Balance"), left_format)
        sheet.write("K9", _("Partner"), left_format)
        sheet.write("L9", _("Salesperson"), left_format)
        if is_all_internal_location:
            sheet.write("M9", _("Location"), left_format)

        if is_all_internal_location:
            internal_locations = self.env['stock.location'].sudo().search([('usage', '=', 'internal')])
        else:
            internal_locations = self.env['stock.location'].sudo().browse(location_id[0])
        col = 0
        row = 10
        total_income = 0.0
        total_outgoing = 0.0
        total_initial_balance = 0.0

        for location in internal_locations:
            domain = ['|', ('location_id', '=', location.id), ('location_dest_id', '=', location.id),
                      ('state', '=', 'done'), ('date', '>=', date_from), ('date', '<=', date_to)]
            if product_id:
                domain.append(('product_id', '=', product_id[0]))
            if partner_ids:
                domain.append(('picking_id.partner_id', 'in', partner_ids))
            if salesperson_ids:
                domain.append(('picking_id.salesperson_id.id', 'in', salesperson_ids))

            all_move_lines = move_line_obj.search(domain, order='date ASC')
            balance = 0.0
            if all_move_lines:
                initial_balance = self.get_initial_balance(location.id, date_from, product)
                sheet.write(row, col, "Opening Balance", left_format)
                sheet.write(row, col + 1, initial_balance)
                balance = initial_balance
                total_initial_balance += balance
                row += 1

            for line in all_move_lines:
                operation_type = ''
                incoming = 0.0
                outgoing = 0.0
                if line.location_dest_id.id == location.id:
                    incoming = line.product_uom_id._compute_quantity(line.qty_done,
                                                                     line.product_id.uom_id)

                    operation_type = 'IN'
                if line.location_id.id == location.id:
                    outgoing = line.product_uom_id._compute_quantity(line.qty_done,
                                                                     line.product_id.uom_id)
                    operation_type = 'OUT'
                balance += incoming - outgoing

                sheet.write(row, col, fields.Datetime.to_string(line.date))
                sheet.write(row, col + 1, '')
                sheet.write(row, col + 2, operation_type)
                sheet.write(row, col + 3, line.reference)
                sheet.write(row, col + 4, line.origin or "")
                sheet.write(row, col + 5, line.sales_price or 0)
                sheet.write(row, col + 6, line.product_id.uom_id.name)
                sheet.write(row, col + 7, incoming)
                sheet.write(row, col + 8, outgoing)
                sheet.write(row, col + 9, balance)
                sheet.write(row, col + 10, line.picking_id.partner_id.display_name or "")
                sheet.write(row, col + 11, line.picking_id.salesperson_id.name or "")

                if is_all_internal_location:
                    sheet.write(row, col + 12, location.display_name)
                total_income += incoming
                total_outgoing += outgoing
                row += 1
        all_total_balance = total_income - total_outgoing + total_initial_balance
        sheet.merge_range(row, col, row, col + 6, _("Total"), left_format)
        sheet.write(row, col + 7, total_income, left_format)
        sheet.write(row, col + 8, total_outgoing, left_format)
        sheet.write(row, col + 9, all_total_balance, left_format)

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






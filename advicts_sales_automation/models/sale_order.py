from odoo import models, fields,api
from odoo.exceptions import UserError
from datetime import timedelta
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
 

class SaleOrder(models.Model):
    _inherit = 'sale.order'
 
    
    def action_create_invoice_bulk(self, limit=None):
        try: 
            sale_orders = self.env['sale.order'].search([
                ('invoice_ids', '=', False),
                 ('company_id', '=', 2),
                ('state', 'in', ['sale', 'done'])
            ], limit=limit , order='id')

            for sale_order in sale_orders: 
                advance_payment_inv = self.env['sale.advance.payment.inv'].create({
                    'sale_order_ids': [(4, sale_order.id)]
                }) 
                advance_payment_inv.create_invoices()
 
                invoice_ids = sale_order.invoice_ids.ids
                if invoice_ids: 
                    sale_invoices = self.env['account.move'].browse(invoice_ids)
                    sale_invoices.action_post()
        except Exception as e:
            _logger.exception("Error creating and posting invoices in bulk: %s", e)

    def action_confirm(self):
        try: 
            isdone=False
            for order in self:
                    for line in order.order_line: 
                        
                        product_template = line.product_id.product_tmpl_id 
                        suppliers_info = product_template.seller_ids
                        if product_template.route_ids.filtered(lambda r: r.id == self.env.ref('stock.route_warehouse0_mto').id) and len(suppliers_info)>0 and not line.vendor_id: 
                            for supplier in suppliers_info: 
                                    supplier.sequence = 1
                                    supplier.price=line.purchase_price 
                            isdone=True
                            
                        elif line.vendor_id : 
                            vendor_info = suppliers_info.filtered(lambda s: s.partner_id == line.vendor_id) 
                            if not vendor_info:
                                supplier_info = self.env['product.supplierinfo'].create({
                                    'partner_id': line.vendor_id.id,
                                    'product_tmpl_id': product_template.id,
                                    'sequence': 1  
                                            })
                            sequence=2
                            for supplier in product_template.seller_ids:
                                if supplier.partner_id == line.vendor_id:
                                    supplier.sequence = 1
                                    supplier.price=line.purchase_price 
                                    isdone=True
                                else:
                                    supplier.sequence = sequence
                                    sequence +=1
    

                    if isdone:
                        temp_order_date = order.date_order
                        super(SaleOrder, self).action_confirm() 
                        order.write({'date_order': temp_order_date})

                        order_reference = order.reference
                        
                        purchase_orders = order._get_purchase_orders()
                        for purchase_order in purchase_orders:
                            purchase_order.write({
                                'payment_reference': order_reference,
                                'date_order': temp_order_date,
                                'date_approve': temp_order_date,
                                'state': 'sent'
                            })

                    else:
                        temp_order_date = order.date_order
                        super(SaleOrder, self).action_confirm() 
                        order.write({'date_order': temp_order_date})
        except:
           pass           
                        
               
    def action_do(self):
        for order in self:
            purchase_orders = order._get_purchase_orders()
            raise UserError(str(purchase_orders))    

    def _prepare_invoice(self):
            invoice_vals = super(SaleOrder, self)._prepare_invoice()
            if self.date_order:
                invoice_date = self.date_order + timedelta(hours=3)
                invoice_vals['invoice_date'] = invoice_date 
            return invoice_vals

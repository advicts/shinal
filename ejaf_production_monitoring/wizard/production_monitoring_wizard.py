from odoo import models, fields
from odoo.exceptions import ValidationError


class ProductionMonitoringWizard(models.TransientModel):
    _name = 'production.monitoring.wizard'

    type_id = fields.Many2one(comodel_name="monitoring.team", string="Type", required=True)

    def add_ticket(self):
        mo_id = self.env['mrp.production'].browse(self._context.get('active_id', False))
        self.env['production.monitoring'].sudo().create({'name': mo_id.name,
                                                         'user_id': self.env.user.id,
                                                         'date': fields.Datetime.today(),
                                                         'type_id': self.type_id.id,
                                                         'mo_id': mo_id.id,
                                                         'product_id': mo_id.product_id.id,
                                                         'quantity': mo_id.product_qty,
                                                         'product_uom': mo_id.product_uom_id.id,

                                                         })


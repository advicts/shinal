from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ProductionMonitoring(models.Model):
    _name = 'production.monitoring'
    _rec_name = 'name'
    _description = 'Production Monitoring'

    name = fields.Char()
    date = fields.Date(string="Date", required=1, default=fields.Date.context_today)
    ref = fields.Char(string='Reference')
    type_id = fields.Many2one(comodel_name="monitoring.team", string="Type", required=True)
    stage_id = fields.Many2one(comodel_name="monitoring.stage", string="stage", default=1, readonly=1,group_expand='_expand_stages', copy=False,)
    mo_id = fields.Many2one(comodel_name="mrp.production", string="stage")
    user_id = fields.Many2one(comodel_name="res.users", string="Assign To", default=lambda self: self.env.user)
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    quantity = fields.Float(string="Quantity")
    product_uom = fields.Many2one('uom.uom', 'Unit of measure')
    is_standardization = fields.Boolean(string="Standardization")
    homogenizer = fields.Boolean(string="Homogenizer")
    cream = fields.Float(string="Cream (Kg) ")
    homogenizer_bar = fields.Float(string="Homogenizer Bar")
    pasteurizer_temperature = fields.Float(string="Pasteurizer Temperature (°C)")
    pasteurizer_flow = fields.Float(string="Pasteurizer Flow (Lt/h)")
    evp_flow = fields.Float(string="EVP flow (Lt/h)")
    milk_inlet_temp = fields.Float(string="Milk Inlet Temp (°C)")
    total_milk = fields.Float(string="Total Milk (Lt) ")
    brix = fields.Float(string="BRIX")
    type_of_ulture = fields.Char(string="Type of Culture ")
    fermentation_temperature = fields.Float(string="Fermentation Temperature (°C)")
    number_of_products = fields.Float(string="Number of products (1750g) ")
    heat_of_room = fields.Float(string="Heat of room (°C) ")
    rest_time = fields.Integer(string="Rest Time (hours)")
    cooling_degree = fields.Float(string="Cooling Degree (°C) ")
    cooling_hours = fields.Integer(string="Cooling Hours (hours)")
    is_confirmed = fields.Boolean('Confirmed', default=False, copy=False)
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    description = fields.Text(string="Description")

    is_final_stage = fields.Boolean(related='stage_id.is_final_stage', string="Final Stage")
    is_first_stage = fields.Boolean(related='stage_id.is_first_stage', string="First Stage")
    display_standardization = fields.Boolean(related='stage_id.display_standardization',
                                             string="Display Standardization")
    display_homogenizer = fields.Boolean(related='stage_id.display_homogenizer', string="Display Homogenizer")
    display_cream = fields.Boolean(related='stage_id.display_cream', string="Display Cream (Kg) ")
    display_homogenizer_bar = fields.Boolean(related='stage_id.display_homogenizer_bar',
                                             string="Display Homogenizer Bar")
    display_pasteurizer_temperature = fields.Boolean(related='stage_id.display_pasteurizer_temperature',
                                                     string="Display Pasteurizer Temperature (°C)")
    display_pasteurizer_flow = fields.Boolean(related='stage_id.display_pasteurizer_flow',
                                              string="Display Pasteurizer Flow (Lt/h)")
    display_evp_flow = fields.Boolean(related='stage_id.display_evp_flow', string="Display EVP Flow (Lt/h)")
    display_milk_inlet_temp = fields.Boolean(related='stage_id.display_milk_inlet_temp',
                                             string="Display Milk Inlet Temp (°C)")
    display_total_milk = fields.Boolean(related='stage_id.display_total_milk', string="Display Total Milk (Lt) ")
    display_brix = fields.Boolean(related='stage_id.display_brix', string="Display BRIX")
    display_type_of_ulture = fields.Boolean(related='stage_id.display_type_of_ulture',
                                            string="Display Type of Culture ")
    display_fermentation_temperature = fields.Boolean(related='stage_id.display_fermentation_temperature',
                                                      string="Display Fermentation Temperature (°C)")
    display_number_of_products = fields.Boolean(related='stage_id.display_number_of_products',
                                                string="Display Number of products (1750g) ")
    display_heat_of_room = fields.Boolean(related='stage_id.display_heat_of_room', string="Display Heat of room (°C) ")
    display_rest_time = fields.Boolean(related='stage_id.display_rest_time', string="Display Rest Time (hours)")
    display_cooling_degree = fields.Boolean(related='stage_id.display_cooling_degree',
                                            string="Display Cooling Degree (°C) ")
    display_cooling_hours = fields.Boolean(related='stage_id.display_cooling_hours',
                                           string="Display Cooling Hours (hours)")

    def _expand_stages(self, states, domain, order):
        stage_ids = self.env['monitoring.stage'].search([])
        return stage_ids

    def unlink(self):
        for rec in self:
            if rec.is_confirmed:
                raise UserError(_('You can not delete a Confirmed Record!.'))
        return super(ProductionMonitoring, self).unlink()

    def action_confirm(self):
        self.write({
            'is_confirmed': True
        })

    @api.model
    def create(self, values):
        res = super(ProductionMonitoring, self).create(values)
        res.write({
            'ref': self.env['ir.sequence'].get('production.monitoring')
        })
        return res

    def open_mrp(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp.mrp_production_action")

        action['domain'] = [('id', '=', self.mo_id.id)]
        return action

    def action_move_to_back_stage(self):
        for lead in self:
            stage_objects = self.env['monitoring.stage'].search([])
            if len(stage_objects) > 0:
                current_stage_index = stage_objects.ids.index(lead.stage_id.id)
                if lead.stage_id != stage_objects[0]:
                    lead.stage_id = stage_objects.ids[current_stage_index - 1]

    def action_move_to_next_stage(self):
        for lead in self:
            stage_objects = self.env['monitoring.stage'].search([])
            if len(stage_objects) > 0:
                current_stage_index = stage_objects.ids.index(lead.stage_id.id)
                if lead.stage_id != stage_objects[-1]:
                    lead.stage_id = stage_objects.ids[current_stage_index + 1]

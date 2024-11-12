# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MonitoringStage(models.Model):
    _name = 'monitoring.stage'
    _rec_name = 'name'
    _description = 'Production Monitoring Stages'

    name = fields.Char()
    is_first_stage = fields.Boolean(string="First Stage")
    is_final_stage = fields.Boolean(string="Final Stage")
    types_ids = fields.Many2many(comodel_name="monitoring.team",  string="Types")

    display_standardization = fields.Boolean(string="Display Standardization")
    display_homogenizer = fields.Boolean(string="Display Homogenizer")
    display_cream = fields.Boolean(string="Display Cream (Kg) ")
    display_homogenizer_bar = fields.Boolean(string="Display Homogenizer Bar")
    display_pasteurizer_temperature = fields.Boolean(string="Display Pasteurizer Temperature (°C)")
    display_pasteurizer_flow = fields.Boolean(string="Display Pasteurizer Flow (Lt/h)")
    display_evp_flow = fields.Boolean(string="Display EVP Flow (Lt/h)")
    display_milk_inlet_temp = fields.Boolean(string="Display Milk Inlet Temp (°C)")
    display_total_milk = fields.Boolean(string="Display Total Milk (Lt) ")
    display_brix = fields.Boolean(string="Display BRIX")
    display_type_of_ulture = fields.Boolean(string="Display Type of Culture ")
    display_fermentation_temperature = fields.Boolean(string="Display Fermentation Temperature (°C)")
    display_number_of_products = fields.Boolean(string="Display Number of products (1750g) ")
    display_heat_of_room = fields.Boolean(string="Display Heat of room (°C) ")
    display_rest_time = fields.Boolean(string="Display Rest Time (hours)")
    display_cooling_degree = fields.Boolean(string="Display Cooling Degree (°C) ")
    display_cooling_hours = fields.Boolean(string="Display Cooling Hours (hours)")


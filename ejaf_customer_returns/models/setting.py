# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = 'res.company'

    customer_return_price_type = fields.Selection([('avg', 'Avg Invoice Price'),
                                                   ('last_invoice', 'Last Invoice Price')])


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_return_price_type = fields.Selection([('avg', 'Avg Invoice Price'),
                                                   ('last_invoice', 'Last Invoice Price')],
                                                  related='company_id.customer_return_price_type',
                                                  readonly=False
                                                  )

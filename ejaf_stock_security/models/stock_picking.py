import logging
from odoo import models, api, fields, exceptions, _
from lxml import etree
import json

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_readonly_user = fields.Boolean(compute='check_user_group')

    def check_user_group(self):
        for record in self:
            record.is_readonly_user = True if self.env.user.has_group(
                'simple_readonly_user.group_simple_readonly_user') else False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(StockPicking, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        group_simple_readonly_user = self.env.user.has_group('simple_readonly_user.group_simple_readonly_user')
        invisible_button = ['action_confirm', 'action_assign', 'button_validate',
                            'action_set_quantities_to_reservation',
                            'do_print_picking', 'do_unreserve', 'button_scrap',
                            'action_toggle_is_locked', 'action_cancel']

        if view_type == 'form' and group_simple_readonly_user:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//button"):
                if node.get('name') in invisible_button:
                    node.set('invisible', '1')
                    modifiers = json.loads(node.get("modifiers"))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res

import logging
from odoo import models, api, fields, exceptions, _
from lxml import etree
import json

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(AccountMove, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        group_simple_readonly_user = self.env.user.has_group('simple_readonly_user.group_simple_readonly_user')
        invisible_button = ['action_post', 'button_draft', 'action_invoice_sent', 'action_register_payment',
                            'preview_invoice','button_cancel','action_reverse','add_vendor_receipt']

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

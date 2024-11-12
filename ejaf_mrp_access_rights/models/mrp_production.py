# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields, exceptions, _
from lxml import etree
import json
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    validated = fields.Boolean(default=False,copy=False)


    def validate_mrp(self):
        for record in self:
            record.validated = True

    def action_confirm(self):
        for mrp in self:
            if not mrp.validated:
                raise ValidationError('You should validate order first.')
        return super(MrpProduction, self).action_confirm()


    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(MrpProduction, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        group_simple_readonly_user = self.env.user.has_group('simple_readonly_user.group_simple_readonly_user')
        invisible_button = ['action_cancel']

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


# -*-	coding:	utf-8	-*-
from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.addons.purchase.models.purchase import PurchaseOrder as ParentPurchase


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    READONLY_STATES = {
        'approvals': [('readonly', True)],
        'amount_limitation': [('readonly', True)],
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    next_approval_level_id = fields.Many2one(string='Next Approval Action')
    last_approved_level_id = fields.Many2one(string='Current Approval Action')

    date_order = fields.Datetime(states=READONLY_STATES)
    partner_id = fields.Many2one(states=READONLY_STATES)
    dest_address_id = fields.Many2one(states=READONLY_STATES)
    currency_id = fields.Many2one(states=READONLY_STATES)
    company_id = fields.Many2one(states=READONLY_STATES)
    order_line = fields.One2many(states=READONLY_STATES)
    picking_type_id = fields.Many2one(states=READONLY_STATES)

    def send_notifications(self):
        if not self.next_approval_level_id:
            return
        users = self.env['res.users']
        partner_ids = []
        for user in self.next_approval_level_id.to_notify_user_ids:
            users += user
        for u in users:
            if u.partner_id.id not in partner_ids:
                partner_ids.append(u.partner_id.id)

        if partner_ids:
            subject = _('Please check for approval')
            body_template = self.env.ref('ejaf_purchase_multi_approval_customization.message_check_po_approval')
            model_description = 'Purchase Order'
            body = body_template._render(
                dict(
                    activity=self,
                    model_description=model_description,
                    access_link=self.env['mail.thread']._notify_get_action_link('view', model='purchase.order',
                                                                                res_id=self),
                ),
                engine='ir.qweb',
                minimal_qcontext=True
            )
            self.message_notify(
                partner_ids=partner_ids,
                body=body,
                subject=subject,
                record_name=self.name,
                model_description=model_description,
                email_layout_xmlid='mail.mail_notification_light',
            )

    @api.depends('last_approved_level_id', 'state')
    def get_next_approval_level(self):
        res = super(PurchaseOrder, self).get_next_approval_level()
        for rec in self:
            if rec._origin and rec.next_approval_level_id and rec.state not in ['cancel']:
                rec.send_notifications()
                for user in rec.next_approval_level_id.user_ids:
                    rec.activity_schedule(
                        'approvals.mail_activity_data_approval',
                        user_id=user.id)
        return res

    def get_approval_levels_list(self):
        self.ensure_one()
        approvals_list = super(PurchaseOrder, self).get_approval_levels_list()
        result_obj = []
        for approval in approvals_list:
            approval['currency_id'] = approval['level'].currency_id
            if approval['level'].currency_id != self.currency_id:
                approval['amount_from'] = approval['level'].currency_id._convert(
                                              approval['level'].amount_from,
                                              self.currency_id,
                                              self.company_id,
                                              self.date_order or fields.Date.today())
            else:
                approval['amount_from'] = approval['level'].amount_from

            if approval['level'].currency_id != self.currency_id:
                approval['amount_to'] = approval['level'].currency_id._convert(
                                              approval['level'].amount_to,
                                              self.currency_id,
                                              self.company_id,
                                              self.date_order or fields.Date.today())
            else:
                approval['amount_to'] = approval['level'].amount_to

            # skip amount approval if limit not reached
            if (not approval['amount_from'] or (approval['amount_from'] and float_compare(self.amount_total, approval['amount_from'], 4) >= 0)):
                result_obj.append(approval)
        return result_obj



ParentPurchase.READONLY_STATES = PurchaseOrder.READONLY_STATES
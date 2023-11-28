from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class SendMsg(models.TransientModel):
    _name = "send.msg"
    _description = "Send massage."

    phone = fields.Char(string="Phone")
    type_message = fields.Selection(
        [("template", "Template"), ("custom", "Custom")]
        , string="Message", default="template")

    # Custom message
    custom_msg = fields.Text(string="")

    # Template message
    template = fields.Many2one("temp.database")
    template_msg = fields.Text(string="", compute="change_msg")

    @api.model
    def default_get(self, fields_list):
        res = super(SendMsg, self).default_get(fields_list)
        return res

    @api.depends("template")
    def change_msg(self):
        for rec in self:
            rec.template_msg = rec.template.template

    def send(self):
        msg = self.custom_msg if self.type_message == 'custom' else self.template_msg

        if not msg:
            raise UserError("You can't send empty message")

        url = "https://api.whatsapp.com/send?phone=%s&text=%s" % (self.phone, msg)

        return {
            "type": "ir.actions.act_url",
            "target": 'new',
            "url": url,
        }
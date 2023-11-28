from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_key = fields.Char(related='company_id.api_key', string="Api Key", store=True, readonly=False)
    date_from = fields.Datetime(related='company_id.date_from',string="Date From", store=True, readonly=False)
    date_to = fields.Datetime(related='company_id.date_to',string="Date to", store=True, readonly=False)


class Company(models.Model):
    _inherit = 'res.company'

    api_key = fields.Char(string="Api Key", store=True)
    date_from = fields.Datetime(string="Date From", store=True)
    date_to = fields.Datetime(string="Date to", store=True)

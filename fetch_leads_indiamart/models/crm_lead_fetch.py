from odoo import fields, models, api, _
import json
from odoo import http
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request
import logging


class Lead(models.Model):
    _inherit = "crm.lead"

    source_of_lead = fields.Selection([
        ('W', 'Direct'),
        ('B', 'Consumed BuyLead'),
        ('P', 'PNS'),
    ], string="Source of Lead")
    lead_date = fields.Datetime(string="Lead date")
    lead_product = fields.Char(string="Lead Product")
    lead_product_cat = fields.Char(string="Lead Product Category")
    lead_enquiry_id = fields.Char(string="Lead Enquiry Id")
    crm_mobile = fields.Char(string="Mobile", related='partner_id.mobile')

    def fetch_lead_from_indiamart(self):
        import requests
        url = "https://mapi.indiamart.com/wservce/crm/crmListing/v2/?glusr_crm_key=%s" % (
                self.env.company.api_key or '')
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        response_json = response.json()
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",response_json)
        if response_json["CODE"] == 200:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!****!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            if response_json["RESPONSE"]:
                for data in response_json["RESPONSE"]:
                    mobile = data['SENDER_MOBILE']
                    state = data['SENDER_STATE']
                    country = data['SENDER_COUNTRY_ISO']
                    if state:
                        state_id = self.env['res.country.state'].sudo().search([('name', '=', state)])
                    if country:
                        country_id = self.env['res.country'].sudo().search([('code', '=', country)])
                    existing = self.env['res.partner'].sudo().search([('mobile', '=', mobile)])
                    partner_data = {
                        'company_name': data['SENDER_COMPANY'],
                        # sender_address : data['SENDER_ADDRESS'],
                        'state_id': state_id.id,
                        'country_id': country_id.id,
                        'city': data['SENDER_CITY'],
                        'zip': data['SENDER_PINCODE'],
                        # 'phone': data['SENDER_MOBILE_ALT'],
                        'phone': data['SENDER_PHONE'],
                        # 'sender_phone_alt': data['SENDER_PHONE_ALT'],
                        'alternative_email': data['SENDER_EMAIL_ALT'],
                        'name': data['SENDER_NAME'],
                        'mobile': data['SENDER_MOBILE'],
                        'email': data['SENDER_EMAIL'],
                    }
                    if existing:
                        partner_id = existing
                    else:
                        partner = self.env['res.partner'].sudo().create(partner_data)
                        partner_id = partner
                    vals = {
                        'lead_enquiry_id': data['UNIQUE_QUERY_ID'],
                        'source_of_lead': data['QUERY_TYPE'],
                        'lead_date': data['QUERY_TIME'],
                        'partner_id': partner_id.id,
                        'name': data['SUBJECT'],
                        'lead_product': data['QUERY_PRODUCT_NAME'],
                        'description': data['QUERY_MESSAGE'],
                        'lead_product_cat': data['QUERY_MCAT_NAME'],
                        'stage_id': self.env.ref('fetch_leads_indiamart.stage_indiamart').id,
                        'user_id': self.env.ref('base.user_admin').id
                    }
                    self.env['crm.lead'].sudo().create(vals)
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!+++++!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

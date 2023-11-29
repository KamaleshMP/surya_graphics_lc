from odoo.exceptions import UserError
from odoo import api, fields, models, _
from num2words import num2words
from datetime import datetime
import calendar


class SaleQuotation(models.Model):
    _name = 'sale.quotation'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sale Quotation"

    name = fields.Char(string='Graphics design')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_type_id = fields.Many2one('sale.quotation', string='Quotation Type')

    # FUNCTION FOR GENERATING SEQUENCE (REFERENCE ID)
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         vals['name'] = self.sudo().env['ir.sequence'].get('offset.printing.quotation') or '/'
    #         res = super(SaleOrder, self).create(vals)
    #     return res

    def consolidated_quantities(self):
        prods = []
        for line in self.order_line:
            # if line.product_id not in [prod['product'] for prod in prods]:
            if line.product_template_id:
                if line.price_subtotal and line.product_uom_qty:
                    tax_price = line.price_subtotal / line.product_uom_qty
                else:
                    tax_price = 0
                prods.append({
                    'product': line.product_template_id,
                    'description': line.name,
                    'hsncode': line.product_template_id.l10n_in_hsn_code,
                    'taxids': line.tax_id.name,
                    'prodqty': line.product_uom_qty,
                    'price': line.price_unit,
                    'measure': line.product_uom.name,
                    'disc': line.discount,
                    'taxprice': tax_price})
        return prods

    def action_confirm(self):
        res = super().action_confirm()
        if self.partner_id.customer_rank and not self.partner_id.customer_id:
            self.partner_id.customer_id = self.env['ir.sequence'].next_by_code('res.partner.customer')

        if self.order_line:
            for i in self.order_line:
                if i.price_unit < 0.00 or i.price_unit == 0.00:
                    raise UserError(_(' unit Price Is zero So Kindly Add Product Unit Price '))
            print('---------------IF------------')
        else:
            print('---------------ELSE---------------')
            raise UserError(_('Kindly Add Product'))
        return res

        # for order in self:
        # for i in self.order_line:
        #     print("==================Second For===========================",i.name)
        #     if len(i.product_template_id) > 0:
        #         print("==================Not Product=================")
        #         if i.price_unit > 0.00:
        #             print('=========================not unit ==============================')
        #             if self.partner_id.customer_rank and not self.partner_id.customer_id:
        #                 self.partner_id.customer_id = self.env['ir.sequence'].next_by_code('res.partner.customer')
        #
        #             self.order_line._validate_analytic_distribution()
        #
        #             for order in self:
        #                 order.validate_taxes_on_sales_order()
        #                 if order.partner_id in order.message_partner_ids:
        #                     continue
        #                 order.message_subscribe([order.partner_id.id])
        #
        #             self.write(self._prepare_confirmation_values())
        #
        #             # Context key 'default_name' is sometimes propagated up to here.
        #             # We don't need it and it creates issues in the creation of linked records.
        #             context = self._context.copy()
        #             context.pop('default_name', None)
        #
        #             self.with_context(context)._action_confirm()
        #             if self.env.user.has_group('sale.group_auto_done_setting'):
        #                 self.action_done()
        #
        #             return True
        #         raise UserError(_(' unit Price Is zero So Kindly Add Product Unit Price '))
        #     raise UserError(_('Kindly Add Product'))


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pan_card_info = fields.Char(string='Pan Card')
    customer_id = fields.Char(string='Customer ID')
    vendor_id = fields.Char(string='Vendor ID')
    cus_tin = fields.Char(string='TIN')
    alternative_email = fields.Char(string='ALT Mail')
    # seq_no = fields.Char(string='Sequence Number')

    # @api.model
    # def create(self, vals):
    #     pass
    # if not self.vendor_id:
    #     partner = super(ResPartner, self).create(vals)
    #     if partner.supplier_rank and not partner.vendor_id:
    #         partner.vendor_id = self.env['ir.sequence'].next_by_code('res.partner.vendor')
    #     return partner


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_id = fields.Char(string='Vendor ID')

    def consolidated_quantities(self):
        prods = []
        for line in self.order_line:
            # if line.product_id not in [prod['product'] for prod in prods]:
            if line.product_id:
                if line.price_subtotal and line.product_qty:
                    tax_price = line.price_subtotal / line.product_qty
                else:
                    tax_price = 0
                prods.append({
                    'product': line.product_id,
                    'description': line.name,
                    'hsncode': line.product_id.l10n_in_hsn_code,
                    'taxids': line.taxes_id.name,
                    'prodqty': line.product_qty,
                    'price': line.price_unit,
                    'measure': line.product_uom.name,
                    # 'disc': line.discount,
                    'taxprice': tax_price})
        return prods

    def button_confirm(self):

        if self.partner_id.supplier_rank and not self.partner_id.vendor_id:
            self.partner_id.vendor_id = self.env['ir.sequence'].next_by_code('res.partner.vendor')

        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])

        return True


class AccountMove(models.Model):
    _inherit = 'account.move'

    def consolidated_quantities(self):
        prods = []
        for line in self.line_ids:
            if line.product_id:
                prods.append({
                    'product': line.product_id.name,
                    'hsn_code': line.product_id.l10n_in_hsn_code,
                    'quantity': line.quantity,
                    'rate': line.price_unit,
                    'amount': line.price_subtotal,
                    'product_uom': line.product_uom_id.name,
                    'taxids': line.tax_ids.name,
                })
        return prods


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def consolidated_quantities(self):
        prods = []
        for line in self.move_ids_without_package:
            if line.product_id:
                prods.append({
                    'product': line.product_id.name,
                    'demand': line.product_uom_qty,
                    'done': line.quantity_done,
                })
        return prods

    def email_split(self, email):
        esplit = email.split(",")
        if esplit:
            current_name = ''
            for each_email in esplit:
                current_name += each_email
            if len(current_name) > 1:
                name = current_name

        return current_name


class Crmlead(models.Model):
    _inherit = 'crm.lead'

    seq_no = fields.Char(string='Sequence')
    sale_types_id = fields.Many2one('sale.quotation', string='Quotation Type')
    mobile = fields.Char(string="Mobile",required='1')

    # CRM LEAD EXISTING FUNCTION INCLUDED HERE AND PASSED ONLY SALE_TYPE_ID TO PLACE INTO QUOTATION
    def _prepare_opportunity_quotation_context(self):
        """ Prepares the context for a new quotation (sale.order) by sharing the values of common fields """
        self.ensure_one()
        quotation_context = {
            'default_opportunity_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_sale_type_id': self.sale_types_id.id,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)]
        }
        if self.team_id:
            quotation_context['default_team_id'] = self.team_id.id
        if self.user_id:
            quotation_context['default_user_id'] = self.user_id.id
        return quotation_context

    # @api.model
    # def create(self, values):
    #     current_month = datetime.now().month
    #     current_year = datetime.now().year
    #     abbr_month = calendar.month_abbr[current_month]
    #     print("------------------------------------------", values)
    #     seq_no = self.sudo().env['ir.sequence'].get('crm.lead') or '/'
    #     values['seq_no'] = str(abbr_month) + "/" + str(current_year) + str(seq_no)
    #     res = super(Crmlead, self).create(values)
    #     return res

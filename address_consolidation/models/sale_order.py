# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
import re


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Legal to be used when no invoice/delivery address is filled
    legal_partner_street = fields.Char('Street')
    legal_partner_street2 = fields.Char('Street2')
    legal_partner_zip = fields.Char('Zip', size=24)
    legal_partner_city = fields.Char('City')
    legal_partner_state_id = fields.Many2one(
        'res.country.state',
        string='State',
    )
    legal_partner_country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    # Historical Invoice address
    invoice_partner_street = fields.Char('Street')
    invoice_partner_street2 = fields.Char('Street2')
    invoice_partner_zip = fields.Char('Zip', size=24)
    invoice_partner_city = fields.Char('City')
    invoice_partner_state_id = fields.Many2one(
        'res.country.state',
        string='State',
    )
    invoice_partner_country_id = fields.Many2one(
        'res.country',
        string='Country',
    )
    # Historical Shipping address
    shipping_partner_street = fields.Char('Street')
    shipping_partner_street2 = fields.Char('Street2')
    shipping_partner_zip = fields.Char('Zip', size=24)
    shipping_partner_city = fields.Char('City')
    shipping_partner_state_id = fields.Many2one(
        'res.country.state',
        string='State',
    )
    shipping_partner_country_id = fields.Many2one(
        'res.country',
        string='Country',
    )

    # Methods to make a method of another class available in the sale order
    # report:
    @api.multi
    def _display_invoice_partner_address(
            self, invoice, without_company=False, context=None):
        return self.env['account.invoice']._display_invoice_partner_address(
            invoice, without_company=False, context=None
        )

    @api.multi
    def _display_picking_partner_address(
            self, picking, without_company=False, context=None):
        return self.env['stock.picking']._display_picking_partner_address(
            picking, without_company=False, context=None
        )

    @api.multi
    def _display_order_partner_address(
            self, order, without_company=False, context=None):
        address_format = order.partner_id.country_id.address_format or \
            "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'street': order.legal_partner_street or '',
            'street2': order.legal_partner_street2 or '',
            'zip': order.legal_partner_zip or '',
            'city': order.legal_partner_city or '',
            'company_name': order.partner_id.name or '',
            'state_code': order.legal_partner_state_id.code or '',
            'state_name': order.legal_partner_state_id.name or '',
            'country_code': order.legal_partner_country_id.code or '',
            'country_name': order.legal_partner_country_id.name or '',
        }
        if without_company:
            args['company_name'] = ''
        elif order.partner_id.parent_id:
            address_format = '%(company_name)s\n' + address_format
        res = address_format % args
        res = re.sub("\n\n|\n", "<br/>", res)
        return res

    @api.multi
    def onchange_partner_id(self, partner_id):
        """Fill invoice and shipping address data,
        or legal if invoice or shipping not set.
        """
        partner_obj = self.env['res.partner']
        res = super(SaleOrder, self).onchange_partner_id(partner_id)
        if partner_id:
            if res['value'].get('partner_invoice_id', False):
                invoice_partner = partner_obj.browse(
                    res['value']['partner_invoice_id']
                )
                res['value'].update({
                    'invoice_partner_street': invoice_partner.street,
                    'invoice_partner_street2': invoice_partner.street2,
                    'invoice_partner_zip': invoice_partner.zip,
                    'invoice_partner_city': invoice_partner.city,
                    'invoice_partner_state_id': invoice_partner.state_id.id,
                    'invoice_partner_country_id':
                        invoice_partner.country_id.id,
                })

            if res['value'].get('partner_shipping_id', False):
                shipping_partner = partner_obj.browse(
                    res['value']['partner_shipping_id']
                )
                res['value'].update({
                    'shipping_partner_street': shipping_partner.street,
                    'shipping_partner_street2': shipping_partner.street2,
                    'shipping_partner_zip': shipping_partner.zip,
                    'shipping_partner_city': shipping_partner.city,
                    'shipping_partner_state_id': shipping_partner.state_id.id,
                    'shipping_partner_country_id':
                        shipping_partner.country_id.id,
                })

            partner = self.env['res.partner'].browse(partner_id)
            res['value'].update({
                'legal_partner_street': partner.street,
                'legal_partner_street2': partner.street2,
                'legal_partner_zip': partner.zip,
                'legal_partner_city': partner.city,
                'legal_partner_state_id': partner.state_id.id,
                'legal_partner_country_id': partner.country_id.id,
            })
        return res

    @api.model
    def _prepare_invoice(self, order, lines, context=None):
        val = super(SaleOrder, self)._prepare_invoice(
            order, lines, context=context
        )
        if order.partner_invoice_id:
            val.update({
                'invoice_partner_street': order.invoice_partner_street,
                'invoice_partner_street2': order.invoice_partner_street2,
                'invoice_partner_zip': order.invoice_partner_zip,
                'invoice_partner_city': order.invoice_partner_city,
                'invoice_partner_state_id': order.invoice_partner_state_id.id,
                'invoice_partner_country_id':
                    order.invoice_partner_country_id.id,
            })

        return val

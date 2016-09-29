# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
import re


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def _picking_assign(
            self, move_ids, procurement_group, location_from, location_to,
            context=None):
        """Assign a picking on the given move_ids, which is a list of move
        supposed to share the same procurement_group, location_from and
        location_to (and company).
        Those attributes are also given as parameters.
        """
        pick_obj = self.env['stock.picking']
        order_obj = self.env['sale.order']
        picks = pick_obj.search([
            ('group_id', '=', procurement_group),
            ('location_id', '=', location_from),
            ('location_dest_id', '=', location_to),
            ('state', 'in', ['draft', 'confirmed', 'waiting'])])
        if picks:
            pick = picks[0]
        else:
            move = self.browse(move_ids)[0]
            values = {
                'origin': move.origin,
                'company_id':
                    move.company_id and move.company_id.id or False,
                'move_type':
                    move.group_id and move.group_id.move_type or 'direct',
                'partner_id': move.partner_id.id or False,
                'picking_type_id':
                    move.picking_type_id and move.picking_type_id.id or False,
            }
            if self._context.get('action_ship_create', None):
                order = self._context['action_ship_create']
                if order.partner_shipping_id:
                    values.update({
                        'shipping_partner_street':
                            order.shipping_partner_street,
                        'shipping_partner_street2':
                            order.shipping_partner_street2,
                        'shipping_partner_zip':
                            order.shipping_partner_zip,
                        'shipping_partner_city':
                            order.shipping_partner_city,
                        'shipping_partner_state_id':
                            order.shipping_partner_state_id.id,
                        'shipping_partner_country_id':
                            order.shipping_partner_country_id.id,
                    })
            pick = pick_obj.create(values)
        move_rec = self.browse(move_ids)
        return move_rec.write({'picking_id': pick.id})

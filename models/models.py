from datetime import datetime

from odoo import models, fields, api, _, api
# from odoo.exceptions import Access
from odoo.exceptions import AccessError

class return_order(models.Model):
    _name = 'return.order'
    _description = 'return_order'

    customer = fields.Many2one(string='customer', comodel_name='res.partner')
    return_date = fields.Date(string='return date', required=True)
    sale_order = fields.Many2many('sale.order', string='sale order')
    status = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')
    seq_num = fields.Char(string='sequence number', default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('seq_num', _('New')) == _('New'):
            vals['seq_num'] = self.env['ir.sequence'].next_by_code('return.order') or _('New')
        res = super(return_order, self).create(vals)
        return res

    def action_draft(self):
        for rec in self:
            rec.status = 'draft'

    def action_confirm(self):
        check = self.env['stock.picking'].search(
            [('picking_type_id', '=', 6), ('partner_id', '=', self.customer.id), ('origin', '=', self.seq_num)])
        if check:

            self.status = 'confirm'


        picking_ship = self.env['stock.picking'].create({
            'partner_id': self.customer.id,
            'picking_type_id': 6,
            'location_id': 1,
            'location_dest_id': 1,
            'origin': self.seq_num
        })

        for rec in self:
            rec.status = 'confirm'

        for rec in self.sale_order:
            for new in rec.order_line:
                # print(new.product_uom_qty)
                self.env['stock.move'].create({
                    'name': new.product_id.id,
                    'product_id': new.product_id.id,
                    'product_uom_qty': new.product_uom_qty,
                    'product_uom': new.product_uom.id,
                    'picking_id': picking_ship.id,
                    'location_id': 8,
                    'location_dest_id': 8,
                    'procure_method': 'make_to_order',
                    'origin': 'SOURCEDOCUMENT',
                    'state': 'draft',
                })
                # move_line_paw = self.env['stock.move'].create({
                #     'product_id': new.product_id.id,
                #     'product_uom_id': new.product_uom_qty,
                #     'picking_id': picking_ship.id,
                #     'qty_done': new.product_uom_qty,
                #     'location_id': 8,
                #     'location_dest_id': 8,
                #     'product_uom_qty': new.product_uom_qty
                #
                # })

            # move_line_paw = self.env['stock.move.line'].create({
            #     'product_id': rec.product_id,
            #     'product_uom_id': self.uom_kg.id,
            #     'picking_id': picking_ship.id,
            #     'qty_done': 5,
            #     'location_id': self.stock_location.id,
            #     'location_dest_id': self.customer_location.id,
            #     'move_ids_without_package': [(0, 0, {
            #         'product_id': self.product_id.id,
            #         'product_uom_qty': self.sel,
            #         'picking_type_id': 1
            #     })]
            # })

    # def action_credit_notes(self):
    #     print('value', self.sale_order)

    def action_credit_notes(self):
        check =self.env['account.move'].search([('move_type', '=', 'out_refund'), ('partner_id','=',self.customer.id)])
        if check:
            raise AccessError('already created note before')
        invoice_line_ids = []
        for rec in self.sale_order.order_line:
            invoice_line_ids.append(
                {
                    'product_id': rec.product_id.id,
                    'quantity': rec.product_uom_qty,
                    'name': rec.name,
                    'price_unit': rec.price_unit,
                }
            )
        refund = self.env['account.move'].create({
            'move_type': 'out_refund',
            # 'journal_id': journal.id,
            'partner_id': self.customer.id,
            'invoice_date': self.return_date,
            'date': self.return_date,
            # 'currency_id': '',
            'invoice_line_ids': invoice_line_ids
        })

        # print("invoices", invoice_line_ids)

        view_id = self.env.ref('account.view_move_form').id
        # ctx = self._context.copy()
        # # ctx = context.copy()
        # ctx['partner_id'] = self.customer.id
        #
        #
        return {
            'name': 'return order Credit Notes ',
            'view_mode': 'form',
             # 'views': [(view_id, 'form')],
            'res_model': 'account.move',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': refund.id,
            # 'target': 'self',


        }

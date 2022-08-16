
from odoo import fields, models, api
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError


class PropertyOffers(models.Model):
    _name = 'estate.property.offer'
    _order = 'price desc'

    price = fields.Float()
    status = fields.Selection([('A', 'Accepted'), ('R', 'Refused')], copy=False)
    partner_id = fields.Many2one(comodel_name='res.partner', required=True, string='Partner')
    property_id = fields.Many2one(comodel_name='estate.property', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_deadline', inverse='_inverse_deadline')
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    _sql_constraints = [('just_positive_price', 'CHECK(price > 0)', 'The offer price must be positive')]

    @api.depends('validity', 'create_date')
    def _compute_deadline(self):
        today_date = date.today()
        for record in self:
            if record.create_date:
                creation_date = fields.Datetime.to_datetime(record.create_date).date()
                record.date_deadline = creation_date + relativedelta(days=+ record.validity)
                # Viendo qué tipo de datos eran los objetos de tipo Date
                # print(type(record.create_date))
            else:
                record.date_deadline = today_date + relativedelta(days=+ record.validity)

    def _inverse_deadline(self):
        today_date = date.today()
        for record in self:
            deadline_date = fields.Date.to_date(record.date_deadline)
            if record.create_date:
                creation_date = fields.Datetime.to_datetime(record.create_date).date()
                record.validity = int((deadline_date - creation_date).days)
                # print(int((deadline_date - creation_date).days))
            else:
                record.validity = int((deadline_date - today_date).days)
                # print(int((deadline_date - today_date).days))

    def action_accept_offer(self):
        for offer in self:
            offer.status = 'A'
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price
            offer.property_id.state = 'OA'
        return True

    def action_reject_offer(self):
        for offer in self:
            self.status = 'R'
            offer.property_id.buyer_id = None
            offer.property_id.selling_price = 0
            offer.property_id.state = 'N'
        return True

    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])

        if property.best_price > vals['price']:
            raise UserError("Offers smaller than the current ones cannot be captured")

        property.state = 'OR'
        return super().create(vals)

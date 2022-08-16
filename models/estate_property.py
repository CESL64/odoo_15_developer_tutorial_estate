
from odoo import models, fields, api
from datetime import date

from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class Estate_Property(models.Model):
    _name = "estate.property"
    _description = "Ejercicio de la documentacion oficial de Odoo"
    _order = 'id desc'

    name = fields.Char(required=True, string='Title')
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(string='Available From', copy=False, default=date(date.today().year, date.today().month + 3, date.today().day))
    expected_price = fields.Float(required=True, default=None)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([('N', 'North'), ('S', 'South'), ('E', 'East'), ('W', 'West')])
    active = fields.Boolean(default=True)
    state = fields.Selection([('N', 'New'), ('OR', 'Offer Received'), ('OA', 'Offer Accepted'), ('S', 'Sold'), ('C', 'Canceled')], default='N', copy=False, required=True, string='Status')
    salesman_id = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user)
    buyer_id = fields.Many2one(comodel_name='res.partner', copy=False)
    property_type_id = fields.Many2one(string='Property Type', comodel_name='estate.property.type')
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id')
    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_offer')

    _sql_constraints = [('not_negative_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive'),
                        ('not_negative_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive')]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            prices = record.mapped('offer_ids.price')

            higher = 0

            for i in range(0, len(prices)):
                if prices[i] > higher:
                    higher = prices[i]

            record.best_price = higher

    @api.onchange('garden')
    def _onchange_garden_defaults(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'N'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    def action_sold_property(self):
        for property in self:
            if property.state is not 'C':
                property.state = 'S'
            else:
                raise UserError('Canceled properties cannot be sold')

        return True

    def action_cancel_property(self):
        for property in self:
            if property.state is not 'S':
                property.state = 'C'
            else:
                raise UserError('Sold properties cannot be canceled')

        return True

    @api.constrains('selling_price', 'expected_price')
    def check_selling_prince(self):
        for record in self:
            min_value = record.expected_price * 0.90
            if float_compare(record.selling_price, min_value, precision_digits=2) == -1:
                if float_is_zero(record.selling_price, 2):
                    return
                else:
                    raise ValidationError('The selling price must be at least 90% of the expected price! You must reduce the expected price if you want to accept this offer.')

    @api.ondelete(at_uninstall=False)
    def unlink_if_property_state(self):
        for property in self:
            if property.state == 'OA' or property.state == 'OR' or property.state == 'S':
                raise UserError('Only new and canceled properties can be deleted.')




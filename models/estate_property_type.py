from odoo import models, fields, api


class PropertyTypes(models.Model):
    _name = 'estate.property.type'
    _description = 'Tipos de propiedades'
    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'The name must be unique')]
    _order = 'sequence, name'

    name = fields.Char(required=True)
    properties_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id')
    sequence = fields.Integer('Sequence', default=1, help="Used to order properties types. Lower is better.")
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_type_id')
    offer_count = fields.Integer(compute='_compute_offer_count')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for property_type in self:
            linked_offers = property_type.mapped('offer_ids')
            property_type.offer_count = len(linked_offers)


from odoo import fields, models

class PropertyTags(models.Model):
    _name = 'estate.property.tag'
    _sql_constraints = [('uniq_name', 'UNIQUE(name)', 'The name of the tag must be unique')]
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer()
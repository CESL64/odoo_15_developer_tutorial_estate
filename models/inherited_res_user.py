from odoo import models, fields, api

class Res_users_inherited(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='salesman_id', domain=['|', ('state', '=', 'N'), ('state', '=', 'OR')])


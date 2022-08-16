{
    'name': "estate",
    'depends': ['base', 'contacts', 'mail'],
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        #'security/security.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tags_view.xml',
        'views/estate_property_offer_view.xml',
        'views/inherited_res_user.xml',
        'views/estate_menus.xml',

     ]
}
# -*- coding: utf-8 -*-
{
    'name': 'Baron Sales Representative',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Baron Sales Representative',
    'description': '''
Torgovik UI
    ''',
    'auto_install': False,
    'application': True,
    'author': 'Soft29',
    'website': 'https://soft29.ru',
    'depends': ['base', 'sale', 'account', 'web', 
                'web_tree_dynamic_colored_field',
                'point_of_sale', 'warning', 'baron_res_partner',
                'web_graph'],
    'data': [
        'templates.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/views.xml',
      #  'views/user_groups.xml',
       # 'views/delivery_period.xml',
      #  'views/sale_order.xml',

       # 'data/data.xml',
    ],
    'qweb': [
    ],
    'js': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'images': ['static/description/main.png'],
    'update_xml': [],
    'installable': True,
    'private_category': True,
    'external_dependencies': {
    },
}

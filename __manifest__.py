# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'return order',
    'version' : '1.2',
    'summary': 'return order',
    'sequence': 10,
    'description': """  """,
    'category': 'orders',
    'website': 'https://www.odoo.com/app/invoicing',
    'images': [],
    'depends': ['sale'],
    'data': [
             'security/ir.model.access.csv',
             'data/sequence.xml',
             'views/return_order.xml',

            ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

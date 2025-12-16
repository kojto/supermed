# -*- coding: utf-8 -*-
{
    'name': "Trinity Commons",
    'summary': "Common utilities and shared functionality for Trinity modules",
    'description': "Module providing common utilities, medical notices, and deputization management for Trinity medical center modules",
    'author': "MG",
    'website': "https://www.trinitymedcenter.com",
    'category': 'Tools',
    'sequence': 4,
    'version': '18.04.07',
    'depends': ['base', 'trinity_examination', 'kojto_landingpage'],
    'data': [
        'security/ir.model.access.csv',
        'views/trinity_medical_notice.xml',
        'views/trinity_commons_buttons.xml',
        'views/trinity_deputization_update.xml',
        'views/trinity_deputization_check.xml'

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

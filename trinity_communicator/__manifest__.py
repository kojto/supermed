# -*- coding: utf-8 -*-
{
    'name': "Trinity Communicator",
    'summary': "Communication and API integration module",
    'description': "Communication module for managing API tokens, requests, communication logs, and external system integrations",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    'category': 'Tools',
    'sequence': 4,
    'version': '18.04.07',
    'depends': ['base', 'web', 'kojto_landingpage', 'trinity_medical_facility'],
    'data': [
        'security/ir.model.access.csv',
        'views/trinity_communicator_views.xml',
        'views/trinity_communicator_buttons.xml',
        'views/trinity_communication_log_views.xml',
        'views/trinity_token_views.xml',
        'views/trinity_requests_views.xml',
        'views/trinity_communicator_menu_items.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

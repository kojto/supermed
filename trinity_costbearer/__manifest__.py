# -*- coding: utf-8 -*-
{
    "name": "Trinity Cost Bearer",
    "summary": "Cost bearer and payment management",
    "description": "Cost bearer management module for managing payment sources, cost allocation, and financial responsibility tracking",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "Tools",
    "sequence": 6,
    "version": "18.04.07",
    "depends": ["base", "kojto_base", "trinity_library", "trinity_medical_facility"],
    "data": [
        "security/ir.model.access.csv",
        "views/trinity_costbearer_views.xml",
        "views/trinity_costbearer_buttons.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

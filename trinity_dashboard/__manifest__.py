# -*- coding: utf-8 -*-
{
    "name": "Trinity Dashboard",
    "summary": "Dashboard and analytics for Trinity medical center",
    "description": "Dashboard module providing analytics, reporting, and overview functionality for Trinity medical center operations",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "Tools",
    "sequence": 9,
    "version": "18.04.07",
    "depends": ["base", "trinity_examination", "kojto_landingpage"],
    "data": [
        "security/ir.model.access.csv",
        "views/trinity_dashboard_views.xml",
        "views/trinity_dashboard_buttons.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

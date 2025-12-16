# -*- coding: utf-8 -*-
{
    "name": "Trinity Landing Page",
    "summary": """Fusion module to remove HR buttons from landing page""",
    "description": """This module removes all HR-related buttons from the Kojto landing page view.""",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "Tools",
    "sequence": 5,
    "version": "18.04.07",
    "depends": ["base", "kojto_landingpage", "kojto_hr", "kojto_assets", "kojto_base", "kojto_commission_codes", "kojto_contacts", "kojto_finance", "kojto_offers", "kojto_contracts"],
    "data": [
        "views/trinity_landingpage_buttons.xml",
        "views/trinity_landingpage_menu_overrides.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

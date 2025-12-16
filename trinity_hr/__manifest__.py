# -*- coding: utf-8 -*-
{
    "name": "Trinity HR",
    "summary": "Human resources integration for Trinity",
    "description": "Human resources module extending KOJTO HR functionality for Trinity medical center",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "Tools",
    "sequence": 9,
    "version": "18.04.07",
    "depends": [
        "base",
        "kojto_hr",
        "kojto_landingpage",
        "trinity_landingpage"
    ],
    "data": [
        "views/trinity_hr_buttons.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

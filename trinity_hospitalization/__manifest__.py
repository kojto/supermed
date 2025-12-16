# -*- coding: utf-8 -*-
{
    "name": "Trinity Hospitalization",
    "summary": "Hospitalization management module",
    "description": "Hospitalization management module for managing patient hospitalizations, incoming hospitalization data, and hospitalization tracking",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "Tools",
    "sequence": 5,
    "version": "18.04.07",
    "depends": ["base", "trinity_examination", "kojto_landingpage", "trinity_nomenclature"],
    "data": [
        "security/ir.model.access.csv",
        "views/trinity_hospitalization_fetch.xml",
        "views/trinity_hospitalization_incoming.xml",
        "views/trinity_hospitalization_buttons.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}


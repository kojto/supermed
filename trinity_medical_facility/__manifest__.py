# -*- coding: utf-8 -*-
{
    "name": "Trinity Medical Facility",
    "summary": "Medical facility and doctor management",
    "description": "Medical facility management module for managing doctors, doctor deductions, external doctors, and facility information",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "Tools",
    "sequence": 5,
    "version": "18.04.07",
    "depends": ["base", "trinity_nomenclature", "kojto_landingpage"],
    "data": [
        "security/ir.model.access.csv",
        "data/trinity_medical_facility_groups.xml",
        "views/trinity_medical_facility_doctors_views.xml",
        "views/trinity_medical_facility_doctors_deductions_views.xml",
        "views/trinity_medical_facility_doctors_external_views.xml",
        "views/trinity_medical_facility_buttons.xml",
        "views/trinity_medical_facility_views.xml",
        "views/trinity_medical_facility_menu_items.xml",
    ],
    'installable': True,
    'application': False,
}

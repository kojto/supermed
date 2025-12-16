# -*- coding: utf-8 -*-
{
    "name": "Trinity Prescription",
    "summary": "Prescription management system",
    "description": "Prescription management module for creating, managing, validating prescriptions, and fetching prescription data",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "Tools",
    "sequence": 4,
    "version": "18.04.07",
    "depends": ["base", "trinity_examination", "kojto_landingpage"],
    "data": [
        "security/ir.model.access.csv",
        "views/trinity_prescription_views.xml",
        "views/trinity_prescription_template_views.xml",
        "views/trinity_prescription_buttons.xml",
        "views/trinity_prescription_fetch_views.xml",
        "views/trinity_prescription_validation_wizard_views.xml",
        "views/trinity_prescription_inherit_patient_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

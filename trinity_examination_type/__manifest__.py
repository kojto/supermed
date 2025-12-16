# -*- coding: utf-8 -*-
{
    "name": "Trinity Examination Type",
    "summary": "Examination type classification and management",
    "description": "Examination type management module for managing different types of medical examinations and their classifications",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "",
    "version": "18.04.07",
    "depends": ["base", "trinity_costbearer", "kojto_landingpage"],
    "data": [
        "security/ir.model.access.csv",
        "views/trinity_examination_type_views.xml",
        "views/trinity_examination_type_buttons.xml",
        "views/action_dropdown_view.xml",
        "data/trinity_examination_type_cron.xml",
    ],
}

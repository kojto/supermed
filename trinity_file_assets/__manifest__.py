{
    "name": "Trinity File Assets",
    "summary": "Shared file assets and styling for Trinity modules",
    "description": "Module providing shared JavaScript, CSS, XML templates, fonts, and styling assets used across all Trinity modules",
    "version": "18.04.07",
    "author": "MG",
    "website": "https://www.trinitymedcenter.com",
    "category": "",
    "depends": ["base", "web"],
    'installable': True,
    'application': True,
    'auto_install': False,
    "data": [
        "static/src/xml/trinity_webclient_templates.xml",
    ],
    'assets': {
        'web.assets_backend': [
        ],
        "web.report_assets_common": [
            "trinity_file_assets/static/src/scss/fonts.scss",
        ],
    },
}

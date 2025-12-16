# -*- coding: utf-8 -*-
{
    'name': "Trinity Financial Reports",
    'summary': "Financial reporting and analysis",
    'description': "Financial reports module for generating financial reports, tracking rejected payments, and financial analysis for Trinity medical center",
    'author': "MG",
    'website': "https://www.trinitymedcenter.com",
    'category': 'Tools',
    'sequence': 9,
    'version': '18.04.07',
    'depends': ['base', 'trinity_examination', 'kojto_landingpage', 'trinity_library'],
    'data': [
        'security/ir.model.access.csv',
        'views/trinity_financial_reports.xml',
        'views/trinity_financial_reports_buttons.xml',
        'views/trinity_rejected_payment.xml',
        'reports/reports_pdf_template.xml',
        'reports/reports_pdf.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

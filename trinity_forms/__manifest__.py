{
    'name': "Trinity Forms",
    'version': '18.04.07',
    'summary': 'Module for managing sheets API integration',
    'category': 'Healthcare',
    'author': 'MG',
    'depends': ['base', 'trinity_medical_facility', 'trinity_nomenclature', 'trinity_medical_facility'],
    'data': [
        'security/ir.model.access.csv',
        'views/trinity_forms_buttons.xml',
        'views/trinity_form_patient_intake_views.xml',
    ],
    'installable': True,
    'application': True,
}

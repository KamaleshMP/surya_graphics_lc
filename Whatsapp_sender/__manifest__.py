# -*- coding: utf-8 -*-

{
    'name': 'Whatsapp sender',
    'version': '1.0.0',
    'author': 'Abdullah Saeed',
    'summary': 'module for send whatsapp message in odoo.',
    'description': """
    Whatsapp sender, is a module for send whatsapp message in odoo, and you can make a lot of templates or you can custom message before sending it.
    """,
    'depends': ['hr'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/wizard.xml",
        "data/type_records.xml",
        "data/temp_records.xml",
        "views/inherit_employees.xml",
        "views/inherit_contact.xml",
        "views/temp_edit.xml",
        "views/type_temp_edit.xml",
        "views/menuitems.xml",
    ],
    'demo': [],
    'images': ['static/description/bannar.gif'],
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

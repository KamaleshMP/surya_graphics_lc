{
    'name': 'sale quotation',
    'version': '16.0',
    'summary': 'sale quotation',
    'sequence': 1,
    'description': """ sale quotation """,
    'author': "AppsComp",
    'website': "http://www.appscomp.com",
    'category': 'sale quotation',
    'depends': [
        'base','sale','purchase'
    ],
    'data': [
         'security/ir.model.access.csv',
         'security/security.xml',
         'views/sale_quotation.xml',
         'reports/purcahse_report.xml',
         'reports/sale_report.xml',
         'reports/tax_invoice.xml',
        # 'reports/delivery_report.xml',
    ],
    'demo': [],
    'qweb': [],
    # 'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
{
    'name': 'Reparaciones de Joyería',
    'version': '1.0',
    'summary': 'Gestión de órdenes de reparación de joyas',
    'author': 'DR',
    'category': 'Operations',
    'depends': ['base', 'product', 'sale', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'security/joyeria_security.xml',
        'views/reparacion_js.xml',
        'data/ir_sequence_data.xml',
        'report/report.xml',  # ← este es el que importa
        'report/report_qrcode_template.xml',
        'static/src/reparacion_form.js',
        #'views/vendedora_qr_views.xml',
        'views/vendedora_views.xml',

        
    
        
    ],
    'installable': True,
    'application': True,
}


from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
import base64
import re  
import qrcode
from datetime import datetime
from io import BytesIO
import uuid

class Reparacion(models.Model):
    _name = 'joyeria.reparacion'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # 👈 Esto habilita el historial
    _description = 'Reparación de Joyería'
    partner_id = fields.Many2one('res.partner', string="Cliente")
    

    name = fields.Char(
        string='Referencia de reparación',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo'
    )


    producto_id = fields.Many2one('joyeria.producto', string='Producto a reparar', required=True)
    cliente_id = fields.Many2one('res.partner', string='Nombre del cliente', required=True)
    nombre_cliente = fields.Char(string='Nombre del cliente', required=False)
    apellido_cliente = fields.Char(string="Apellido del cliente", required=True)
    correo_cliente = fields.Char(string="Correo electrónico")
    telefono = fields.Char(string='Teléfono', required=True)
    direccion_entrega = fields.Char(string='Dirección de entrega')
    vencimiento_garantia = fields.Date(string='Vencimiento de la garantía')
    fecha_entrega = fields.Date(string='Fecha de entrega', tracking=True)
    responsable_id = fields.Many2one('res.users', string="Responsable", default=lambda self: self.env.user, tracking=True)
    fecha_retiro = fields.Datetime(string='Fecha y hora de retiro', tracking=True)
    fecha_recepcion = fields.Datetime(
        string="Fecha de recepción",
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )
    tipo_joya = fields.Selection([
        ('anillo', 'Anillo'),
        ('aros', 'Aros'),
        ('cadena', 'Cadena'),
        ('pulsera', 'Pulsera'),
        ('dije', 'Dije'),
        ('otro', 'Otro')
    ], string='Tipo de joya', required=True)
    metal = fields.Selection([
        ('oro 14k', 'Oro 14K'),
        ('oro 18k rosado', 'Oro 18K Rosado'),
        ('oro 18k amarillo', 'Oro 18K Amarillo'),
        ('oro 18k blanco', 'Oro 18K Blanco'),
        ('oro 18k multi', 'Oro 18K Multi'), 
        ('plata', 'Plata'),
        ('plata con oro', 'Plata con Oro'),
        ('plata con oro 18k', 'Plata con Oro 18K'),
        ('platino', 'Platino'),
        ('otros', 'Otros')
    ], string='Metal Fabricación', required=True, tracking=True)
    
    peso = fields.Selection([
        ('estandar', 'Estándar'),
        ('especial', 'Especial')
    ], string='Tipo de peso', required=True, tracking=True)

    peso_valor = fields.Float(string='Peso', required=True, tracking=True)


    modelo = fields.Char(string='Modelo del Producto',tracking=True)
    servicio = fields.Selection([
        ('reparacion', 'Reparación'),
        ('fabricacion', 'Fabricación')
    ], string='Servicio', required=True, tracking=True)
    solicitud_cliente = fields.Text(string='Solicitud del cliente', tracking=True)
    producto_recibido_por = fields.Char(string='Recibido por', tracking=True)
    #unidades = fields.Selection([
    #    ('gr', 'Gramo'),
     #   ('kg', 'Kilogramo'),
    #], string='Unidades', required=True)

    n_cm_reparacion = fields.Char(string='N° CM Reparación')
    n_cm_fabricacion = fields.Char(string='N° CM Fabricación')
    cantidad = fields.Float(string='Cantidad', required=True, tracking=True)
    local_tienda = fields.Selection([
        ('local 345', 'Local 345'),
        ('local 906', 'Local 906'),
        ('local 584', 'Local 584'),
        ('local 392', 'Local 392'),
        ('local 329', 'Local 329'),
        ('local 325', 'Local 325'),
        ('local 383 online', 'Local 383 Online'),
        ('local maipu', 'Local Maipú'),
        ('local 921', 'Local 921'),
    ], string='Tienda', required=True)
    vendedora_id = fields.Many2one('joyeria.vendedora', string='Recibido por', tracking=True)


    precio_unitario = fields.Float(string='Precio unitario', tracking=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    abono = fields.Float(string='Abono', tracking=True,)
    saldo = fields.Float(string="Saldo", compute='_compute_saldo', store=True)

    express = fields.Boolean(string='Express', tracking=True)
    qr = fields.Binary(string='Código QR', attachment=True)
    notas = fields.Text(string='Notas')
    comentarios = fields.Text(string="Comentarios")

    lineas_operacion_ids = fields.One2many(
        'joyeria.operacion', 'reparacion_id', string='Operaciones')

    estado = fields.Selection([
    ('presupuesto', 'Presupuesto'),
    ('reparado', 'Reparado'),
    ('cancelado', 'Cancelado'),
    ('confirmado', 'Confirmado')
    ], string='Estado', default='presupuesto', tracking=True, compute='_compute_estado', store=True, readonly=False)


    def registrar_retiro(self, qr_escaneado):
        if self.vendedora_id:
            raise ValidationError("Ya se ha registrado una vendedora. No se puede escanear otra.")

        vendedora = self.env['joyeria.vendedora'].search([('name', '=', qr_escaneado)], limit=1)

        if not vendedora:
            raise ValidationError("No se encontró una vendedora con ese QR. Asegúrate de que esté registrada.")

        ahora = fields.Datetime.now()
        self.write({
            'vendedora_id': vendedora.id,
            'fecha_retiro': ahora
        })

        self.message_post(
            body=f"<b>{vendedora.name} (Recibido por)</b> - {ahora.strftime('%d/%m/%Y %H:%M')}",
            message_type="comment"
        )

    


    @api.onchange('fecha_recepcion')
    def _onchange_fecha_recepcion(self):
        if self.fecha_recepcion:
            self.vencimiento_garantia = self.fecha_recepcion + relativedelta(months=3)



    @api.onchange('express')
    def _onchange_express(self):
        if self.express:
            self.fecha_entrega = fields.Date.today()


    @api.onchange('local_tienda')
    def _onchange_local_tienda(self):
        if self.local_tienda:
            self.direccion_entrega = "Paseo Estado 344 (Galería Matte), Santiago Centro, Metro Plaza de Armas"

    @api.onchange('responsable_id')
    def _onchange_responsable_id(self):
        if not self.env.user.has_group('base.group_system'):
            raise UserError("No tienes permisos para modificar el campo 'Responsable'.")

    @api.model
    def create(self, vals):
        if not vals.get('cliente_id'):
            raise ValidationError("Debes seleccionar un cliente antes de crear la orden de reparación.")
        if not vals.get('producto_id'):
            raise ValidationError("Debes seleccionar un producto antes de crear la orden de reparación.")
    
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('joyeria.reparacion') or 'Nuevo'
            
    
        record = super(Reparacion, self).create(vals)

        # Generar QR
        record._generar_codigo_qr()

        

        # Crear mensaje resumen en la bitácora
        mensaje = (
            f"📋 Se ha creado una nueva orden de reparación:\n"
            f"- Cliente: {record.cliente_id.name or ''}\n"
            f"- Teléfono: {record.telefono or ''}\n"
            f"- Producto: {record.producto_id.name or ''}\n"
            f"- Servicio: {record.servicio.capitalize() if record.servicio else ''}\n"
            f"- Estado inicial: {record.estado.capitalize() if record.estado else ''}\n"
            f"- Precio unitario: ${record.precio_unitario or 0}\n"
            f"- Abono inicial: ${record.abono or 0}\n"
        )
        record.message_post(body=mensaje)

        return record
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('joyeria.reparacion') or 'Nuevo'

        record = super(Reparacion, self).create(vals)
        record._generar_codigo_qr()
        return record



    @api.model
    def create(self, vals):
        if not vals.get('vendedora_id'):
            raise ValidationError("Debe escanear una vendedora válida antes de crear la orden.")
        return super(Reparacion, self).create(vals)


    @api.constrains('servicio', 'n_cm_fabricacion', 'n_cm_reparacion')
    def _check_campos_cm_por_servicio(self):
        for record in self:
            if record.servicio == 'fabricacion':
                if record.n_cm_fabricacion and record.n_cm_reparacion:
                    raise ValidationError("Solo se debe completar el campo N° CM Fabricación cuando el servicio es Fabricación.")
                if not record.n_cm_fabricacion:
                    raise ValidationError("Debes completar el campo N° CM Fabricación si el servicio es Fabricación.")
        
            elif record.servicio == 'reparacion':
                if record.n_cm_fabricacion and record.n_cm_reparacion:
                    raise ValidationError("Solo se debe completar el campo N° CM Reparación cuando el servicio es Reparación.")
                if not record.n_cm_reparacion:
                    raise ValidationError("Debes completar el campo N° CM Reparación si el servicio es Reparación.")




    ###Validacion correo
    @api.constrains('correo_cliente')
    def _check_email_format(self):
        for record in self:
            if record.correo_cliente:
                email_regex = r"[^@]+@[^@]+\.[^@]+"
                if not re.match(email_regex, record.correo_cliente):
                    raise ValidationError("El correo electrónico ingresado no es válido.")
                
    ###Validacion teléfono
    @api.constrains('telefono')
    def _check_telefono_format(self):
        for record in self:
            if record.telefono:
                telefono_regex = r"^\+56\d{8,9}$"
                if not re.match(telefono_regex, record.telefono):
                    raise ValidationError("El teléfono debe comenzar con +56 seguido de 8 o 9 dígitos. Ejemplo: +56912345678")



    @api.depends()
    def _compute_estado(self):
        for rec in self:
            if not self.env.user.has_group('joyeria_reparaciones.grupo_gestion_estado_reparacion'):
                rec.estado = rec.estado  # No cambia el valor, pero evita la edición


    @api.depends('cantidad', 'precio_unitario')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.cantidad * rec.precio_unitario

    @api.depends('subtotal', 'abono')
    def _compute_saldo(self):
        for rec in self:
            rec.saldo = rec.subtotal - rec.abono

    @api.model
    def create(self, vals):
        if not vals.get('cliente_id'):
            raise ValidationError("Debes seleccionar un cliente antes de crear la orden de reparación.")
        if not vals.get('producto_id'):
            raise ValidationError("Debes seleccionar un producto antes de crear la orden de reparación.")
        
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('joyeria.reparacion') or 'Nuevo'
        
        record = super(Reparacion, self).create(vals)
        record._generar_codigo_qr()  # Generar QR
        return record



    

    def write(self, vals):
        if 'cliente_id' in vals and not vals.get('cliente_id'):
            raise ValidationError("El campo Cliente no puede quedar vacío.")
        if 'producto_id' in vals and not vals.get('producto_id'):
            raise ValidationError("El campo Producto no puede quedar vacío.")

        res = super(Reparacion, self).write(vals)

        campos_relevantes = [
            'producto_id', 'cliente_id', 'direccion_entrega',
            'vencimiento_garantia', 'estado'
        ]
        if any(campo in vals for campo in campos_relevantes):
            self._generar_codigo_qr()

        return res



    
    
    
    
    
    
    #def copy(self, default=None):
     #   if not self.env.user.has_group('joyeria_reparaciones.grupo_gestion_estado_reparacion'):
      #      raise UserError("No tienes permiso para duplicar órdenes de reparación.")
       # return super(Reparacion, self).copy(default)


    def _generar_codigo_qr(self):
        for record in self:
            if record.name:
                texto_qr = str(record.name).replace("'", "").replace("‘", "").replace("’", "").replace("`", "").replace("´", "").strip()
                qr_img = qrcode.make(texto_qr)
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                record.qr = base64.b64encode(buffer.getvalue())




    def unlink(self):
        if self.env.user.has_group('joyeria_reparaciones.grupo_gestion_estado_reparacion'):
            raise UserError("No tienes permiso para eliminar órdenes de reparación.")
        return super(Reparacion, self).unlink()
    
    


    @api.onchange('cliente_id')
    def _onchange_cliente_id(self):
        if self.cliente_id:
            nombre_completo = self.cliente_id.name or ''
            partes = nombre_completo.split(' ', 1)
            self.nombre_cliente = partes[0] if partes else ''
            self.apellido_cliente = partes[1] if len(partes) > 1 else ''
            self.correo_cliente = self.cliente_id.email or ''
            self.telefono = self.cliente_id.phone or ''
            self.direccion_entrega = self.cliente_id.street or ''



class Operacion(models.Model):
    _name = 'joyeria.operacion'
    _description = 'Línea de operación de reparación'

    reparacion_id = fields.Many2one('joyeria.reparacion', string='Reparación')
    producto_id = fields.Many2one('product.product', string='Producto')
    descripcion = fields.Char(string='Descripción')
    cantidad = fields.Float(string='Cantidad')
    unidad_medida = fields.Char(string='Unidad de medida')
    precio_unitario = fields.Float(string='Precio unitario')


class Vendedora(models.Model):
    _name = 'joyeria.vendedora'
    _description = 'Vendedora'

    name = fields.Char("Nombre completo", required=True)
    codigo_qr = fields.Char("Código QR", readonly=True, copy=False)
    qr_image = fields.Binary("QR", readonly=True)

    @api.model
    def create(self, vals):
        generar_qr = vals.pop('generar_qr', True)  # 👈 solo si lo pasas como True
        if generar_qr and not vals.get('codigo_qr'):
            vals['codigo_qr'] = self.env['ir.sequence'].next_by_code('joyeria.vendedora.qr')
        rec = super().create(vals)
        if generar_qr:
            rec._generar_qr()
        return rec

    def _generar_qr(self):
        import qrcode
        import base64
        from io import BytesIO

        for rec in self:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(rec.name)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            rec.qr_image = base64.b64encode(buffer.getvalue())

            


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            args = ['|', ('codigo_qr', operator, name), ('name', operator, name)] + args
        return self.search(args, limit=limit).name_get()

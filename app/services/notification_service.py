"""
Servicio para gestión de notificaciones a inquilinos
Sistema escalable con plantillas y historial
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from manager.app.services.email_service import email_service
from manager.app.services.payment_service import payment_service
from manager.app.services.apartment_service import apartment_service
from datetime import datetime


class NotificationService:
    """Servicio para gestión de notificaciones"""
    
    DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "notifications.json"
    
    # Plantillas de notificaciones
    TEMPLATES = {
        "payment_reminder": {
            "name": "Recordatorio de Pago Pendiente",
            "subject": "Recordatorio: Pago de Arriendo Pendiente",
            "template": """Estimado/a {tenant_name},

Le recordamos que tiene un pago de arriendo pendiente.

Detalles:
- Apartamento: {apartment_number}
- Valor del arriendo: ${rent_amount:,.0f}
- Días de mora: {days_overdue}
- Próximo vencimiento: {next_due_date}

Por favor, realice el pago correspondiente a la brevedad posible para evitar inconvenientes.

Si ya realizó el pago, por favor ignore este mensaje.

Saludos cordiales,
{sender_name}"""
        },
        "upcoming_due_date": {
            "name": "Recordatorio de Próximo Vencimiento",
            "subject": "Recordatorio: Próximo Vencimiento de Pago",
            "template": """Estimado/a {tenant_name},

Le recordamos que su próximo pago de arriendo vence pronto.

Detalles:
- Apartamento: {apartment_number}
- Valor del arriendo: ${rent_amount:,.0f}
- Fecha de vencimiento: {next_due_date}

Por favor, tenga en cuenta esta fecha para realizar su pago a tiempo.

Saludos cordiales,
{sender_name}"""
        },
        "payment_received": {
            "name": "Confirmación de Pago Recibido",
            "subject": "Confirmación: Pago de Arriendo Recibido",
            "template": """Estimado/a {tenant_name},

Le confirmamos que hemos recibido su pago de arriendo.

Detalles del pago:
- Fecha de pago: {payment_date}
- Monto: ${payment_amount:,.0f}
- Método: {payment_method}
- Apartamento: {apartment_number}

Su estado de cuenta está al día.

Gracias por su puntualidad.

Saludos cordiales,
{sender_name}"""
        },
        "missing_documents": {
            "name": "Recordatorio de Documentos Faltantes",
            "subject": "Recordatorio: Documentos Pendientes",
            "template": """Estimado/a {tenant_name},

Le recordamos que tiene documentos pendientes de entregar.

Apartamento: {apartment_number}

Por favor, complete la documentación requerida a la brevedad posible.

Si ya entregó los documentos, por favor ignore este mensaje.

Saludos cordiales,
{sender_name}"""
        },
        "custom": {
            "name": "Mensaje Personalizado",
            "subject": "Notificación - {custom_subject}",
            "template": """Estimado/a {tenant_name},

{custom_message}

Apartamento: {apartment_number}

Saludos cordiales,
{sender_name}"""
        }
    }
    
    def __init__(self):
        self._ensure_data_file()
        self._load_data()
    
    def _ensure_data_file(self):
        """Asegura que el archivo de datos existe"""
        if not self.DATA_FILE.exists():
            self.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_data(self):
        """Carga los datos de notificaciones"""
        try:
            with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                self.notifications = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.notifications = []
    
    def _save_data(self):
        """Guarda los datos de notificaciones"""
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.notifications, f, ensure_ascii=False, indent=2)
    
    def get_templates(self) -> Dict[str, Dict[str, str]]:
        """Obtiene todas las plantillas disponibles"""
        return self.TEMPLATES.copy()
    
    def get_template(self, template_key: str) -> Optional[Dict[str, str]]:
        """Obtiene una plantilla específica"""
        return self.TEMPLATES.get(template_key)
    
    def get_notification_history(self, tenant_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene el historial de notificaciones"""
        self._load_data()
        if tenant_id:
            return [n for n in self.notifications if n.get("tenant_id") == tenant_id]
        return self.notifications.copy()
    
    def send_notification(
        self,
        tenant: Dict[str, Any],
        template_key: str,
        custom_subject: Optional[str] = None,
        custom_message: Optional[str] = None,
        attach_receipt: bool = False,
        receipt_payment_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Envía una notificación al inquilino
        
        Args:
            tenant: Datos del inquilino
            template_key: Clave de la plantilla a usar
            custom_subject: Asunto personalizado (solo para template "custom")
            custom_message: Mensaje personalizado (solo para template "custom")
            attach_receipt: Si se debe adjuntar un recibo
            receipt_payment_id: ID del pago del recibo a adjuntar
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Verificar que el inquilino tenga email
        tenant_email = tenant.get("email", "").strip()
        if not tenant_email:
            return False, "El inquilino no tiene un email registrado."
        
        # Verificar que el email esté configurado
        if not email_service.is_configured():
            return False, "El sistema de email no está configurado. Por favor configure las credenciales SMTP primero."
        
        # Obtener plantilla
        template = self.get_template(template_key)
        if not template:
            return False, f"Plantilla '{template_key}' no encontrada."
        
        # Preparar datos para la plantilla
        tenant_name = tenant.get("nombre", "Inquilino")
        apartment_id = tenant.get("apartamento")
        apartment_number = "N/A"
        
        if apartment_id:
            try:
                apt = apartment_service.get_apartment_by_id(int(apartment_id))
                if apt and 'number' in apt:
                    apartment_number = apt['number']
            except Exception:
                apartment_number = str(apartment_id)
        
        rent_amount = float(tenant.get("valor_arriendo", 0))
        sender_name = email_service.config.get("sender_name", "Building Manager Pro")
        
        # Calcular información de pagos si es necesario
        payment_service._load_data()
        payments = payment_service.get_payments_by_tenant(tenant.get("id"))
        
        next_due_date = "N/A"
        days_overdue = 0
        
        if payments:
            try:
                # Ordenar pagos por fecha
                payments.sort(key=lambda x: datetime.strptime(x.get("fecha_pago", "01/01/1900"), "%d/%m/%Y"), reverse=True)
                last_payment = payments[0]
                last_payment_date = datetime.strptime(last_payment.get("fecha_pago", "01/01/1900"), "%d/%m/%Y")
                
                # Calcular próximo vencimiento (30 días después del último pago)
                next_due = last_payment_date + timedelta(days=30)
                next_due_date = next_due.strftime("%d/%m/%Y")
                
                # Calcular días de mora
                today = datetime.now()
                if today > next_due:
                    days_overdue = (today - next_due).days
            except Exception:
                pass
        
        # Construir el mensaje
        if template_key == "custom":
            if not custom_subject or not custom_message:
                return False, "Para mensajes personalizados, debe proporcionar asunto y mensaje."
            subject = custom_subject
            body = template["template"].format(
                tenant_name=tenant_name,
                apartment_number=apartment_number,
                sender_name=sender_name,
                custom_message=custom_message
            )
        elif template_key == "payment_received" and receipt_payment_id:
            # Buscar el pago específico
            payment = None
            for p in payments:
                if p.get("id") == receipt_payment_id:
                    payment = p
                    break
            
            if not payment:
                return False, "No se encontró el pago especificado."
            
            subject = template["subject"]
            body = template["template"].format(
                tenant_name=tenant_name,
                apartment_number=apartment_number,
                sender_name=sender_name,
                payment_date=payment.get("fecha_pago", ""),
                payment_amount=float(payment.get("monto", 0)),
                payment_method=payment.get("metodo", "N/A")
            )
        else:
            subject = template["subject"]
            body = template["template"].format(
                tenant_name=tenant_name,
                apartment_number=apartment_number,
                rent_amount=rent_amount,
                sender_name=sender_name,
                next_due_date=next_due_date,
                days_overdue=days_overdue
            )
        
        # Enviar email
        try:
            # Si se debe adjuntar recibo
            pdf_path = None
            if attach_receipt and receipt_payment_id:
                # Buscar el pago y construir ruta del PDF
                payment = None
                for p in payments:
                    if p.get("id") == receipt_payment_id:
                        payment = p
                        break
                
                if payment:
                    # Construir la ruta del PDF usando el mismo formato que se usa al generar el recibo
                    nombre = payment.get("nombre_inquilino", tenant.get("nombre", tenant_name)).replace(" ", "_")
                    fecha = payment.get("fecha_pago", "").replace("/", "-")
                    folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../recibos'))
                    os.makedirs(folder, exist_ok=True)
                    
                    # Primera opción: usar nombre_inquilino del pago
                    pdf_path = os.path.join(folder, f"recibo_pago_{nombre}_{fecha}.pdf")
                    
                    # Si no existe, intentar con el nombre del tenant directamente
                    if not os.path.exists(pdf_path):
                        nombre_tenant = tenant_name.replace(" ", "_")
                        pdf_path_alt = os.path.join(folder, f"recibo_pago_{nombre_tenant}_{fecha}.pdf")
                        if os.path.exists(pdf_path_alt):
                            pdf_path = pdf_path_alt
                    
                    # Si aún no existe, intentar buscar cualquier PDF que coincida con la fecha
                    if not os.path.exists(pdf_path):
                        try:
                            import glob
                            pattern = os.path.join(folder, f"recibo_pago_*_{fecha}.pdf")
                            matches = glob.glob(pattern)
                            if matches:
                                pdf_path = matches[0]
                                for match in matches:
                                    if nombre.lower() in os.path.basename(match).lower():
                                        pdf_path = match
                                        break
                        except Exception:
                            pass
                    
                    # Si el PDF no existe, generarlo automáticamente
                    if not os.path.exists(pdf_path):
                        try:
                            pdf_path = self._generate_receipt_pdf(payment, tenant, pdf_path)
                        except Exception as e:
                            return False, f"No se pudo generar el recibo PDF automáticamente.\n\nError: {str(e)}\n\nPor favor, genere el recibo manualmente usando 'Generar Recibo' antes de enviarlo por email."
            
            # Enviar email simple (sin adjunto) o con adjunto
            if pdf_path and os.path.exists(pdf_path):
                # Enviar email con adjunto usando método personalizado
                success, message = email_service.send_email_with_attachment(
                    recipient_email=tenant_email,
                    recipient_name=tenant_name,
                    subject=subject,
                    body=body,
                    pdf_path=pdf_path
                )
                if not success:
                    return False, message
            else:
                # Enviar email simple sin adjunto
                success, message = email_service.send_simple_email(
                    recipient_email=tenant_email,
                    recipient_name=tenant_name,
                    subject=subject,
                    body=body
                )
                if not success:
                    return False, message
            
            # Guardar en historial
            notification_record = {
                "id": len(self.notifications) + 1,
                "tenant_id": tenant.get("id"),
                "tenant_name": tenant_name,
                "tenant_email": tenant_email,
                "template_key": template_key,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "attached_receipt": attach_receipt and pdf_path is not None
            }
            
            self.notifications.append(notification_record)
            self._save_data()
            
            return True, "Notificación enviada exitosamente."
            
        except Exception as e:
            return False, f"Error al enviar notificación: {str(e)}"
    
    def _generate_receipt_pdf(self, payment: Dict[str, Any], tenant: Dict[str, Any], filepath: str) -> str:
        """Genera el PDF del recibo de pago"""
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from datetime import datetime
        
        # Obtener el número real del apartamento
        apt_display = "N/A"
        apt_id = tenant.get('apartamento', '')
        if apt_id:
            try:
                apt = apartment_service.get_apartment_by_id(int(apt_id))
                if apt and 'number' in apt:
                    apt_display = apt['number']
                else:
                    apt_display = str(apt_id)
            except Exception:
                apt_display = str(apt_id)
        
        # Generar PDF
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Logo placeholder
        c.setFillColorRGB(0.2, 0.4, 0.7)
        c.rect(40, height-80, 80, 40, fill=1)
        c.setFillColorRGB(1,1,1)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height-60, "LOGO")
        
        # Encabezado
        c.setFillColorRGB(0,0,0)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(140, height-60, "RECIBO DE PAGO DE ARRENDAMIENTO")
        c.setFont("Helvetica", 10)
        c.drawString(140, height-80, f"Emitido: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Datos del inquilino y pago
        y = height-120
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Datos del Inquilino:")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Nombre: {payment.get('nombre_inquilino', tenant.get('nombre', ''))}")
        y -= 15
        c.drawString(50, y, f"Apartamento: {apt_display}")
        y -= 15
        c.drawString(50, y, f"Documento: {tenant.get('numero_documento', 'N/A')}")
        y -= 25
        
        # Detalles del pago
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Detalles del Pago:")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Fecha de pago: {payment.get('fecha_pago', '')}")
        y -= 15
        c.drawString(50, y, f"Monto: ${float(payment.get('monto', 0)):,.2f}")
        y -= 15
        c.drawString(50, y, f"Método: {payment.get('metodo', '')}")
        y -= 15
        obs = payment.get('observaciones', '')
        if obs:
            c.drawString(50, y, f"Observaciones: {obs}")
        else:
            c.drawString(50, y, "Observaciones: -")
        
        y -= 40
        
        # Pie de página
        c.setFont("Helvetica", 9)
        c.drawString(40, y, "Este documento es válido como comprobante de pago.")
        
        # Finalizar PDF
        c.save()
        
        return filepath

# Instancia global del servicio
notification_service = NotificationService()

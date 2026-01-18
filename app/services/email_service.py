"""
Servicio para envío de emails con adjuntos PDF
Maneja la configuración SMTP y envío de recibos
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json


class EmailService:
    """Servicio para envío de emails"""
    
    CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "email_config.json"
    
    def __init__(self):
        self._ensure_config_file()
        self._load_config()
    
    def _ensure_config_file(self):
        """Asegura que el archivo de configuración existe"""
        if not self.CONFIG_FILE.exists():
            self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "provider": "gmail",  # gmail, outlook, custom
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email": "",
                    "password": "",  # Se guardará la contraseña de aplicación
                    "sender_name": "Building Manager Pro"
                }, f, ensure_ascii=False, indent=2)
    
    def _load_config(self):
        """Carga la configuración de email"""
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                "provider": "gmail",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "",
                "password": "",
                "sender_name": "Building Manager Pro"
            }
    
    def save_config(self, config_data: Dict[str, Any]) -> bool:
        """Guarda la configuración de email"""
        try:
            # Determinar servidor SMTP según el proveedor
            provider = config_data.get("provider", "gmail")
            if provider == "gmail":
                self.config = {
                    "provider": "gmail",
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email": config_data.get("email", ""),
                    "password": config_data.get("password", ""),
                    "sender_name": config_data.get("sender_name", "Building Manager Pro")
                }
            elif provider == "outlook":
                self.config = {
                    "provider": "outlook",
                    "smtp_server": "smtp-mail.outlook.com",
                    "smtp_port": 587,
                    "email": config_data.get("email", ""),
                    "password": config_data.get("password", ""),
                    "sender_name": config_data.get("sender_name", "Building Manager Pro")
                }
            else:  # custom
                self.config = {
                    "provider": "custom",
                    "smtp_server": config_data.get("smtp_server", ""),
                    "smtp_port": int(config_data.get("smtp_port", 587)),
                    "email": config_data.get("email", ""),
                    "password": config_data.get("password", ""),
                    "sender_name": config_data.get("sender_name", "Building Manager Pro")
                }
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar configuración de email: {str(e)}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de email (sin la contraseña para mostrar)"""
        config_copy = self.config.copy()
        if config_copy.get("password"):
            config_copy["password"] = "********"  # Ocultar contraseña
        return config_copy
    
    def is_configured(self) -> bool:
        """Verifica si el email está configurado"""
        return bool(self.config.get("email") and self.config.get("password"))
    
    def send_receipt_email(self, recipient_email: str, recipient_name: str, 
                          pdf_path: str, payment_date: str, payment_amount: float) -> Tuple[bool, str]:
        """
        Envía un recibo PDF por email
        
        Args:
            recipient_email: Email del destinatario
            recipient_name: Nombre del destinatario
            pdf_path: Ruta completa del archivo PDF
            payment_date: Fecha del pago
            payment_amount: Monto del pago
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.is_configured():
            return False, "El email no está configurado. Por favor configure las credenciales SMTP primero."
        
        if not os.path.exists(pdf_path):
            return False, f"El archivo PDF no existe: {pdf_path}"
        
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = f"{self.config.get('sender_name', 'Building Manager Pro')} <{self.config['email']}>"
            msg['To'] = recipient_email
            msg['Subject'] = f"Recibo de Pago - {payment_date}"
            
            # Cuerpo del mensaje
            body = f"""
Estimado/a {recipient_name},

Adjunto encontrará el recibo de pago correspondiente a la fecha {payment_date}.

Detalles del pago:
- Fecha: {payment_date}
- Monto: ${payment_amount:,.0f}

Este es un mensaje automático generado por Building Manager Pro.

Saludos cordiales,
{self.config.get('sender_name', 'Building Manager Pro')}
            """
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Adjuntar PDF
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(pdf_path)}'
                )
                msg.attach(part)
            
            # Conectar y enviar
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            
            # Limpiar contraseña de espacios y caracteres especiales
            email_clean = self.config['email'].strip()
            password_clean = self.config['password'].strip()
            
            server.login(email_clean, password_clean)
            text = msg.as_string()
            server.sendmail(email_clean, recipient_email, text)
            server.quit()
            
            return True, "Recibo enviado exitosamente por email."
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "Error de autenticación SMTP.\n\n"
            error_msg += "Posibles causas:\n"
            error_msg += "• La contraseña de aplicación es incorrecta\n"
            error_msg += "• Para Gmail: Asegúrese de usar una contraseña de aplicación (no su contraseña normal)\n"
            error_msg += "• Para Gmail: Verifique que tenga 2FA habilitado y genere una nueva contraseña de aplicación\n"
            error_msg += "• El email puede tener espacios o caracteres incorrectos\n\n"
            error_msg += f"Detalles técnicos: {str(e)}"
            return False, error_msg
        except smtplib.SMTPServerDisconnected:
            return False, "No se pudo conectar al servidor SMTP. Verifique su conexión a internet y los datos de servidor."
        except smtplib.SMTPException as e:
            return False, f"Error SMTP: {str(e)}"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error inesperado: {str(e)}"

# Instancia global del servicio
email_service = EmailService()

"""
Generación de recibo de pago en PDF con diseño profesional.
Unificado para uso en PaymentsView, TenantDetailsView y NotificationService.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Colores del recibo (diseño profesional)
HEADER_BG = (0.12, 0.32, 0.55)       # Azul corporativo #1e5290
HEADER_TEXT = (1, 1, 1)
SUBTITLE_GRAY = (0.45, 0.45, 0.45)
SECTION_HEADER = (0.2, 0.2, 0.2)
BODY_TEXT = (0.15, 0.15, 0.15)
LINE_COLOR = (0.88, 0.88, 0.88)
CERT_BG = (0.97, 0.97, 0.97)
SIGN_LABEL = (0.4, 0.4, 0.4)


def _get_apartment_display(tenant: Dict[str, Any]) -> str:
    """Obtiene el número de apartamento para mostrar (no el ID)."""
    from manager.app.services.apartment_service import apartment_service
    apt_id = tenant.get("apartamento", "")
    if not apt_id:
        return "N/A"
    try:
        apt = apartment_service.get_apartment_by_id(int(apt_id))
        if apt and apt.get("number"):
            return str(apt["number"])
        return str(apt_id)
    except Exception:
        return str(apt_id)


def generate_payment_receipt_pdf(
    payment: Dict[str, Any],
    tenant: Dict[str, Any],
    filepath: str,
    logo_path: Optional[str] = None,
) -> str:
    """
    Genera un PDF de recibo de pago con diseño profesional.

    :param payment: dict con nombre_inquilino, fecha_pago, monto, metodo, observaciones
    :param tenant: dict con apartamento, numero_documento, nombre
    :param filepath: ruta donde guardar el PDF
    :param logo_path: ruta opcional a imagen PNG/JPG para el logo (ej. assets/logo.png)
    :return: filepath
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    margin = 50
    content_width = width - 2 * margin

    # --- Encabezado: barra superior ---
    header_h = 72
    c.setFillColorRGB(*HEADER_BG)
    c.rect(0, height - header_h, width, header_h, fill=1, stroke=0)

    # Logo: imagen o placeholder
    logo_left = margin
    logo_w, logo_h = 52, 44
    logo_y = height - header_h + (header_h - logo_h) / 2
    if logo_path is None:
        try:
            from manager.app.paths_config import get_logo_path
            lp = get_logo_path()
            logo_path = str(lp) if lp else None
        except Exception:
            logo_path = None
    if logo_path and Path(logo_path).exists():
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo_path)
            c.drawImage(img, logo_left, logo_y, width=logo_w, height=logo_h, mask="auto")
        except Exception:
            _draw_logo_placeholder(c, logo_left, logo_y, logo_w, logo_h)
    else:
        _draw_logo_placeholder(c, logo_left, logo_y, logo_w, logo_h)

    # Título y fecha en el encabezado
    c.setFillColorRGB(*HEADER_TEXT)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin + logo_w + 20, height - 38, "RECIBO DE PAGO DE ARRENDAMIENTO")
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.drawString(margin + logo_w + 20, height - 58, f"Emitido: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # --- Contenido ---
    y = height - header_h - 32

    # Línea separadora
    c.setStrokeColorRGB(*LINE_COLOR)
    c.setLineWidth(0.5)
    c.line(margin, y, width - margin, y)
    y -= 24

    apt_display = _get_apartment_display(tenant)
    nombre = payment.get("nombre_inquilino") or tenant.get("nombre", "")
    doc = tenant.get("numero_documento", "N/A")
    fecha = payment.get("fecha_pago", "")
    monto = float(payment.get("monto", 0))
    metodo = payment.get("metodo", "")
    obs = (payment.get("observaciones") or "").strip() or "—"

    # Sección: Datos del Inquilino
    c.setFillColorRGB(*SECTION_HEADER)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "DATOS DEL INQUILINO")
    y -= 20
    c.setFillColorRGB(*BODY_TEXT)
    c.setFont("Helvetica", 11)
    c.drawString(margin + 8, y, f"Nombre:        {nombre}")
    y -= 18
    c.drawString(margin + 8, y, f"Apartamento:   {apt_display}")
    y -= 18
    c.drawString(margin + 8, y, f"Documento:     {doc}")
    y -= 28

    # Línea separadora
    c.setStrokeColorRGB(*LINE_COLOR)
    c.line(margin, y, width - margin, y)
    y -= 24

    # Sección: Detalles del Pago
    c.setFillColorRGB(*SECTION_HEADER)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "DETALLES DEL PAGO")
    y -= 20
    c.setFillColorRGB(*BODY_TEXT)
    c.setFont("Helvetica", 11)
    c.drawString(margin + 8, y, f"Fecha de pago:    {fecha}")
    y -= 18
    c.drawString(margin + 8, y, f"Monto:            ${monto:,.2f}")
    y -= 18
    c.drawString(margin + 8, y, f"Método:           {metodo}")
    y -= 18
    c.drawString(margin + 8, y, f"Observaciones:    {obs}")
    y -= 32

    # Caja de certificación
    cert_y = y - 28
    c.setFillColorRGB(*CERT_BG)
    c.setStrokeColorRGB(*LINE_COLOR)
    c.roundRect(margin, cert_y, content_width, 36, 4, fill=1, stroke=1)
    c.setFillColorRGB(*BODY_TEXT)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(margin + 12, cert_y + 14, "Este recibo certifica que el inquilino ha realizado el pago")
    c.drawString(margin + 12, cert_y + 2, "correspondiente al arriendo en la fecha indicada.")
    y = cert_y - 44

    # Línea separadora antes de firmas
    c.setStrokeColorRGB(*LINE_COLOR)
    c.line(margin, y, width - margin, y)
    y -= 28

    # Firmas
    c.setFillColorRGB(*SIGN_LABEL)
    c.setFont("Helvetica", 10)
    sig_line_w = 140
    # Administrador (izquierda)
    c.drawString(margin, y, "Firma administrador:")
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.setLineWidth(0.3)
    c.line(margin, y - 18, margin + sig_line_w, y - 18)
    # Inquilino (derecha)
    right_x = width - margin - sig_line_w - 20
    c.drawString(right_x, y, "Firma inquilino:")
    c.line(right_x, y - 18, right_x + sig_line_w, y - 18)

    c.save()
    return filepath


def _draw_logo_placeholder(c, x, y, w, h):
    """Dibuja un placeholder elegante para el logo."""
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(0.85, 0.85, 0.85)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 3, fill=1, stroke=1)
    c.setFillColorRGB(0.7, 0.75, 0.82)
    c.setFont("Helvetica", 9)
    c.drawString(x + 12, y + h / 2 - 4, "LOGO")

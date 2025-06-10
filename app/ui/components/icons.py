"""
Sistema de iconos profesional para Building Manager
Iconos elegantes usando Unicode y símbolos modernos
"""

class Icons:
    """Colección de iconos profesionales para la aplicación"""
    
    # NAVEGACIÓN PRINCIPAL
    DASHBOARD = "⊞"  # Dashboard principal
    TENANTS = "👥"  # Gestión de inquilinos
    PAYMENTS = "💳"  # Pagos y facturación
    EXPENSES = "📊"  # Gastos y contabilidad
    REPORTS = "📈"  # Reportes y analytics
    SETTINGS = "⚙"  # Configuración
    
    # ACCIONES PRINCIPALES
    ADD = "+"  # Agregar nuevo
    EDIT = "✏"  # Editar
    DELETE = "🗑"  # Eliminar
    SAVE = "💾"  # Guardar
    CANCEL = "✕"  # Cancelar
    SEARCH = "🔍"  # Buscar
    FILTER = "⚡"  # Filtrar
    EXPORT = "📤"  # Exportar
    IMPORT = "📥"  # Importar
    REFRESH = "🔄"  # Actualizar
    
    # ESTADOS Y STATUS
    SUCCESS = "✓"  # Éxito
    WARNING = "⚠"  # Advertencia
    ERROR = "✗"  # Error
    INFO = "ℹ"  # Información
    PENDING = "⏳"  # Pendiente
    COMPLETED = "✅"  # Completado
    ACTIVE = "🟢"  # Activo
    INACTIVE = "🔴"  # Inactivo
    
    # INQUILINOS ESPECÍFICOS
    TENANT_PROFILE = "👤"  # Perfil de inquilino
    TENANT_CONTACT = "📞"  # Contacto
    TENANT_ADDRESS = "🏠"  # Dirección
    TENANT_DOCUMENTS = "📄"  # Documentos
    TENANT_LEASE = "📝"  # Contrato de arrendamiento
    EMERGENCY_CONTACT = "🚨"  # Contacto de emergencia
    
    # PAGOS Y FINANZAS
    PAYMENT_RECEIVED = "💰"  # Pago recibido
    PAYMENT_PENDING = "⏰"  # Pago pendiente
    PAYMENT_OVERDUE = "⚠"  # Pago vencido
    INVOICE = "🧾"  # Factura
    RECEIPT = "🧾"  # Recibo
    BANK = "🏦"  # Banco
    CREDIT_CARD = "💳"  # Tarjeta de crédito
    CASH = "💵"  # Efectivo
    
    # GASTOS Y CONTABILIDAD
    EXPENSE_MAINTENANCE = "🔧"  # Mantenimiento
    EXPENSE_UTILITIES = "⚡"  # Servicios públicos
    EXPENSE_SUPPLIES = "📦"  # Suministros
    EXPENSE_LEGAL = "⚖"  # Legal
    EXPENSE_INSURANCE = "🛡"  # Seguros
    EXPENSE_TAXES = "📋"  # Impuestos
    
    # ARCHIVOS Y DOCUMENTOS
    FILE = "📄"  # Archivo general
    PDF = "📕"  # Archivo PDF
    IMAGE = "🖼"  # Imagen
    FOLDER = "📁"  # Carpeta
    ATTACHMENT = "📎"  # Adjunto
    DOWNLOAD = "⬇"  # Descargar
    UPLOAD = "⬆"  # Subir archivo
    
    # NAVEGACIÓN Y UI
    ARROW_LEFT = "←"  # Flecha izquierda
    ARROW_RIGHT = "→"  # Flecha derecha
    ARROW_UP = "↑"  # Flecha arriba
    ARROW_DOWN = "↓"  # Flecha abajo
    CHEVRON_LEFT = "‹"  # Chevron izquierda
    CHEVRON_RIGHT = "›"  # Chevron derecha
    CHEVRON_UP = "⌃"  # Chevron arriba
    CHEVRON_DOWN = "⌄"  # Chevron abajo
    
    # TIEMPO Y FECHAS
    CALENDAR = "📅"  # Calendario
    CLOCK = "🕐"  # Reloj
    DATE = "📆"  # Fecha
    TIMER = "⏲"  # Temporizador
    
    # COMUNICACIÓN
    EMAIL = "📧"  # Email
    PHONE = "📞"  # Teléfono
    MESSAGE = "💬"  # Mensaje
    NOTIFICATION = "🔔"  # Notificación
    
    # MÉTRICAS Y ANALYTICS
    CHART_BAR = "📊"  # Gráfico de barras
    CHART_LINE = "📈"  # Gráfico de líneas
    CHART_PIE = "🥧"  # Gráfico circular
    TRENDING_UP = "📈"  # Tendencia positiva
    TRENDING_DOWN = "📉"  # Tendencia negativa
    
    # UTILIDADES
    LOCK = "🔒"  # Bloqueado
    UNLOCK = "🔓"  # Desbloqueado
    VISIBLE = "👁"  # Visible
    HIDDEN = "🙈"  # Oculto
    STAR = "⭐"  # Favorito
    HEART = "❤"  # Me gusta
    
    @classmethod
    def get_colored_icon(cls, icon: str, color: str = "#1e40af") -> dict:
        """
        Retorna configuración de icono con color
        Args:
            icon: El icono Unicode
            color: Color hexadecimal
        """
        return {
            "text": icon,
            "color": color,
            "font": ("Segoe UI Symbol", 12, "normal")
        }
    
    @classmethod
    def get_large_icon(cls, icon: str, size: int = 16) -> dict:
        """
        Retorna configuración de icono grande
        Args:
            icon: El icono Unicode  
            size: Tamaño de fuente
        """
        return {
            "text": icon,
            "font": ("Segoe UI Symbol", size, "normal")
        }
    
    @classmethod
    def get_button_icon(cls, icon: str) -> dict:
        """
        Configuración optimizada para iconos en botones
        """
        return {
            "text": f"{icon} ",
            "font": ("Segoe UI", 10, "normal")
        }

class IconThemes:
    """Temas de iconos para diferentes estados"""
    
    PRIMARY = {
        "color": "#1e40af",
        "bg": "#eff6ff"
    }
    
    SUCCESS = {
        "color": "#059669", 
        "bg": "#ecfdf5"
    }
    
    WARNING = {
        "color": "#d97706",
        "bg": "#fffbeb"
    }
    
    ERROR = {
        "color": "#dc2626",
        "bg": "#fef2f2"
    }
    
    NEUTRAL = {
        "color": "#6b7280",
        "bg": "#f9fafb"
    } 
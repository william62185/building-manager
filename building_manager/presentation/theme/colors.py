class MaterialColors:
    # Primary colors
    PRIMARY = "#1976D2"  # Blue 700
    PRIMARY_LIGHT = "#42A5F5"  # Blue 400
    PRIMARY_DARK = "#1565C0"  # Blue 800
    
    # Secondary colors
    SECONDARY = "#00C853"  # Green A700
    SECONDARY_LIGHT = "#69F0AE"  # Green A200
    SECONDARY_DARK = "#00E676"  # Green A400
    
    # Error colors
    ERROR = "#D32F2F"  # Red 700
    ERROR_LIGHT = "#EF5350"  # Red 400
    ERROR_DARK = "#C62828"  # Red 800
    
    # Warning colors
    WARNING = "#FFA000"  # Amber 700
    WARNING_LIGHT = "#FFB300"  # Amber 600
    WARNING_DARK = "#FF8F00"  # Amber 800
    
    # Success colors
    SUCCESS = "#388E3C"  # Green 700
    SUCCESS_LIGHT = "#4CAF50"  # Green 500
    SUCCESS_DARK = "#2E7D32"  # Green 800
    
    # Background colors
    BACKGROUND = "#FFFFFF"
    SURFACE = "#FFFFFF"
    CARD = "#FFFFFF"
    
    # Text colors
    TEXT_PRIMARY = "#212121"  # Grey 900
    TEXT_SECONDARY = "#757575"  # Grey 600
    TEXT_DISABLED = "#9E9E9E"  # Grey 500
    
    # Border colors
    BORDER = "#E0E0E0"  # Grey 300
    DIVIDER = "#EEEEEE"  # Grey 200
    
    # Hover effects
    HOVER_OPACITY = 0.08
    SELECTED_OPACITY = 0.16
    
    @classmethod
    def get_hover_color(cls, base_color: str) -> str:
        """Calcula el color hover basado en el color base"""
        return f"{base_color}{int(cls.HOVER_OPACITY * 255):02x}"
    
    @classmethod
    def get_selected_color(cls, base_color: str) -> str:
        """Calcula el color seleccionado basado en el color base"""
        return f"{base_color}{int(cls.SELECTED_OPACITY * 255):02x}" 
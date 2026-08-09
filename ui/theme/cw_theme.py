"""
CW Transportadora Design System v2.0
Identidade visual profissional para sistema de logística

Inspiração: Linear, Stripe, Attio, Plane
Cor principal: #D32F2F (Vermelho CW)
Modo padrão: Light Premium
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from typing import Dict
from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"


class CWColor(Enum):
    """Paleta de cores CW Transportadora"""
    
    # Brand Colors
    PRIMARY = "#D32F2F"        # Vermelho CW - cor principal
    PRIMARY_DARK = "#B71C1C"   # Vermelho mais escuro
    PRIMARY_LIGHT = "#FFCDD2"  # Vermelho mais claro
    PRIMARY_SOFT = "#FFEBEE"   # Vermelho background suave
    
    # Neutral Colors - Superfícies
    BG_PRIMARY = "#FFFFFF"        # Branco puro - canvas principal
    BG_SECONDARY = "#F9FAFB"     # Cinza muito claro - sidebar, cards
    BG_TERTIARY = "#F3F4F6"      # Cinza claro - inputs, hover
    BG_ELEVATED = "#FFFFFF"      # Branco - cards elevados
    BG_OVERLAY = "#E5E7EB"       # Cinza médio - hover states
    BG_SURFACE = "#F9FAFB"       # Surface intermediária
    
    # Neutral Colors - Texto
    TEXT_PRIMARY = "#111827"     # Quase preto - texto principal
    TEXT_SECONDARY = "#6B7280"   # Cinza médio - texto secundário
    TEXT_TERTIARY = "#9CA3AF"    # Cinza claro - texto terciário
    TEXT_DISABLED = "#D1D5DB"     # Cinza muito claro - desabilitado
    TEXT_INVERTED = "#FFFFFF"    # Branco - texto invertido
    
    # Neutral Colors - Bordas
    BORDER_SUBTLE = "#E5E7EB"    # Cinza muito claro - borda sutil
    BORDER_DEFAULT = "#D1D5DB"   # Cinza claro - borda padrão
    BORDER_STRONG = "#9CA3AF"    # Cinza médio - borda forte
    BORDER_FOCUS = "#D32F2F"     # Vermelho CW - borda foco
    
    # Semantic Colors
    SUCCESS = "#10B981"         # Verde esmeralda
    SUCCESS_SOFT = "#D1FAE5"    # Verde background suave
    WARNING = "#F59E0B"         # Laranja âmbar
    WARNING_SOFT = "#FEF3C7"    # Laranja background suave
    ERROR = "#EF4444"           # Vermelho erro
    ERROR_SOFT = "#FEE2E2"      # Vermelho background suave
    INFO = "#3B82F6"            # Azul info
    INFO_SOFT = "#DBEAFE"       # Azul background suave


class CWTypography:
    """Sistema de tipografia CW - Fonte Inter"""
    
    # Font Family
    FONT_FAMILY = "'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
    FONT_FAMILY_QT = "Inter"
    FONT_FAMILY_MONO = "'JetBrains Mono', 'Fira Code', Consolas, monospace"
    
    # Font Sizes (escala baseada em 4px)
    FONT_SIZE_XS = 11
    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_2XL = 24
    FONT_SIZE_3XL = 32
    FONT_SIZE_4XL = 48
    FONT_SIZE_5XL = 64
    
    # Font Weights
    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700
    
    # Line Heights
    LINE_HEIGHT_TIGHT = 1.1    # Headings
    LINE_HEIGHT_NORMAL = 1.5   # Body
    LINE_HEIGHT_RELAXED = 1.6  # Long text
    
    # Letter Spacing
    LETTER_SPACING_TIGHT = -0.02
    LETTER_SPACING_NORMAL = -0.01
    LETTER_SPACING_WIDE = 0


class CWSpacing:
    """Sistema de espaçamento CW - Grid 4px"""
    
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    _2XL = 32
    _3XL = 48
    _4XL = 64
    _5XL = 96


class CWRadius:
    """Sistema de border radius CW - Profissional"""
    
    XS = 4     # Badges, tags
    SM = 6     # Small inputs
    MD = 8     # Inputs, buttons
    LG = 10    # Cards
    XL = 12    # Dialogs
    _2XL = 16  # Large cards
    FULL = 9999


class CWShadow:
    """Sistema de sombras CW - Sutis e profissionais"""
    
    NONE = "none"
    SM = "0 1px 2px rgba(0, 0, 0, 0.05)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.04)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.07), 0 10px 10px -5px rgba(0, 0, 0, 0.03)"
    
    # Shadow with brand color
    BRAND = "0 4px 12px rgba(211, 47, 47, 0.15)"


class CWTheme:
    """Gerenciador de tema CW Transportadora - Dark Mode Premium"""
    
    def __init__(self, mode: ThemeMode = ThemeMode.DARK):
        self.mode = mode
        self.colors = self._build_colors()
        self.typography = CWTypography
        self.spacing = CWSpacing
        self.radius = CWRadius
        self.shadow = CWShadow
    
    def _build_colors(self) -> Dict[str, str]:
        """Constrói dicionário de cores baseado no modo - Dark Mode CW"""
        return {
            # Brand - CW Red
            'primary': "#D32F2F",              # CW Red - cor principal
            'primary_dark': "#B71C1C",         # Vermelho mais escuro
            'primary_light': "#FFCDD2",        # Vermelho mais claro
            'primary_soft': "#3D1A1A",         # Vermelho background suave (dark)
            'brand': "#D32F2F",                # Alias para primary
            'brand_hover': "#E53935",          # Brand hover
            'brand_active': "#C62828",         # Brand active
            'brand_glow': "rgba(211, 47, 47, 0.25)",  # Brand glow
            
            # Backgrounds - Dark Sophisticated Palette
            'bg_primary': "#0B0D10",           # Background principal
            'bg_secondary': "#101318",          # Background secundário
            'bg_tertiary': "#15191E",           # Cards
            'bg_elevated': "#1A1F25",          # Cards elevados
            'bg_overlay': "#262C33",           # Bordas
            'bg_surface': "#101318",           # Surface intermediária
            
            # Sidebar
            'sidebar_bg': "#0D1014",           # Sidebar background
            'sidebar_gradient_top': "#0D1014",
            'sidebar_gradient_bottom': "#0D1014",
            'sidebar_text': "#F5F7FA",
            'sidebar_text_muted': "#6F7883",
            'sidebar_active': "#D32F2F",
            'sidebar_active_bg': "#3D1A1A",
            'sidebar_hover': "#1A1F25",
            'sidebar_border': "#1A1F25",
            
            # Header
            'header_bg': "#101318",
            'header_border': "#1A1F25",
            
            # Cards
            'card_bg': "#15191E",
            'card_border': "#1A1F25",
            'card_hover': "#1A1F25",
            
            # Tables
            'table_header_bg': "#101318",
            'table_header_text': "#A7AFB8",
            'table_row_even': "#0B0D10",
            'table_row_odd': "#101318",
            'table_row_hover': "#15191E",
            'table_row_selected': "#3D1A1A",
            
            # Text - Dark Mode Hierarchy
            'text_primary': "#F5F7FA",         # Texto principal
            'text_secondary': "#A7AFB8",       # Texto secundário
            'text_tertiary': "#6F7883",        # Texto terciário
            'text_disabled': "#4A5159",        # Texto desabilitado
            'text_inverted': "#0B0D10",        # Texto invertido
            
            # Borders
            'border_subtle': "#1A1F25",        # Borda sutil
            'border_default': "#262C33",       # Borda padrão
            'border_strong': "#3A424B",        # Borda forte
            'border_focus': "#D32F2F",         # Borda foco (CW Red)
            
            # Semantic Colors
            'success': "#22C55E",              # Success
            'success_soft': "#1A3D28",         # Success background suave
            'warning': "#F59E0B",              # Warning
            'warning_soft': "#3D2E1A",         # Warning background suave
            'error': "#EF4444",                # Danger
            'error_soft': "#3D1A1A",           # Error background suave
            'info': "#3B82F6",                 # Info
            'info_soft': "#1A2D3D",            # Info background suave
            
            # Chart Colors
            'chart_1': "#3B82F6",              # Blue
            'chart_2': "#22C55E",              # Green
            'chart_3': "#D32F2F",              # Red/Brand
            'chart_4': "#F59E0B",              # Amber
            'chart_5': "#8B5CF6",              # Violet
            'chart_6': "#06B6D4",              # Cyan
            'chart_7': "#EC4899",              # Pink
            'chart_8': "#6366F1",              # Indigo
            'chart_bg': "#0B0D10",
            'chart_grid': "#1A1F25",
            'chart_text': "#A7AFB8",
        }
    
    def get_font(self, size: int, bold: bool = False) -> QFont:
        """Retorna QFont configurado"""
        font = QFont(self.typography.FONT_FAMILY_QT, size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        else:
            font.setWeight(QFont.Weight.Normal)
        return font
    
    def set_mode(self, mode: ThemeMode):
        """Altera o modo do tema"""
        self.mode = mode
        self.colors = self._build_colors()


# Instância global do tema CW - Dark Mode por padrão
cw_theme = CWTheme(mode=ThemeMode.DARK)

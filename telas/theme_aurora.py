"""
Aurora Design System v1.0 - CW Transportadora
Identidade visual premium inspirada em Linear, Stripe, Notion, Vercel

Conceitos:
- Glassmorphism sutil com bordas ultra-finas
- Gradientes coloridos em vez de cores sólidas
- Sombras coloridas (glow effects)
- Tipografia Inter com tracking refinado
- Animações fluidas e micro-interações
- Paleta escura premium com vermelho institucional da CW
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont
from typing import Dict
from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"


class AccentColor(Enum):
    AURORA = "aurora"         # Primary gradient (CW red)
    OCEAN = "ocean"           # Secondary (teal-cyan)
    SUNSET = "sunset"         # Warm (orange-pink)
    FOREST = "forest"         # Success (emerald-green)
    COSMOS = "cosmos"         # Info (blue-purple)
    EMBER = "ember"           # Warning (amber-orange)
    CRIMSON = "crimson"       # Error (red-rose)
    NEON = "neon"             # Accent (cyan-lime)
    
    # Backward compatibility aliases for old theme system
    BRAND = "aurora"          # Maps to AURORA
    EMERALD = "forest"        # Maps to FOREST
    SKY = "ocean"            # Maps to OCEAN
    AMBER = "ember"           # Maps to EMBER
    VIOLET = "aurora"         # Maps to AURORA
    CYAN = "ocean"            # Maps to OCEAN
    ROSE = "crimson"          # Maps to CRIMSON


class ThemeTokens:
    """Design tokens - 4px grid system com refinamentos premium."""

    # Tipografia
    FONT_FAMILY = "'Inter', 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif"
    FONT_FAMILY_QT = "Inter"
    FONT_FAMILY_DISPLAY = "'Inter', 'Segoe UI', sans-serif"
    FONT_FAMILY_MONO = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace"

    # Tamanhos refinados estilo Linear
    FONT_SIZE_XS = 11
    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_2XL = 24
    FONT_SIZE_3XL = 32
    FONT_SIZE_4XL = 48

    # Font weights refinados estilo Linear
    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700

    # Letter-spacing (tracking) refinado estilo Linear
    LETTER_SPACING_TIGHT = -0.02  # Headings
    LETTER_SPACING_NORMAL = -0.01  # Body
    LETTER_SPACING_WIDE = 0  # Default
    LETTER_SPACING_WIDER = 0.05  # Uppercase

    # Line-height refinado estilo Linear
    LINE_HEIGHT_TIGHT = 1.1  # Headings
    LINE_HEIGHT_NORMAL = 1.5  # Body
    LINE_HEIGHT_RELAXED = 1.6  # Long text

    # Espaçamentos (4px grid)
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_2XL = 32
    SPACING_3XL = 48
    SPACING_4XL = 64
    SPACING_5XL = 96

    # Bordas - mais arredondadas para visual moderno
    RADIUS_XS = 4
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_XL = 20
    RADIUS_2XL = 24
    RADIUS_3XL = 32
    RADIUS_FULL = 9999

    # Sombras refinadas estilo Linear (mais sutis e elegantes)
    SHADOW_SM = "0 1px 2px rgba(0, 0, 0, 0.04)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.03)"
    SHADOW_AURORA = "0 0 20px rgba(99, 102, 241, 0.12)"
    SHADOW_OCEAN = "0 0 20px rgba(20, 184, 166, 0.12)"
    SHADOW_SUNSET = "0 0 20px rgba(249, 115, 22, 0.12)"

    # Opacity system refinado estilo Linear
    OPACITY_DISABLED = 0.4
    OPACITY_TERTIARY = 0.6
    OPACITY_SECONDARY = 0.8
    OPACITY_PRIMARY = 1.0

    # Elevation system refinado estilo Linear
    ELEVATION_NONE = 0
    ELEVATION_SM = 1
    ELEVATION_MD = 2
    ELEVATION_LG = 3
    ELEVATION_XL = 4


class AuroraDarkTheme:
    """Tema Aurora Dark Premium - Paleta inspirada em Linear/Stripe/Notion."""

    # Superfícies - GitHub Dark Theme inspirado
    BG_PRIMARY = "#0D1117"        # Canvas principal - fundo principal
    BG_SECONDARY = "#161B22"      # Sidebar, painéis fixos - cards
    BG_TERTIARY = "#21262D"       # Inputs, campos - hover states
    BG_ELEVATED = "#1C2128"       # Cards, dropdowns
    BG_OVERLAY = "#30363D"        # Hover states
    BG_SURFACE = "#161B22"        # Surface intermediária
    BG_GLASS = "rgba(22, 27, 34, 0.8)"  # Glassmorphism

    # Texto - contraste refinado
    TEXT_PRIMARY = "#FFFFFF"      # Branco puro
    TEXT_SECONDARY = "#9CA3AF"    # Cinza médio
    TEXT_TERTIARY = "#6B7280"     # Cinza escuro
    TEXT_DISABLED = "#484F58"     # Desabilitado
    TEXT_INVERTED = "#0D1117"

    # Bordas - ultra-finas e sutis
    BORDER_SUBTLE = "rgba(48, 54, 61, 0.5)"
    BORDER_DEFAULT = "rgba(48, 54, 61, 0.8)"
    BORDER_STRONG = "rgba(240, 246, 252, 0.15)"
    BORDER_HOVER = "rgba(240, 246, 252, 0.2)"
    BORDER_FOCUS = "rgba(211, 47, 47, 0.5)"

    # Aurora Gradient (Primary) - vermelho CW premium
    AURORA_START = "#D32F2F"
    AURORA_END = "#E53935"
    AURORA = "#D32F2F"
    AURORA_HOVER = "#E53935"
    AURORA_ACTIVE = "#C62828"
    AURORA_SOFT = "rgba(211, 47, 47, 0.15)"
    AURORA_GLOW = "rgba(211, 47, 47, 0.3)"
    AURORA_GRADIENT = "linear-gradient(135deg, #D32F2F 0%, #E53935 100%)"

    # Ocean Gradient (Secondary) - teal-cyan premium
    OCEAN_START = "#0EA5E9"
    OCEAN_END = "#38BDF8"
    OCEAN = "#0284C7"
    OCEAN_HOVER = "#0EA5E9"
    OCEAN_ACTIVE = "#0369A1"
    OCEAN_SOFT = "rgba(2, 132, 199, 0.15)"
    OCEAN_GLOW = "rgba(14, 165, 233, 0.3)"
    OCEAN_GRADIENT = "linear-gradient(135deg, #0EA5E9 0%, #38BDF8 100%)"

    # Sunset Gradient (Warm) - orange-pink premium
    SUNSET_START = "#F97316"
    SUNSET_END = "#FB923C"
    SUNSET = "#EA580C"
    SUNSET_HOVER = "#F97316"
    SUNSET_ACTIVE = "#C2410C"
    SUNSET_SOFT = "rgba(234, 88, 12, 0.15)"
    SUNSET_GLOW = "rgba(249, 115, 22, 0.3)"
    SUNSET_GRADIENT = "linear-gradient(135deg, #F97316 0%, #FB923C 100%)"

    # Forest Gradient (Success) - emerald-green premium
    FOREST_START = "#22C55E"
    FOREST_END = "#4ADE80"
    FOREST = "#16A34A"
    FOREST_HOVER = "#22C55E"
    FOREST_ACTIVE = "#15803D"
    FOREST_SOFT = "rgba(22, 99, 74, 0.15)"
    FOREST_GLOW = "rgba(34, 197, 94, 0.3)"
    FOREST_GRADIENT = "linear-gradient(135deg, #22C55E 0%, #4ADE80 100%)"

    # Cosmos Gradient (Info) - blue-purple premium
    COSMOS_START = "#3B82F6"
    COSMOS_END = "#60A5FA"
    COSMOS = "#2563EB"
    COSMOS_HOVER = "#3B82F6"
    COSMOS_ACTIVE = "#1D4ED8"
    COSMOS_SOFT = "rgba(37, 99, 235, 0.15)"
    COSMOS_GLOW = "rgba(59, 130, 246, 0.3)"
    COSMOS_GRADIENT = "linear-gradient(135deg, #3B82F6 0%, #38BDF8 100%)"

    # Ember Gradient (Warning) - amber-orange premium
    EMBER_START = "#F59E0B"
    EMBER_END = "#FBBF24"
    EMBER = "#D97706"
    EMBER_HOVER = "#F59E0B"
    EMBER_ACTIVE = "#B45309"
    EMBER_SOFT = "rgba(217, 119, 6, 0.15)"
    EMBER_GLOW = "rgba(245, 158, 11, 0.3)"
    EMBER_GRADIENT = "linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)"

    # Crimson Gradient (Error) - red-rose premium
    CRIMSON_START = "#EF4444"
    CRIMSON_END = "#F87171"
    CRIMSON = "#DC2626"
    CRIMSON_HOVER = "#EF4444"
    CRIMSON_ACTIVE = "#B91C1C"
    CRIMSON_SOFT = "rgba(220, 38, 38, 0.15)"
    CRIMSON_GLOW = "rgba(239, 68, 68, 0.3)"
    CRIMSON_GRADIENT = "linear-gradient(135deg, #EF4444 0%, #F87171 100%)"

    # Neon Gradient (Accent) - cyan-lime premium
    NEON_START = "#06B6D4"
    NEON_END = "#22D3EE"
    NEON = "#0891B2"
    NEON_HOVER = "#06B6D4"
    NEON_ACTIVE = "#0E7490"
    NEON_SOFT = "rgba(8, 145, 178, 0.15)"
    NEON_GLOW = "rgba(6, 182, 212, 0.3)"
    NEON_GRADIENT = "linear-gradient(135deg, #06B6D4 0%, #22D3EE 100%)"

    # Estados semânticos (aliases) - atualizados com novas cores
    SUCCESS = "#22C55E"
    SUCCESS_SOFT = "rgba(34, 197, 94, 0.15)"
    SUCCESS_GLOW = "rgba(34, 197, 94, 0.3)"
    WARNING = "#F59E0B"
    WARNING_SOFT = "rgba(245, 158, 11, 0.15)"
    WARNING_GLOW = "rgba(245, 158, 11, 0.3)"
    ERROR = "#EF4444"
    ERROR_SOFT = "rgba(239, 68, 68, 0.15)"
    ERROR_GLOW = "rgba(239, 68, 68, 0.3)"
    INFO = "#3B82F6"
    INFO_SOFT = "rgba(59, 130, 246, 0.15)"
    INFO_GLOW = "rgba(59, 130, 246, 0.3)"

    # Sidebar - glassmorphism atualizado
    SIDEBAR_BG = "#161B22"
    SIDEBAR_BORDER = "rgba(48, 54, 61, 0.8)"
    SIDEBAR_TEXT = "#9CA3AF"
    SIDEBAR_TEXT_MUTED = "#6B7280"
    SIDEBAR_ACTIVE = AURORA
    SIDEBAR_ACTIVE_BG = AURORA_SOFT
    SIDEBAR_HOVER = "rgba(48, 54, 61, 0.5)"
    SIDEBAR_ACTIVE_INDICATOR = AURORA

    # Header/TopBar - glass atualizado
    HEADER_BG = "rgba(22, 27, 34, 0.95)"
    HEADER_BORDER = "rgba(48, 54, 61, 0.8)"

    # Cards - glassmorphism atualizado
    CARD_BG = "#161B22"
    CARD_BORDER = "rgba(48, 54, 61, 0.8)"
    CARD_HOVER = "#21262D"
    CARD_GLOW = "rgba(211, 47, 47, 0.1)"

    # Tabelas atualizadas
    TABLE_HEADER_BG = "#161B22"
    TABLE_HEADER_TEXT = "#9CA3AF"
    TABLE_ROW_EVEN = "#0D1117"
    TABLE_ROW_ODD = "#161B22"
    TABLE_ROW_HOVER = "rgba(211, 47, 47, 0.08)"
    TABLE_ROW_SELECTED = AURORA_SOFT

    # Chart palette - atualizado com cores premium
    CHART_1 = "#D32F2F"   # brand primary
    CHART_2 = "#0EA5E9"   # ocean
    CHART_3 = "#F97316"   # sunset
    CHART_4 = "#3B82F6"   # cosmos
    CHART_5 = "#22C55E"   # forest
    CHART_6 = "#EF4444"   # crimson
    CHART_7 = "#F59E0B"   # ember
    CHART_8 = "#06B6D4"   # neon

    CHART_BG = "#0D1117"
    CHART_GRID = "rgba(48, 54, 61, 0.5)"
    CHART_TEXT = "#9CA3AF"


class AuroraLightTheme:
    """Tema Aurora Light - clean e sofisticado."""

    # Superfícies
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F8FAFC"
    BG_TERTIARY = "#F1F5F9"
    BG_ELEVATED = "#FFFFFF"
    BG_OVERLAY = "#E2E8F0"
    BG_SURFACE = "#F8FAFC"
    BG_GLASS = "rgba(255, 255, 255, 0.9)"

    # Texto
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#475569"
    TEXT_TERTIARY = "#94A3B8"
    TEXT_DISABLED = "#CBD5E1"
    TEXT_INVERTED = "#FFFFFF"

    # Bordas
    BORDER_SUBTLE = "rgba(148, 163, 184, 0.2)"
    BORDER_DEFAULT = "rgba(148, 163, 184, 0.3)"
    BORDER_STRONG = "rgba(148, 163, 184, 0.5)"
    BORDER_HOVER = "rgba(148, 163, 184, 0.4)"
    BORDER_FOCUS = "rgba(207, 34, 46, 0.4)"

    # Aurora (Primary) - vermelho CW
    AURORA_START = "#CF222E"
    AURORA_END = "#F85149"
    AURORA = "#CF222E"
    AURORA_HOVER = "#F85149"
    AURORA_ACTIVE = "#A40E26"
    AURORA_SOFT = "rgba(207, 34, 46, 0.1)"
    AURORA_GLOW = "rgba(207, 34, 46, 0.15)"
    AURORA_GRADIENT = "linear-gradient(135deg, #CF222E 0%, #F85149 100%)"

    # Ocean (Secondary)
    OCEAN_START = "#14B8A6"
    OCEAN_END = "#06B6D4"
    OCEAN = "#0891B2"
    OCEAN_HOVER = "#06B6D4"
    OCEAN_ACTIVE = "#0E7490"
    OCEAN_SOFT = "rgba(8, 145, 178, 0.1)"
    OCEAN_GLOW = "rgba(20, 184, 166, 0.15)"
    OCEAN_GRADIENT = "linear-gradient(135deg, #14B8A6 0%, #06B6D4 100%)"

    # Sunset (Warm)
    SUNSET_START = "#F97316"
    SUNSET_END = "#EC4899"
    SUNSET = "#EA580C"
    SUNSET_HOVER = "#F97316"
    SUNSET_ACTIVE = "#C2410C"
    SUNSET_SOFT = "rgba(234, 88, 12, 0.1)"
    SUNSET_GLOW = "rgba(249, 115, 22, 0.15)"
    SUNSET_GRADIENT = "linear-gradient(135deg, #F97316 0%, #EC4899 100%)"

    # Forest (Success)
    FOREST_START = "#10B981"
    FOREST_END = "#34D399"
    FOREST = "#059669"
    FOREST_HOVER = "#10B981"
    FOREST_ACTIVE = "#047857"
    FOREST_SOFT = "rgba(5, 150, 105, 0.1)"
    FOREST_GLOW = "rgba(16, 185, 129, 0.15)"
    FOREST_GRADIENT = "linear-gradient(135deg, #10B981 0%, #34D399 100%)"

    # Cosmos (Info)
    COSMOS_START = "#3B82F6"
    COSMOS_END = "#8B5CF6"
    COSMOS = "#2563EB"
    COSMOS_HOVER = "#3B82F6"
    COSMOS_ACTIVE = "#1D4ED8"
    COSMOS_SOFT = "rgba(37, 99, 235, 0.1)"
    COSMOS_GLOW = "rgba(59, 130, 246, 0.15)"
    COSMOS_GRADIENT = "linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)"

    # Ember (Warning)
    EMBER_START = "#F59E0B"
    EMBER_END = "#FB923C"
    EMBER = "#D97706"
    EMBER_HOVER = "#F59E0B"
    EMBER_ACTIVE = "#B45309"
    EMBER_SOFT = "rgba(217, 119, 6, 0.1)"
    EMBER_GLOW = "rgba(245, 158, 11, 0.15)"
    EMBER_GRADIENT = "linear-gradient(135deg, #F59E0B 0%, #FB923C 100%)"

    # Crimson (Error)
    CRIMSON_START = "#EF4444"
    CRIMSON_END = "#F43F5E"
    CRIMSON = "#DC2626"
    CRIMSON_HOVER = "#EF4444"
    CRIMSON_ACTIVE = "#B91C1C"
    CRIMSON_SOFT = "rgba(220, 38, 38, 0.1)"
    CRIMSON_GLOW = "rgba(239, 68, 68, 0.15)"
    CRIMSON_GRADIENT = "linear-gradient(135deg, #EF4444 0%, #F43F5E 100%)"

    # Neon (Accent)
    NEON_START = "#06B6D4"
    NEON_END = "#84CC16"
    NEON = "#0891B2"
    NEON_HOVER = "#06B6D4"
    NEON_ACTIVE = "#0E7490"
    NEON_SOFT = "rgba(8, 145, 178, 0.1)"
    NEON_GLOW = "rgba(6, 182, 212, 0.15)"
    NEON_GRADIENT = "linear-gradient(135deg, #06B6D4 0%, #84CC16 100%)"

    # Estados
    SUCCESS = FOREST
    SUCCESS_SOFT = FOREST_SOFT
    SUCCESS_GLOW = FOREST_GLOW
    WARNING = EMBER
    WARNING_SOFT = EMBER_SOFT
    WARNING_GLOW = EMBER_GLOW
    ERROR = CRIMSON
    ERROR_SOFT = CRIMSON_SOFT
    ERROR_GLOW = CRIMSON_GLOW
    INFO = COSMOS
    INFO_SOFT = COSMOS_SOFT
    INFO_GLOW = COSMOS_GLOW

    # Sidebar
    SIDEBAR_BG = "#F8FAFC"
    SIDEBAR_BORDER = "rgba(148, 163, 184, 0.2)"
    SIDEBAR_TEXT = "#475569"
    SIDEBAR_TEXT_MUTED = "#94A3B8"
    SIDEBAR_ACTIVE = AURORA
    SIDEBAR_ACTIVE_BG = AURORA_SOFT
    SIDEBAR_HOVER = "rgba(148, 163, 184, 0.08)"
    SIDEBAR_ACTIVE_INDICATOR = AURORA

    # Header
    HEADER_BG = "rgba(255, 255, 255, 0.95)"
    HEADER_BORDER = "rgba(148, 163, 184, 0.2)"

    # Cards
    CARD_BG = "rgba(255, 255, 255, 0.9)"
    CARD_BORDER = "rgba(148, 163, 184, 0.2)"
    CARD_HOVER = "#FFFFFF"
    CARD_GLOW = "rgba(207, 34, 46, 0.06)"

    # Tabelas
    TABLE_HEADER_BG = "#F8FAFC"
    TABLE_HEADER_TEXT = "#64748B"
    TABLE_ROW_EVEN = "#FFFFFF"
    TABLE_ROW_ODD = "#F8FAFC"
    TABLE_ROW_HOVER = "rgba(207, 34, 46, 0.06)"
    TABLE_ROW_SELECTED = AURORA_SOFT

    # Charts
    CHART_1 = "#CF222E"
    CHART_2 = "#14B8A6"
    CHART_3 = "#F97316"
    CHART_4 = "#3B82F6"
    CHART_5 = "#10B981"
    CHART_6 = "#F43F5E"
    CHART_7 = "#FB923C"
    CHART_8 = "#06B6D4"

    CHART_BG = "#FFFFFF"
    CHART_GRID = "rgba(148, 163, 184, 0.15)"
    CHART_TEXT = "#64748B"


class AuroraThemeManager:
    """Gerenciador central do Aurora Design System."""

    def __init__(self):
        self._current_mode = ThemeMode.DARK
        self._theme = AuroraDarkTheme
        self._tokens = ThemeTokens

    def set_mode(self, mode: ThemeMode):
        self._current_mode = mode
        self._theme = AuroraLightTheme if mode == ThemeMode.LIGHT else AuroraDarkTheme

    def get_mode(self) -> ThemeMode:
        return self._current_mode

    def toggle_mode(self):
        if self._current_mode == ThemeMode.LIGHT:
            self.set_mode(ThemeMode.DARK)
        else:
            self.set_mode(ThemeMode.LIGHT)

    @property
    def colors(self) -> Dict[str, str]:
        theme = self._theme
        return {
            "bg_primary": theme.BG_PRIMARY,
            "bg_secondary": theme.BG_SECONDARY,
            "bg_tertiary": theme.BG_TERTIARY,
            "bg_elevated": theme.BG_ELEVATED,
            "bg_overlay": theme.BG_OVERLAY,
            "bg_surface": theme.BG_SURFACE,
            "bg_glass": theme.BG_GLASS,

            "text_primary": theme.TEXT_PRIMARY,
            "text_secondary": theme.TEXT_SECONDARY,
            "text_tertiary": theme.TEXT_TERTIARY,
            "text_disabled": theme.TEXT_DISABLED,
            "text_inverted": theme.TEXT_INVERTED,

            "border_subtle": theme.BORDER_SUBTLE,
            "border_default": theme.BORDER_DEFAULT,
            "border_strong": theme.BORDER_STRONG,
            "border_hover": theme.BORDER_HOVER,
            "border_focus": theme.BORDER_FOCUS,

            "aurora": theme.AURORA,
            "aurora_start": theme.AURORA_START,
            "aurora_end": theme.AURORA_END,
            "aurora_hover": theme.AURORA_HOVER,
            "aurora_active": theme.AURORA_ACTIVE,
            "aurora_soft": theme.AURORA_SOFT,
            "aurora_glow": theme.AURORA_GLOW,
            "aurora_gradient": theme.AURORA_GRADIENT,

            "ocean": theme.OCEAN,
            "ocean_start": theme.OCEAN_START,
            "ocean_end": theme.OCEAN_END,
            "ocean_hover": theme.OCEAN_HOVER,
            "ocean_active": theme.OCEAN_ACTIVE,
            "ocean_soft": theme.OCEAN_SOFT,
            "ocean_glow": theme.OCEAN_GLOW,
            "ocean_gradient": theme.OCEAN_GRADIENT,

            "sunset": theme.SUNSET,
            "sunset_start": theme.SUNSET_START,
            "sunset_end": theme.SUNSET_END,
            "sunset_hover": theme.SUNSET_HOVER,
            "sunset_active": theme.SUNSET_ACTIVE,
            "sunset_soft": theme.SUNSET_SOFT,
            "sunset_glow": theme.SUNSET_GLOW,
            "sunset_gradient": theme.SUNSET_GRADIENT,

            "forest": theme.FOREST,
            "forest_start": theme.FOREST_START,
            "forest_end": theme.FOREST_END,
            "forest_hover": theme.FOREST_HOVER,
            "forest_active": theme.FOREST_ACTIVE,
            "forest_soft": theme.FOREST_SOFT,
            "forest_glow": theme.FOREST_GLOW,
            "forest_gradient": theme.FOREST_GRADIENT,

            "cosmos": theme.COSMOS,
            "cosmos_start": theme.COSMOS_START,
            "cosmos_end": theme.COSMOS_END,
            "cosmos_hover": theme.COSMOS_HOVER,
            "cosmos_active": theme.COSMOS_ACTIVE,
            "cosmos_soft": theme.COSMOS_SOFT,
            "cosmos_glow": theme.COSMOS_GLOW,
            "cosmos_gradient": theme.COSMOS_GRADIENT,

            "ember": theme.EMBER,
            "ember_start": theme.EMBER_START,
            "ember_end": theme.EMBER_END,
            "ember_hover": theme.EMBER_HOVER,
            "ember_active": theme.EMBER_ACTIVE,
            "ember_soft": theme.EMBER_SOFT,
            "ember_glow": theme.EMBER_GLOW,
            "ember_gradient": theme.EMBER_GRADIENT,

            "crimson": theme.CRIMSON,
            "crimson_start": theme.CRIMSON_START,
            "crimson_end": theme.CRIMSON_END,
            "crimson_hover": theme.CRIMSON_HOVER,
            "crimson_active": theme.CRIMSON_ACTIVE,
            "crimson_soft": theme.CRIMSON_SOFT,
            "crimson_glow": theme.CRIMSON_GLOW,
            "crimson_gradient": theme.CRIMSON_GRADIENT,

            "neon": theme.NEON,
            "neon_start": theme.NEON_START,
            "neon_end": theme.NEON_END,
            "neon_hover": theme.NEON_HOVER,
            "neon_active": theme.NEON_ACTIVE,
            "neon_soft": theme.NEON_SOFT,
            "neon_glow": theme.NEON_GLOW,
            "neon_gradient": theme.NEON_GRADIENT,

            "success": theme.SUCCESS,
            "success_soft": theme.SUCCESS_SOFT,
            "success_glow": theme.SUCCESS_GLOW,
            "warning": theme.WARNING,
            "warning_soft": theme.WARNING_SOFT,
            "warning_glow": theme.WARNING_GLOW,
            "error": theme.ERROR,
            "error_soft": theme.ERROR_SOFT,
            "error_glow": theme.ERROR_GLOW,
            "info": theme.INFO,
            "info_soft": theme.INFO_SOFT,
            "info_glow": theme.INFO_GLOW,

            "sidebar_bg": theme.SIDEBAR_BG,
            "sidebar_border": theme.SIDEBAR_BORDER,
            "sidebar_text": theme.SIDEBAR_TEXT,
            "sidebar_text_muted": theme.SIDEBAR_TEXT_MUTED,
            "sidebar_active": theme.SIDEBAR_ACTIVE,
            "sidebar_active_bg": theme.SIDEBAR_ACTIVE_BG,
            "sidebar_hover": theme.SIDEBAR_HOVER,
            "sidebar_active_indicator": theme.SIDEBAR_ACTIVE_INDICATOR,

            "header_bg": theme.HEADER_BG,
            "header_border": theme.HEADER_BORDER,

            "card_bg": theme.CARD_BG,
            "card_border": theme.CARD_BORDER,
            "card_hover": theme.CARD_HOVER,
            "card_glow": theme.CARD_GLOW,

            "table_header_bg": theme.TABLE_HEADER_BG,
            "table_header_text": theme.TABLE_HEADER_TEXT,
            "table_row_even": theme.TABLE_ROW_EVEN,
            "table_row_odd": theme.TABLE_ROW_ODD,
            "table_row_hover": theme.TABLE_ROW_HOVER,
            "table_row_selected": theme.TABLE_ROW_SELECTED,

            "chart_1": theme.CHART_1,
            "chart_2": theme.CHART_2,
            "chart_3": theme.CHART_3,
            "chart_4": theme.CHART_4,
            "chart_5": theme.CHART_5,
            "chart_6": theme.CHART_6,
            "chart_7": theme.CHART_7,
            "chart_8": theme.CHART_8,
            "chart_bg": theme.CHART_BG,
            "chart_grid": theme.CHART_GRID,
            "chart_text": theme.CHART_TEXT,

            # Backward compatibility aliases (old theme_pyside6 keys)
            "brand": theme.AURORA,
            "brand_hover": theme.AURORA_HOVER,
            "brand_active": theme.AURORA_ACTIVE,
            "brand_soft": theme.AURORA_SOFT,
            "brand_glow": theme.AURORA_GLOW,
            "violet": theme.COSMOS,
            "violet_soft": theme.COSMOS_SOFT,
            "emerald": theme.FOREST,
            "emerald_soft": theme.FOREST_SOFT,
            "sky": theme.OCEAN,
            "sky_soft": theme.OCEAN_SOFT,
            "amber": theme.EMBER,
            "amber_soft": theme.EMBER_SOFT,
            "cyan": theme.OCEAN,
            "cyan_soft": theme.OCEAN_SOFT,
            "rose": theme.CRIMSON,
            "rose_soft": theme.CRIMSON_SOFT,
        }

    @property
    def tokens(self) -> ThemeTokens:
        return self._tokens

    def get_color(self, color_name: str) -> str:
        return self.colors.get(color_name, "#000000")

    def get_accent(self, accent: AccentColor) -> str:
        accent_map = {
            AccentColor.AURORA: "aurora",
            AccentColor.OCEAN: "ocean",
            AccentColor.SUNSET: "sunset",
            AccentColor.FOREST: "forest",
            AccentColor.COSMOS: "cosmos",
            AccentColor.EMBER: "ember",
            AccentColor.CRIMSON: "crimson",
            AccentColor.NEON: "neon",
            # Backward compatibility aliases
            AccentColor.BRAND: "aurora",
            AccentColor.EMERALD: "forest",
            AccentColor.SKY: "ocean",
            AccentColor.AMBER: "ember",
            AccentColor.VIOLET: "aurora",
            AccentColor.CYAN: "ocean",
            AccentColor.ROSE: "crimson",
        }
        return self.get_color(accent_map.get(accent, "aurora"))

    def get_gradient(self, accent: AccentColor) -> str:
        accent_map = {
            AccentColor.AURORA: "aurora_gradient",
            AccentColor.OCEAN: "ocean_gradient",
            AccentColor.SUNSET: "sunset_gradient",
            AccentColor.FOREST: "forest_gradient",
            AccentColor.COSMOS: "cosmos_gradient",
            AccentColor.EMBER: "ember_gradient",
            AccentColor.CRIMSON: "crimson_gradient",
            AccentColor.NEON: "neon_gradient",
            # Backward compatibility aliases
            AccentColor.BRAND: "aurora_gradient",
            AccentColor.EMERALD: "forest_gradient",
            AccentColor.SKY: "ocean_gradient",
            AccentColor.AMBER: "ember_gradient",
            AccentColor.VIOLET: "aurora_gradient",
            AccentColor.CYAN: "ocean_gradient",
            AccentColor.ROSE: "crimson_gradient",
        }
        return self.get_color(accent_map.get(accent, "aurora_gradient"))

    def get_glow(self, accent: AccentColor) -> str:
        accent_map = {
            AccentColor.AURORA: "aurora_glow",
            AccentColor.OCEAN: "ocean_glow",
            AccentColor.SUNSET: "sunset_glow",
            AccentColor.FOREST: "forest_glow",
            AccentColor.COSMOS: "cosmos_glow",
            AccentColor.EMBER: "ember_glow",
            AccentColor.CRIMSON: "crimson_glow",
            AccentColor.NEON: "neon_glow",
            # Backward compatibility aliases
            AccentColor.BRAND: "aurora_glow",
            AccentColor.EMERALD: "forest_glow",
            AccentColor.SKY: "ocean_glow",
            AccentColor.AMBER: "ember_glow",
            AccentColor.VIOLET: "aurora_glow",
            AccentColor.CYAN: "ocean_glow",
            AccentColor.ROSE: "crimson_glow",
        }
        return self.get_color(accent_map.get(accent, "aurora_glow"))

    def get_chart_colors(self) -> list:
        c = self.colors
        return [c["chart_1"], c["chart_2"], c["chart_3"], c["chart_4"],
                c["chart_5"], c["chart_6"], c["chart_7"], c["chart_8"]]

    def get_font(self, size: int = None, bold: bool = False, weight: int = None) -> QFont:
        size = size or self._tokens.FONT_SIZE_MD
        font = QFont(self._tokens.FONT_FAMILY_QT, size)
        if weight is not None:
            try:
                font.setWeight(weight)
            except Exception:
                pass
        if bold:
            font.setBold(True)
        return font

    def get_stylesheet(self) -> str:
        """Stylesheet global Aurora Design System."""
        c = self.colors
        t = self._tokens

        return f"""
        * {{ font-family: {t.FONT_FAMILY}; }}

        QMainWindow, QDialog {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
        }}

        QWidget {{
            color: {c['text_primary']};
            font-size: {t.FONT_SIZE_MD}px;
        }}

        QLabel {{
            background-color: transparent;
            color: {c['text_primary']};
            border: none;
        }}

        QToolTip {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_MD}px;
            padding: 10px 16px;
            font-size: {t.FONT_SIZE_SM}px;
        }}

        /* BOTÕES AURORA */
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            color: #FFFFFF;
            border: none;
            border-radius: {t.RADIUS_LG}px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: {t.FONT_SIZE_MD}px;
            min-height: 22px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_hover']}, stop:1 {c['aurora_end']});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_active']}, stop:1 {c['aurora']});
        }}
        QPushButton:disabled {{
            background: {c['bg_tertiary']};
            color: {c['text_disabled']};
        }}

        /* INPUTS */
        QLineEdit, QTextEdit, QPlainTextEdit,
        QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QTimeEdit {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 12px 16px;
            selection-background-color: {c['aurora_soft']};
            selection-color: {c['text_primary']};
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {c['border_strong']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1px solid {c['aurora']};
            background-color: {c['bg_surface']};
        }}
        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {c['bg_secondary']};
            color: {c['text_disabled']};
            border-color: {c['border_subtle']};
        }}

        /* COMBOBOX */
        QComboBox {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 10px 16px;
            min-height: 28px;
        }}
        QComboBox:hover {{ border-color: {c['border_strong']}; }}
        QComboBox:focus {{ border: 1px solid {c['aurora']}; }}
        QComboBox::drop-down {{ border: none; width: 32px; subcontrol-position: center right; }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c['text_secondary']};
            margin-right: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            selection-background-color: {c['aurora_soft']};
            selection-color: {c['text_primary']};
            padding: 6px;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 10px 14px;
            border-radius: {t.RADIUS_SM}px;
            min-height: 24px;
        }}
        QComboBox QAbstractItemView::item:hover {{ background-color: {c['bg_overlay']}; }}

        /* CHECKBOX / RADIO */
        QCheckBox, QRadioButton {{
            color: {c['text_secondary']};
            spacing: 12px;
            background-color: transparent;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 20px; height: 20px;
            border: 2px solid {c['border_default']};
            background-color: {c['bg_tertiary']};
        }}
        QCheckBox::indicator {{ border-radius: {t.RADIUS_XS}px; }}
        QRadioButton::indicator {{ border-radius: 10px; }}
        QCheckBox::indicator:hover, QRadioButton::indicator:hover {{ border-color: {c['aurora']}; }}
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            border-color: {c['aurora']};
        }}
        QRadioButton::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            border-color: {c['aurora']};
        }}

        /* TABELAS */
        QTableView, QTableWidget, QTreeView, QListView {{
            background-color: {c['bg_primary']};
            alternate-background-color: {c['table_row_odd']};
            gridline-color: transparent;
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_XL}px;
            selection-background-color: {c['table_row_selected']};
            selection-color: {c['text_primary']};
            outline: none;
        }}
        QTableView::item, QTableWidget::item {{
            padding: 14px 18px;
            border: none;
            border-bottom: 1px solid {c['border_subtle']};
        }}
        QTableView::item:hover, QTableWidget::item:hover {{
            background-color: {c['table_row_hover']};
        }}
        QTableView::item:selected, QTableWidget::item:selected {{
            background-color: {c['table_row_selected']};
            color: {c['text_primary']};
            font-weight: 600;
        }}
        QHeaderView {{ background-color: {c['table_header_bg']}; border: none; }}
        QHeaderView::section {{
            background-color: {c['table_header_bg']};
            color: {c['table_header_text']};
            padding: 14px 18px;
            border: none;
            border-bottom: 1px solid {c['border_default']};
            border-right: 1px solid {c['border_subtle']};
            font-weight: 600;
            font-size: {t.FONT_SIZE_SM}px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }}
        QHeaderView::section:first {{ border-top-left-radius: {t.RADIUS_XL}px; }}
        QHeaderView::section:last {{ border-top-right-radius: {t.RADIUS_XL}px; border-right: none; }}

        /* SCROLLBARS */
        QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{
            background: {c['border_default']}; border-radius: 3px; min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {c['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none; height: 0px;
        }}
        QScrollBar:horizontal {{ background: transparent; height: 6px; margin: 2px 4px; }}
        QScrollBar::handle:horizontal {{
            background: {c['border_default']}; border-radius: 3px; min-width: 40px;
        }}
        QScrollBar::handle:horizontal:hover {{ background: {c['border_strong']}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none; width: 0px;
        }}

        /* MENUS */
        QMenu {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_XL}px;
            padding: 8px;
        }}
        QMenu::item {{ padding: 10px 18px; border-radius: {t.RADIUS_SM}px; min-width: 180px; }}
        QMenu::item:selected {{ background-color: {c['bg_overlay']}; }}
        QMenu::separator {{ height: 1px; background: {c['border_subtle']}; margin: 6px 10px; }}

        QMessageBox {{ background-color: {c['bg_elevated']}; }}
        QMessageBox QLabel {{ color: {c['text_primary']}; font-size: {t.FONT_SIZE_MD}px; padding: 10px; }}
        QMessageBox QPushButton {{ min-width: 100px; padding: 10px 20px; }}

        /* TABS */
        QTabWidget::pane {{
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_XL}px;
            background: {c['bg_elevated']};
            top: -1px;
        }}
        QTabBar::tab {{
            background: transparent;
            color: {c['text_tertiary']};
            padding: 14px 28px;
            border: none;
            border-bottom: 2px solid transparent;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{ color: {c['text_primary']}; border-bottom: 2px solid {c['aurora']}; }}
        QTabBar::tab:hover:!selected {{ color: {c['text_secondary']}; border-bottom: 2px solid {c['border_default']}; }}

        /* GROUPBOX */
        QGroupBox {{
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_XL}px;
            margin-top: 20px; padding: 20px;
            background: {c['bg_elevated']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin; left: 16px; padding: 0 10px;
            color: {c['text_secondary']}; background: {c['bg_primary']};
            font-size: {t.FONT_SIZE_SM}px; text-transform: uppercase; letter-spacing: 0.8px;
        }}

        /* PROGRESS */
        QProgressBar {{
            background: {c['bg_tertiary']}; border: none; border-radius: 6px;
            text-align: center; color: {c['text_primary']}; height: 8px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            border-radius: 6px;
        }}

        QSplitter::handle {{ background: {c['border_subtle']}; }}
        QSplitter::handle:horizontal {{ width: 1px; }}
        QSplitter::handle:vertical {{ height: 1px; }}

        QDialog {{ background: {c['bg_primary']}; }}
        QDialog > QFrame {{ background: transparent; }}

        QStatusBar {{
            background: {c['bg_secondary']};
            color: {c['text_secondary']};
            border-top: 1px solid {c['border_subtle']};
            padding: 6px 16px;
            font-size: {t.FONT_SIZE_SM}px;
        }}

        QSlider::groove:horizontal {{ height: 6px; background: {c['bg_tertiary']}; border-radius: 3px; }}
        QSlider::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            width: 20px; height: 20px; margin: -7px 0; border-radius: 10px;
        }}
        QSlider::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_hover']}, stop:1 {c['aurora_end']});
        }}
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            border-radius: 3px;
        }}
        """

    def apply_to_app(self, app):
        app.setStyleSheet(self.get_stylesheet())


aurora_theme_manager = AuroraThemeManager()

# Backward compatibility: allow importing as theme_manager
theme_manager = aurora_theme_manager


def setup_aurora_theme(settings) -> Dict[str, str]:
    """Configura o tema Aurora. Retorna dict de cores com aliases."""
    tema_config = settings.configuracoes.get("tema", "Aurora Dark")
    if tema_config == "Aurora Light":
        aurora_theme_manager.set_mode(ThemeMode.LIGHT)
    else:
        aurora_theme_manager.set_mode(ThemeMode.DARK)

    colors = aurora_theme_manager.colors
    return {
        "fundo": colors["bg_primary"],
        "sidebar": colors["sidebar_bg"],
        "sidebar_card": colors["bg_elevated"],
        "header": colors["header_bg"],
        "header_bg": colors["header_bg"],
        "header_tag": colors["aurora"],
        "header_title": colors["text_primary"],
        "header_subtitle": colors["text_secondary"],
        "principal": colors["aurora"],
        "hover": colors["aurora_hover"],
        "texto": colors["text_primary"],
        "texto_suave": colors["text_secondary"],
        "card_bg": colors["card_bg"],
        "card_text": colors["text_primary"],
        "muted_border": colors["border_subtle"],
        "surface_alt": colors["bg_tertiary"],
        "accent": colors["aurora"],
        "divider": colors["border_default"],
        "shadow": colors["aurora_glow"],
        "font_family": aurora_theme_manager.tokens.FONT_FAMILY,
        "aurora": colors["aurora"],
        "aurora_soft": colors["aurora_soft"],
        "ocean": colors["ocean"],
        "ocean_soft": colors["ocean_soft"],
        "sunset": colors["sunset"],
        "sunset_soft": colors["sunset_soft"],
        "forest": colors["forest"],
        "forest_soft": colors["forest_soft"],
        "cosmos": colors["cosmos"],
        "cosmos_soft": colors["cosmos_soft"],
        "ember": colors["ember"],
        "ember_soft": colors["ember_soft"],
        "crimson": colors["crimson"],
        "crimson_soft": colors["crimson_soft"],
        "neon": colors["neon"],
        "neon_soft": colors["neon_soft"],
        "success": colors["success"],
        "success_soft": colors["success_soft"],
        "warning": colors["warning"],
        "warning_soft": colors["warning_soft"],
        "error": colors["error"],
        "error_soft": colors["error_soft"],
        "info": colors["info"],
        "info_soft": colors["info_soft"],
        "chart_bg": colors["chart_bg"],
        "chart_grid": colors["chart_grid"],
        "chart_text": colors["chart_text"],
    }

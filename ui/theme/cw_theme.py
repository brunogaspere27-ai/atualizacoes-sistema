"""
Tema CW (Clean Window) para PySide6.
"""
from PySide6.QtGui import QFont


class CWTheme:
    """Tema CW com design tokens."""

    def __init__(self):
        self.colors = {
            "bg_primary": "#0D1117",
            "bg_secondary": "#161B22",
            "bg_tertiary": "#21262D",
            "bg_elevated": "#1C2128",
            "bg_overlay": "#30363D",
            "bg_surface": "#161B22",
            "bg_glass": "rgba(22, 27, 34, 0.8)",

            "text_primary": "#FFFFFF",
            "text_secondary": "#9CA3AF",
            "text_tertiary": "#6B7280",
            "text_disabled": "#484F58",
            "text_inverted": "#0D1117",

            "border_subtle": "rgba(48, 54, 61, 0.5)",
            "border_default": "rgba(48, 54, 61, 0.8)",
            "border_strong": "rgba(240, 246, 252, 0.15)",
            "border_hover": "rgba(240, 246, 252, 0.2)",
            "border_focus": "rgba(211, 47, 47, 0.5)",

            "primary": "#D32F2F",
            "primary_hover": "#E53935",
            "primary_active": "#C62828",
            "primary_soft": "rgba(211, 47, 47, 0.15)",

            "success": "#22C55E",
            "success_soft": "rgba(34, 197, 94, 0.15)",
            "warning": "#F59E0B",
            "warning_soft": "rgba(245, 158, 11, 0.15)",
            "error": "#EF4444",
            "error_soft": "rgba(239, 68, 68, 0.15)",
            "info": "#3B82F6",
            "info_soft": "rgba(59, 130, 246, 0.15)",

            "sidebar_bg": "#161B22",
            "sidebar_border": "rgba(48, 54, 61, 0.8)",
            "sidebar_text": "#9CA3AF",
            "sidebar_text_muted": "#6B7280",

            "header_bg": "rgba(22, 27, 34, 0.95)",
            "header_border": "rgba(48, 54, 61, 0.8)",

            "card_bg": "#161B22",
            "card_border": "rgba(48, 54, 61, 0.8)",
            "card_hover": "#21262D",

            "table_header_bg": "#161B22",
            "table_header_text": "#9CA3AF",
            "table_row_even": "#0D1117",
            "table_row_odd": "#161B22",
            "table_row_hover": "rgba(211, 47, 47, 0.08)",
            "table_row_selected": "rgba(211, 47, 47, 0.15)",

            "brand": "#D32F2F",
            "brand_hover": "#E53935",
            "brand_active": "#C62828",
            "brand_soft": "rgba(211, 47, 47, 0.15)",
            "brand_glow": "rgba(211, 47, 47, 0.3)",

            "emerald": "#22C55E",
            "emerald_soft": "rgba(34, 197, 94, 0.15)",
            "sky": "#0EA5E9",
            "sky_soft": "rgba(14, 165, 233, 0.15)",
            "amber": "#F59E0B",
            "amber_soft": "rgba(245, 158, 11, 0.15)",
            "violet": "#8B5CF6",
            "violet_soft": "rgba(139, 92, 246, 0.15)",
            "cyan": "#06B6D4",
            "cyan_soft": "rgba(6, 182, 212, 0.15)",
            "rose": "#FB7185",
            "rose_soft": "rgba(251, 113, 133, 0.15)",
        }

        self.spacing = self._Spacing()
        self.radius = self._Radius()
        self.typography = self._Typography()

    class _Spacing:
        XS = 4
        SM = 8
        MD = 12
        LG = 16
        XL = 24
        _2XL = 32
        _3XL = 48
        _4XL = 64
        SPACING_XS = 4
        SPACING_SM = 8
        SPACING_MD = 12
        SPACING_LG = 16
        SPACING_XL = 24
        SPACING_2XL = 32
        SPACING_3XL = 48
        SPACING_4XL = 64
        FONT_SIZE_XS = 11
        FONT_SIZE_SM = 12
        FONT_SIZE_MD = 14
        FONT_SIZE_LG = 16
        FONT_SIZE_XL = 18
        FONT_SIZE_2XL = 24
        FONT_SIZE_3XL = 32
        FONT_FAMILY_QT = "Segoe UI"

    class _Radius:
        XS = 4
        SM = 8
        MD = 12
        LG = 16
        XL = 20
        _2XL = 24

    class _Typography:
        FONT_SIZE_XS = 11
        FONT_SIZE_SM = 12
        FONT_SIZE_MD = 14
        FONT_SIZE_LG = 16
        FONT_SIZE_XL = 18
        FONT_SIZE_2XL = 24
        FONT_SIZE_3XL = 32
        FONT_FAMILY_QT = "Segoe UI"

    def get_font(self, size=14, bold=False, weight=None):
        font = QFont(self.spacing.FONT_FAMILY_QT, size)
        if weight is not None:
            try:
                font.setWeight(weight)
            except Exception:
                pass
        if bold:
            font.setBold(True)
        return font


# Instância global
cw_theme = CWTheme()

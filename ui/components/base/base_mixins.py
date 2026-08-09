"""
Base Mixins - CW Transportadora
Mixins para padronizar comportamentos de componentes
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtGui import QColor


class CWStylableMixin:
    """Mixin para componentes que usam o Design System CW."""
    
    def apply_cw_style(self, stylesheet: str):
        """Aplica stylesheet do Design System CW."""
        if isinstance(self, QWidget):
            self.setStyleSheet(stylesheet)
    
    def get_color_from_theme(self, theme, color_name: str) -> str:
        """Obtém cor do tema CW."""
        return theme.colors.get(color_name, "#000000")


class CWInteractiveMixin:
    """Mixin para componentes interativos (hover, focus, active)."""
    
    def setup_interactive_states(self, widget: QWidget, theme):
        """Configura estados interativos básicos."""
        self.theme = theme
        self.widget = widget
        
        # Pré-calcular estilos
        self._normal_style = widget.styleSheet()
        self._hover_style = self._normal_style
        self._focus_style = self._normal_style
        self._active_style = self._normal_style
    
    def set_hover_style(self, stylesheet: str):
        """Define stylesheet para hover."""
        self._hover_style = stylesheet
    
    def set_focus_style(self, stylesheet: str):
        """Define stylesheet para focus."""
        self._focus_style = stylesheet
    
    def set_active_style(self, stylesheet: str):
        """Define stylesheet para active."""
        self._active_style = stylesheet
    
    def animate_opacity(self, duration: int = 200, start_opacity: float = 1.0, end_opacity: float = 0.5):
        """Anima opacidade do widget."""
        if not isinstance(self.widget, QWidget):
            return
        
        animation = QPropertyAnimation(self.widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start()
        return animation

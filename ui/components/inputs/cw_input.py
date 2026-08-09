"""
CW Input - Inputs profissionais para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Label acima do campo
- Height consistente
- Focus state com borda vermelha CW
- Estados: default, focus, error, disabled
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional

from ui.theme.cw_theme import cw_theme, CWRadius, CWSpacing


class CWInput(QWidget):
    """Input profissional CW Transportadora"""
    
    def __init__(
        self,
        label: str,
        placeholder: Optional[str] = None,
        value: Optional[str] = None,
        error: Optional[str] = None,
        disabled: bool = False,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._label = label
        self._placeholder = placeholder or ""
        self._error = error
        self._disabled = disabled
        
        self._setup_ui()
        self._apply_style()
        
        if value:
            self._input.setText(value)
    
    def _setup_ui(self):
        """Configura layout do input"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(cw_theme.spacing.SM)
        self.setLayout(self.layout)
        
        # Label
        self._label_widget = QLabel(self._label)
        self._label_widget.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_SM,
            bold=True
        ))
        self.layout.addWidget(self._label_widget)
        
        # Input field
        self._input = QLineEdit()
        self._input.setPlaceholderText(self._placeholder)
        self._input.setMinimumHeight(40)
        self._input.setMaximumHeight(40)
        self.layout.addWidget(self._input)
        
        # Error message
        if self._error:
            self._error_label = QLabel(self._error)
            self._error_label.setFont(cw_theme.get_font(
                cw_theme.typography.FONT_SIZE_XS
            ))
            self.layout.addWidget(self._error_label)
        
        if self._disabled:
            self._input.setEnabled(False)
    
    def _apply_style(self):
        """Aplica estilos"""
        c = cw_theme.colors
        r = cw_theme.radius
        
        # Label style
        self._label_widget.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                background: transparent;
            }}
        """)
        
        # Input style
        border_color = c['error'] if self._error else c['border_default']
        
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_primary']};
                border: 1px solid {border_color};
                border-radius: {r.MD}px;
                padding: 0 {cw_theme.spacing.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                color: {c['text_primary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {c['border_focus']};
                padding: 0 {cw_theme.spacing.MD - 1}px;
            }}
            QLineEdit:disabled {{
                background-color: {c['bg_secondary']};
                color: {c['text_disabled']};
                border-color: {c['border_subtle']};
            }}
        """)
        
        # Error label style
        if self._error:
            self._error_label.setStyleSheet(f"""
                QLabel {{
                    color: {c['error']};
                    background: transparent;
                }}
            """)
    
    def text(self) -> str:
        """Retorna o valor do input"""
        return self._input.text()
    
    def setText(self, text: str):
        """Define o valor do input"""
        self._input.setText(text)
    
    def set_error(self, error: Optional[str]):
        """Define mensagem de erro"""
        self._error = error
        
        # Remove error label se existir
        if hasattr(self, '_error_label'):
            self.layout.removeWidget(self._error_label)
            self._error_label.deleteLater()
        
        # Adiciona error label se necessário
        if error:
            self._error_label = QLabel(error)
            self._error_label.setFont(cw_theme.get_font(
                cw_theme.typography.FONT_SIZE_XS
            ))
            self.layout.addWidget(self._error_label)
        
        self._apply_style()
    
    def set_disabled(self, disabled: bool):
        """Define estado disabled"""
        self._disabled = disabled
        self._input.setEnabled(not disabled)
        self._apply_style()

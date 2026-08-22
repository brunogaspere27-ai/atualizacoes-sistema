"""Modern Input Component - CW Transportadora
Campos de entrada com validação e Design System CW
"""

from typing import Optional, Callable
from enum import Enum
from PySide6.QtWidgets import QLineEdit, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal

from ui.theme.cw_theme import cw_theme


class InputState(Enum):
    """Estados do input."""
    NORMAL = "normal"
    FOCUS = "focus"
    ERROR = "error"
    SUCCESS = "success"
    DISABLED = "disabled"


class CWInput(QLineEdit):
    """
    Input moderno com Design System CW
    Suporta:
    - Validação integrada
    - Múltiplos estados (normal, focus, error, success)
    - Dark Mode automático
    - Placeholder customizável
    - Ícones opcionais
    """
    
    # Sinais customizados
    state_changed = Signal(InputState)
    validation_changed = Signal(bool)
    
    def __init__(
        self,
        placeholder: str = "",
        validator: Optional[Callable[[str], bool]] = None,
        parent=None
    ):
        super().__init__(parent)
        self.state = InputState.NORMAL
        self.validator_func = validator
        self.is_valid = True
        
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        
        # Conectar sinais
        self.textChanged.connect(self._on_text_changed)
        self.focusInEvent = self._on_focus_in
        self.focusOutEvent = self._on_focus_out
        
        self._apply_style()
    
    def _on_text_changed(self, text: str):
        """Valida texto quando muda."""
        if self.validator_func:
            self.is_valid = self.validator_func(text)
            if self.state != InputState.DISABLED:
                new_state = InputState.SUCCESS if self.is_valid else InputState.ERROR
                self.set_state(new_state)
            self.validation_changed.emit(self.is_valid)
    
    def _on_focus_in(self, event):
        """Manipula focus."""
        super().focusInEvent(event)
        if self.state not in [InputState.ERROR, InputState.DISABLED]:
            self.set_state(InputState.FOCUS)
    
    def _on_focus_out(self, event):
        """Manipula blur."""
        super().focusOutEvent(event)
        if self.state not in [InputState.ERROR, InputState.DISABLED]:
            self.set_state(InputState.NORMAL)
    
    def set_state(self, state: InputState):
        """Altera o estado do input."""
        if self.state == state:
            return
        
        self.state = state
        self._apply_style()
        self.state_changed.emit(state)
    
    def _apply_style(self):
        """Aplica styling baseado no estado."""
        if self.state == InputState.NORMAL:
            stylesheet = self._get_normal_style()
        elif self.state == InputState.FOCUS:
            stylesheet = self._get_focus_style()
        elif self.state == InputState.ERROR:
            stylesheet = self._get_error_style()
        elif self.state == InputState.SUCCESS:
            stylesheet = self._get_success_style()
        elif self.state == InputState.DISABLED:
            stylesheet = self._get_disabled_style()
        else:
            stylesheet = self._get_normal_style()
        
        self.setStyleSheet(stylesheet)
    
    def _get_normal_style(self) -> str:
        """Estilo NORMAL."""
        return f"""
            QLineEdit {{
                background-color: {cw_theme.colors['bg_tertiary']};
                color: {cw_theme.colors['text_primary']};
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 8px 12px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                font-family: {cw_theme.typography.FONT_FAMILY_QT};
            }}
            QLineEdit::placeholder {{
                color: {cw_theme.colors['text_tertiary']};
            }}
        """
    
    def _get_focus_style(self) -> str:
        """Estilo FOCUS."""
        return f"""
            QLineEdit {{
                background-color: {cw_theme.colors['bg_tertiary']};
                color: {cw_theme.colors['text_primary']};
                border: 2px solid {cw_theme.colors['border_focus']};
                border-radius: {cw_theme.radius.MD}px;
                padding: 8px 12px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                font-family: {cw_theme.typography.FONT_FAMILY_QT};
            }}
            QLineEdit::placeholder {{
                color: {cw_theme.colors['text_tertiary']};
            }}
        """
    
    def _get_error_style(self) -> str:
        """Estilo ERROR."""
        return f"""
            QLineEdit {{
                background-color: {cw_theme.colors['error_soft']};
                color: {cw_theme.colors['text_primary']};
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 8px 12px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                font-family: {cw_theme.typography.FONT_FAMILY_QT};
            }}
            QLineEdit::placeholder {{
                color: {cw_theme.colors['text_tertiary']};
            }}
        """
    
    def _get_success_style(self) -> str:
        """Estilo SUCCESS."""
        return f"""
            QLineEdit {{
                background-color: {cw_theme.colors['success_soft']};
                color: {cw_theme.colors['text_primary']};
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 8px 12px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                font-family: {cw_theme.typography.FONT_FAMILY_QT};
            }}
            QLineEdit::placeholder {{
                color: {cw_theme.colors['text_tertiary']};
            }}
        """
    
    def _get_disabled_style(self) -> str:
        """Estilo DISABLED."""
        return f"""
            QLineEdit {{
                background-color: {cw_theme.colors['bg_secondary']};
                color: {cw_theme.colors['text_disabled']};
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 8px 12px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                font-family: {cw_theme.typography.FONT_FAMILY_QT};
            }}
            QLineEdit::placeholder {{
                color: {cw_theme.colors['text_tertiary']};
            }}
        """
    
    def set_error(self, error_message: str = ""):
        """Marca como erro com mensagem opcional."""
        self.set_state(InputState.ERROR)
        if error_message:
            self.setToolTip(error_message)


class CWInputField(QWidget):
    """
    Container para input com label e mensagem de erro
    """
    
    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        validator: Optional[Callable[[str], bool]] = None,
        required: bool = False,
        parent=None
    ):
        super().__init__(parent)
        self.required = required
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(cw_theme.spacing.SM)
        self.setLayout(layout)
        
        # Label
        if label:
            label_text = f"{label}{'*' if required else ''}"
            label_widget = QLabel(label_text)
            label_widget.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            label_widget.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: transparent;")
            layout.addWidget(label_widget)
        
        # Input
        self.input = CWInput(placeholder=placeholder, validator=validator)
        layout.addWidget(self.input)
        
        # Mensagem de erro
        self.error_label = QLabel("")
        self.error_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XS))
        self.error_label.setStyleSheet(f"color: {cw_theme.colors['error']}; background: transparent;")
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Conectar sinais
        self.input.validation_changed.connect(self._on_validation_changed)
    
    def _on_validation_changed(self, is_valid: bool):
        """Mostra/esconde mensagem de erro."""
        if not is_valid and self.input.state == InputState.ERROR:
            self.error_label.setText("Campo inválido")
            self.error_label.show()
        else:
            self.error_label.hide()
    
    def get_value(self) -> str:
        """Retorna valor do input."""
        return self.input.text()
    
    def set_value(self, value: str):
        """Define valor do input."""
        self.input.setText(value)
    
    def set_error(self, message: str):
        """Define mensagem de erro."""
        self.input.set_error(message)
        self.error_label.setText(message)
        self.error_label.show()
    
    def is_valid(self) -> bool:
        """Retorna se o input é válido."""
        return self.input.is_valid

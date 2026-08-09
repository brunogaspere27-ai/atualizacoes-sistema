"""
CW Toast - Sistema de notificações profissional para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Notificações flutuantes
- Auto-dismiss após 4 segundos
- Variantes: Success, Error, Warning, Info
- Posição: top-right
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QFont
from typing import Optional
from enum import Enum

from ui.theme.cw_theme import cw_theme, CWSpacing, CWRadius


class ToastType(Enum):
    """Tipos de toast"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class CWToast(QWidget):
    """Toast profissional CW Transportadora"""
    
    # Sinal quando toast é fechado
    closed = Signal()
    
    def __init__(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = 4000,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._message = message
        self._toast_type = toast_type
        self._duration = duration
        
        self._setup_ui()
        self._apply_style()
        self._setup_animations()
        
        # Auto-dismiss
        QTimer.singleShot(duration, self._dismiss)
    
    def _setup_ui(self):
        """Configura layout do toast"""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedWidth(400)
        self.setMinimumHeight(60)
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(
            cw_theme.spacing.LG,
            cw_theme.spacing.MD,
            cw_theme.spacing.LG,
            cw_theme.spacing.MD
        )
        self.layout.setSpacing(cw_theme.spacing.MD)
        self.setLayout(self.layout)
        
        # Icon
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(24, 24)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setFont(cw_theme.get_font(16))
        self.layout.addWidget(self._icon_label)
        
        # Message
        self._message_label = QLabel(self._message)
        self._message_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_SM
        ))
        self._message_label.setWordWrap(True)
        self.layout.addWidget(self._message_label, 1)
        
        # Close button
        self._close_btn = QPushButton("×")
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.clicked.connect(self._dismiss)
        self.layout.addWidget(self._close_btn)
    
    def _apply_style(self):
        """Aplica estilos baseados no tipo"""
        c = cw_theme.colors
        r = cw_theme.radius
        
        # Type configurations
        type_config = {
            ToastType.SUCCESS: {
                'icon': '✓',
                'bg': c['success_soft'],
                'text': c['success'],
                'border': c['success']
            },
            ToastType.ERROR: {
                'icon': '✕',
                'bg': c['error_soft'],
                'text': c['error'],
                'border': c['error']
            },
            ToastType.WARNING: {
                'icon': '⚠',
                'bg': c['warning_soft'],
                'text': c['warning'],
                'border': c['warning']
            },
            ToastType.INFO: {
                'icon': 'ℹ',
                'bg': c['info_soft'],
                'text': c['info'],
                'border': c['info']
            }
        }
        
        config = type_config[self._toast_type]
        
        self._icon_label.setText(config['icon'])
        self._icon_label.setStyleSheet(f"""
            QLabel {{
                color: {config['text']};
                background: transparent;
            }}
        """)
        
        self._message_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                background: transparent;
            }}
        """)
        
        self._close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c['text_tertiary']};
                border: none;
                border-radius: {r.SM}px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['bg_overlay']};
                color: {c['text_primary']};
            }}
        """)
        
        self.setStyleSheet(f"""
            CWToast {{
                background-color: {config['bg']};
                border: 1px solid {config['border']};
                border-radius: {r.LG}px;
            }}
        """)
    
    def _setup_animations(self):
        """Configura animações de fade in/out"""
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        
        # Fade in
        self._fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_in.setDuration(200)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_in.start()
    
    def _dismiss(self):
        """Fecha o toast com animação"""
        # Fade out
        self._fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_out.setDuration(200)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self._on_dismiss_finished)
        self._fade_out.start()
    
    def _on_dismiss_finished(self):
        """Callback quando animação de dismiss termina"""
        self.closed.emit()
        self.close()
    
    def show_at(self, x: int, y: int):
        """Mostra toast em posição específica"""
        self.move(x, y)
        self.show()


class ToastManager:
    """Gerenciador de toasts CW Transportadora"""
    
    def __init__(self, parent: QWidget):
        self._parent = parent
        self._toasts: list[CWToast] = []
        self._toast_spacing = 16
    
    def show(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = 4000
    ):
        """Mostra um novo toast"""
        toast = CWToast(message, toast_type, duration, self._parent)
        
        # Calcular posição (top-right)
        x = self._parent.width() - toast.width() - 24
        y = 24 + (len(self._toasts) * (toast.height() + self._toast_spacing))
        
        toast.show_at(x, y)
        toast.closed.connect(lambda: self._remove_toast(toast))
        
        self._toasts.append(toast)
    
    def _remove_toast(self, toast: CWToast):
        """Remove toast da lista e reposiciona outros"""
        if toast in self._toasts:
            self._toasts.remove(toast)
            self._reposition_toasts()
    
    def _reposition_toasts(self):
        """Reposiciona todos os toasts"""
        for i, toast in enumerate(self._toasts):
            x = self._parent.width() - toast.width() - 24
            y = 24 + (i * (toast.height() + self._toast_spacing))
            toast.move(x, y)
    
    def clear(self):
        """Remove todos os toasts"""
        for toast in self._toasts[:]:
            toast._dismiss()

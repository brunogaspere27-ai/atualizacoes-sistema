"""
CW Loading State - Estados de carregamento profissionais para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Spinner animado
- Mensagem de carregamento
- Layout centralizado
- Aparência profissional
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from typing import Optional

from ui.theme.cw_theme import cw_theme, CWSpacing


class CWLoadingSpinner(QWidget):
    """Spinner animado CW Transportadora"""
    
    def __init__(self, size: int = 40, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._size = size
        self._angle = 0
        self.setFixedSize(size, size)
        
        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(50)  # 50ms = 20fps
    
    def _rotate(self):
        """Rotaciona o spinner"""
        self._angle = (self._angle + 15) % 360
        self.update()
    
    def paintEvent(self, event):
        """Desenha o spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        c = cw_theme.colors
        
        # Configurar pen
        pen = QPen(QColor(c['primary']))
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Desenhar arco
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = (self.width() - 6) // 2
        
        painter.translate(center_x, center_y)
        painter.rotate(self._angle)
        
        # Desenhar arco de 270 graus
        start_angle = 0
        span_angle = 270 * 16  # Qt usa 1/16 de grau
        
        painter.drawArc(
            -radius, -radius,
            radius * 2, radius * 2,
            start_angle, span_angle
        )
    
    def stop(self):
        """Para a animação"""
        if self._timer.isActive():
            self._timer.stop()
    
    def start(self):
        """Inicia a animação"""
        if not self._timer.isActive():
            self._timer.start(50)


class CWLoadingState(QWidget):
    """Loading state profissional CW Transportadora"""
    
    def __init__(
        self,
        message: str = "Carregando...",
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._message = message
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Configura layout do loading state"""
        c = cw_theme.colors
        t = cw_theme.spacing
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(
            t._3XL, t._3XL,
            t._3XL, t._3XL
        )
        self.layout.setSpacing(t.LG)
        self.setLayout(self.layout)
        
        # Spinner
        spinner_container = QWidget()
        spinner_layout = QHBoxLayout()
        spinner_layout.setContentsMargins(0, 0, 0, 0)
        spinner_layout.addStretch()
        spinner_container.setLayout(spinner_layout)
        
        self.spinner = CWLoadingSpinner(48)
        spinner_layout.addWidget(self.spinner)
        spinner_layout.addStretch()
        
        self.layout.addWidget(spinner_container)
        
        # Message
        message_label = QLabel(self._message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_MD
        ))
        message_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                background: transparent;
            }}
        """)
        self.layout.addWidget(message_label)
        
        self.layout.addStretch()
    
    def _apply_style(self):
        """Aplica estilos"""
        c = cw_theme.colors
        
        self.setStyleSheet(f"""
            CWLoadingState {{
                background-color: {c['bg_primary']};
                border-radius: {cw_theme.radius.LG}px;
            }}
        """)
    
    def stop_loading(self):
        """Para a animação de loading"""
        self.spinner.stop()
    
    def start_loading(self):
        """Inicia a animação de loading"""
        self.spinner.start()

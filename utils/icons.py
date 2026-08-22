"""
Gerenciador de ícones.
"""
from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import Qt


def get_icon(name, size=None, color="#ffffff"):
    """Retorna ícone como QPixmap."""
    if isinstance(size, int):
        w = h = size
    elif hasattr(size, 'width'):
        w, h = size.width(), size.height()
    else:
        w = h = 24
    
    pixmap = QPixmap(w, h)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QColor(color))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, name[0].upper() if name else "?")
    painter.end()
    
    return pixmap


def get_pixmap(name, size=None, color="#ffffff"):
    """Alias para get_icon."""
    return get_icon(name, size, color)
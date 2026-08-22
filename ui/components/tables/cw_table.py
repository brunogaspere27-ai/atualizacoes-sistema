"""
CW Table - Tabela profissional para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Cabeçalho limpo
- Linhas com altura adequada
- Hover
- Seleção clara
- Ordenação
- Estados vazios
"""

from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QWidget, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import List, Optional, Callable

from ui.theme.cw_theme import cw_theme, CWSpacing, CWRadius


class CWTable(QTableWidget):
    """Tabela profissional CW Transportadora"""
    
    def __init__(
        self,
        columns: List[str],
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._columns = columns
        self._on_row_click: Optional[Callable] = None
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Configura tabela"""
        self.setColumnCount(len(self._columns))
        self.setHorizontalHeaderLabels(self._columns)
        
        # Row height
        self.verticalHeader().setDefaultSectionSize(48)
        self.verticalHeader().setVisible(False)
        
        # Selection
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Alternating row colors (subtle)
        self.setAlternatingRowColors(True)
        
        # Header
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Click handler
        self.cellClicked.connect(self._on_cell_clicked)
    
    def _apply_style(self):
        """Aplica estilos"""
        c = cw_theme.colors
        
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {c['bg_primary']};
                border: none;
                border-radius: {cw_theme.radius.LG}px;
                gridline-color: transparent;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {c['text_primary']};
            }}
            QTableWidget::item {{
                padding: {cw_theme.spacing.SM}px;
            }}
            QTableWidget::item:selected {{
                background-color: {c['primary_soft']};
                color: {c['primary']};
            }}
            QTableWidget::item:hover {{
                background-color: {c['bg_tertiary']};
            }}
            QHeaderView::section {{
                background-color: {c['bg_secondary']};
                color: {c['text_secondary']};
                padding: {cw_theme.spacing.SM}px {cw_theme.spacing.MD}px;
                border: none;
                font-weight: 600;
                font-size: {cw_theme.typography.FONT_SIZE_XS}px;
                text-transform: uppercase;
            }}
            QTableWidget::item:alternate {{
                background-color: {c['bg_secondary']};
            }}
        """)
    
    def _on_cell_clicked(self, row: int, column: int):
        """Handler para clique na célula"""
        if self._on_row_click:
            self._on_row_click(row)
    
    def set_row_click_handler(self, handler: Callable[[int], None]):
        """Define handler para clique na linha"""
        self._on_row_click = handler
    
    def add_row(self, data: List[str]):
        """Adiciona uma linha à tabela"""
        row = self.rowCount()
        self.insertRow(row)
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.setItem(row, col, item)
    
    def clear_rows(self):
        """Limpa todas as linhas"""
        self.setRowCount(0)
    
    def set_empty_state(self, message: str, submessage: str = ""):
        """Define estado vazio"""
        self.clear_rows()
        
        # Criar widget de estado vazio
        empty_widget = QWidget()
        empty_layout = QVBoxLayout()
        empty_layout.setContentsMargins(
            cw_theme.spacing._3XL,
            cw_theme.spacing._3XL,
            cw_theme.spacing._3XL,
            cw_theme.spacing._3XL
        )
        empty_layout.setSpacing(cw_theme.spacing.MD)
        empty_widget.setLayout(empty_layout)
        
        # Mensagem principal
        msg_label = QLabel(message)
        msg_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_LG,
            bold=True
        ))
        msg_label.setStyleSheet(f"""
            QLabel {{
                color: {cw_theme.colors['text_secondary']};
                background: transparent;
            }}
        """)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(msg_label)
        
        # Submensagem
        if submessage:
            submsg_label = QLabel(submessage)
            submsg_label.setFont(cw_theme.get_font(
                cw_theme.typography.FONT_SIZE_SM
            ))
            submsg_label.setStyleSheet(f"""
                QLabel {{
                    color: {cw_theme.colors['text_tertiary']};
                    background: transparent;
                }}
            """)
            submsg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            submsg_label.setWordWrap(True)
            empty_layout.addWidget(submsg_label)
        
        self.setCellWidget(0, 0, empty_widget)
        self.setSpan(0, 0, 1, self.columnCount())

"""
Command Palette — CW Transportadora (estilo VS Code / Linear)
Ctrl+K abre busca global: navegar telas, criar viagem, buscar clientes, notas...
"""

from typing import List, Dict, Callable, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel,
    QFrame, QScrollArea, QWidget, QApplication, QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QKeyEvent, QPixmap, QFont

from ui.theme.cw_theme import cw_theme
from utils.icons import get_icon, get_pixmap


# ──────────────────────────────────────────────────────────────────────────────
# Estrutura de comando
# ──────────────────────────────────────────────────────────────────────────────
class Command:
    def __init__(self, id: str, label: str, description: str = "",
                 icon: str = "chevron_right", category: str = "Geral",
                 keywords: List[str] = None, action: Callable = None):
        self.id = id
        self.label = label
        self.description = description
        self.icon = icon
        self.category = category
        self.keywords = keywords or []
        self.action = action

    def matches(self, query: str) -> bool:
        q = query.lower().strip()
        if not q:
            return True
        haystack = f"{self.label} {self.description} {' '.join(self.keywords)}".lower()
        return all(word in haystack for word in q.split())


# ──────────────────────────────────────────────────────────────────────────────
# CommandPalette Dialog
# ──────────────────────────────────────────────────────────────────────────────
class CommandPalette(QDialog):
    """
    Popup estilo VS Code/Linear que aparece no centro da tela.
    Ctrl+K para abrir. Setas para navegar. Enter para executar. Esc para fechar.
    """

    command_executed = Signal(str)    # emite o id do comando

    def __init__(self, commands: List[Command], parent=None,
                 search_provider: Optional[Callable[[str], List[Command]]] = None):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._commands = commands
        self._search_provider = search_provider
        self._filtered: List[Command] = list(commands)
        self._selected_idx = 0
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self._apply_filter)
        self._build()

    def _build(self):
        c = cw_theme.colors
        t = cw_theme.spacing
        typo = cw_theme.typography

        # Outer transparent wrapper (for shadow)
        outer = QVBoxLayout()
        outer.setContentsMargins(16, 16, 16, 16)
        self.setLayout(outer)

        # Inner card
        card = QFrame()
        card.setObjectName("paletteCard")
        card.setMinimumWidth(580)
        card.setMaximumWidth(640)
        card.setStyleSheet(f"""
        QFrame#paletteCard {{
            background: {c['bg_elevated']};
            border: 1px solid {c['border_strong']};
            border-radius: {cw_theme.radius.XL}px;
        }}
        """)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(60)
        shadow.setYOffset(16)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card.setLayout(card_layout)
        outer.addWidget(card)

        # Search bar
        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
        QFrame {{
            background: transparent;
            border-bottom: 1px solid {c['border_default']};
        }}
        """)
        sl = QHBoxLayout()
        sl.setContentsMargins(16, 12, 16, 12)
        sl.setSpacing(10)
        search_frame.setLayout(sl)

        search_ico = QLabel()
        search_ico.setPixmap(get_pixmap("search", color=c["text_tertiary"]))
        sl.addWidget(search_ico)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar ações, telas, clientes...")
        self._search.setFrame(False)
        self._search.setFont(cw_theme.get_font(typo.FONT_SIZE_LG))
        self._search.setStyleSheet(f"""
        QLineEdit {{
            background: transparent; color: {c['text_primary']};
        }}
        """)
        sl.addWidget(self._search, 1)

        hint = QLabel("ESC limpa")
        hint.setFont(cw_theme.get_font(typo.FONT_SIZE_XS))
        hint.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        sl.addWidget(hint)

        card_layout.addWidget(search_frame)

        # Results scroll area
        self._scroll = QScrollArea()
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setMaximumHeight(360)
        self._scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 4px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 2px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self._results_w = QWidget()
        self._results_w.setStyleSheet("background: transparent;")
        self._results_layout = QVBoxLayout()
        self._results_layout.setContentsMargins(6, 6, 6, 6)
        self._results_layout.setSpacing(2)
        self._results_w.setLayout(self._results_layout)
        self._scroll.setWidget(self._results_w)
        card_layout.addWidget(self._scroll)

        # Footer hint
        footer = QFrame()
        footer.setStyleSheet(f"""
        QFrame {{
            background: transparent;
            border-top: 1px solid {c['border_subtle']};
        }}
        """)
        fl = QHBoxLayout()
        fl.setContentsMargins(16, 8, 16, 8)
        fl.setSpacing(16)
        footer.setLayout(fl)

        for key, action in [("↑↓", "navegar"), ("↵", "executar"), ("Ctrl+K", "abrir/fechar")]:
            kw = QLabel(key)
            kw.setFont(cw_theme.get_font(typo.FONT_SIZE_XS, bold=True))
            kw.setStyleSheet(f"""
            QLabel {{
                background: {c['bg_overlay']}; color: {c['text_secondary']};
                border-radius: 4px; padding: 2px 6px;
            }}
            """)
            fl.addWidget(kw)
            av = QLabel(action)
            av.setFont(cw_theme.get_font(typo.FONT_SIZE_XS))
            av.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
            fl.addWidget(av)
        fl.addStretch()

        card_layout.addWidget(footer)
        self._render_results()

    def _on_text_changed(self):
        self._debounce.start()

    def _apply_filter(self):
        query = self._search.text()
        commands = [cmd for cmd in self._commands if cmd.matches(query)]
        if self._search_provider and query.strip():
            try:
                search_results = self._search_provider(query)
                commands = search_results + commands
            except Exception as e:
                print(f"Erro no search_provider: {e}")
                search_results = []
        self._filtered = commands
        self._selected_idx = 0
        self._render_results()

    def _render_results(self):
        c = cw_theme.colors
        t = cw_theme.spacing
        typo = cw_theme.typography

        # Clear
        while self._results_layout.count():
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._filtered:
            empty = QLabel("Nenhum resultado encontrado")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setFont(cw_theme.get_font(typo.FONT_SIZE_MD))
            empty.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; padding: 24px;")
            self._results_layout.addWidget(empty)
            return

        # Group by category
        categories: Dict[str, List[Command]] = {}
        for cmd in self._filtered:
            categories.setdefault(cmd.category, []).append(cmd)

        self._row_widgets: List[QFrame] = []
        flat_idx = 0

        for cat, cmds in categories.items():
            # Category header
            cat_lbl = QLabel(cat.upper())
            cat_lbl.setFont(cw_theme.get_font(typo.FONT_SIZE_XS, bold=True))
            cat_lbl.setStyleSheet(f"""
            QLabel {{
                color: {c['text_tertiary']}; background: transparent;
                padding: 6px 10px 2px;
                letter-spacing: 1px;
            }}
            """)
            self._results_layout.addWidget(cat_lbl)

            for cmd in cmds:
                is_sel = (flat_idx == self._selected_idx)
                row = self._make_row(cmd, is_sel)
                idx_copy = flat_idx
                row.mousePressEvent = lambda e, c=cmd: self._execute(c)
                self._results_layout.addWidget(row)
                self._row_widgets.append(row)
                flat_idx += 1

        self._results_layout.addStretch()

    def _make_row(self, cmd: Command, selected: bool) -> QFrame:
        c = cw_theme.colors
        t = cw_theme.spacing
        typo = cw_theme.typography

        row = QFrame()
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        bg = c["bg_overlay"] if selected else "transparent"
        accent = c["brand"] if selected else "transparent"
        row.setStyleSheet(f"""
        QFrame {{
            background: {bg};
            border-radius: {cw_theme.radius.MD}px;
            border-left: 2px solid {accent};
        }}
        QFrame:hover {{ background: {c['bg_overlay']}; }}
        """)

        rl = QHBoxLayout()
        rl.setContentsMargins(10, 8, 10, 8)
        rl.setSpacing(12)
        row.setLayout(rl)

        # Icon
        ico = QLabel()
        icon_color = c["brand"] if selected else c["text_secondary"]
        ico.setPixmap(get_pixmap(cmd.icon, color=icon_color))
        rl.addWidget(ico)

        # Label + description
        text_col = QVBoxLayout()
        text_col.setSpacing(0)
        text_col.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(cmd.label)
        lbl.setFont(cw_theme.get_font(typo.FONT_SIZE_MD, bold=selected))
        lbl.setStyleSheet(f"color: {c['text_primary'] if selected else c['text_primary']}; background: transparent;")
        text_col.addWidget(lbl)

        if cmd.description:
            desc = QLabel(cmd.description)
            desc.setFont(cw_theme.get_font(typo.FONT_SIZE_XS))
            desc.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
            text_col.addWidget(desc)

        rl.addLayout(text_col, 1)

        # Arrow
        arr = QLabel()
        arr.setPixmap(get_pixmap("chevron_right", color=c["text_tertiary"] if not selected else c["brand"]))
        rl.addWidget(arr)

        return row

    def _execute(self, cmd: Command):
        self.command_executed.emit(cmd.id)
        if cmd.action:
            cmd.action()
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if self._search.text():
                self._search.clear()
            else:
                self.close()
        elif event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Tab):
            self._selected_idx = min(self._selected_idx + 1, len(self._filtered) - 1)
            self._render_results()
        elif event.key() == Qt.Key.Key_Up:
            self._selected_idx = max(self._selected_idx - 1, 0)
            self._render_results()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if 0 <= self._selected_idx < len(self._filtered):
                self._execute(self._filtered[self._selected_idx])
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        # Center on screen/parent
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + int(parent_rect.height() * 0.18)
            self.move(x, y)
        self._search.setFocus()


# ──────────────────────────────────────────────────────────────────────────────
# CommandRegistry — singleton global de comandos
# ──────────────────────────────────────────────────────────────────────────────
class CommandRegistry:
    _instance: Optional["CommandRegistry"] = None

    def __init__(self):
        self._commands: List[Command] = []
        self._palette: Optional[CommandPalette] = None
        self._search_provider: Optional[Callable[[str], List[Command]]] = None

    @classmethod
    def instance(cls) -> "CommandRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, cmd: Command):
        self._commands.append(cmd)

    def register_many(self, cmds: List[Command]):
        self._commands.extend(cmds)

    def set_search_provider(self, provider: Callable[[str], List[Command]]) -> None:
        """Define a fonte de resultados de cadastros para a busca global."""
        self._search_provider = provider

    def build_default_commands(self, navigate_fn: Callable, parent=None) -> List[Command]:
        """Cria os comandos padrão do sistema."""
        nav = navigate_fn
        cmds = [
            Command("dashboard",  "Dashboard",       "Painel principal",          "home",        "Navegação", ["painel","inicio","principal"],       lambda: nav("dashboard")),
            Command("operacoes",  "Nova Operação",   "Transferências SP→Cascavel", "operations",  "Navegação", ["operacao","transferencia","sp"],     lambda: nav("operacoes")),
            Command("notas",      "Notas Fiscais",   "Importar manifesto TXT",     "notes",       "Navegação", ["nota","cte","nfe","importar"],       lambda: nav("notas")),
            Command("criar_viagem","Criar Viagem",   "Montar nova viagem",         "truck",       "Navegação", ["viagem","frete","motorista"],        lambda: nav("criar_viagem")),
            Command("historico",  "Viagens",         "Histórico de viagens",       "trips",       "Navegação", ["historico","viagem","andamento"],    lambda: nav("historico")),
            Command("ranking_clientes","Ranking",    "Top clientes",               "ranking",     "Navegação", ["ranking","cliente","top"],           lambda: nav("ranking_clientes")),
            Command("combustivel","Combustível",     "Abastecimentos e consumo",   "fuel",        "Navegação", ["combustivel","gasolina","diesel"],   lambda: nav("combustivel")),
            Command("manutencao", "Manutenção",      "Frota e reparos",            "maintenance", "Navegação", ["manutencao","reparo","frota"],       lambda: nav("manutencao")),
            Command("contas",     "Contas",          "Contas a pagar/receber",     "accounts",    "Navegação", ["conta","financeiro","pagamento"],    lambda: nav("contas")),
            Command("relatorios", "Relatórios",      "Exportar PDF/Excel",         "reports",     "Navegação", ["relatorio","pdf","exportar"],        lambda: nav("relatorios")),
            Command("funcionarios","Funcionários",   "Equipe e folha de pag.",     "employees",   "Navegação", ["funcionario","equipe","folha"],      lambda: nav("funcionarios")),
            Command("configuracoes","Configurações", "Sistema e preferências",     "settings",    "Navegação", ["configuracao","tema","sistema"],     lambda: nav("configuracoes")),
            Command("minha_conta","Meu Perfil",      "Foto, senha, status",        "user",        "Conta",     ["perfil","foto","senha","status"],    lambda: nav("minha_conta")),
            Command("usuarios",   "Gerenciar Usuários","Usuários e permissões",    "admin",       "Admin",     ["usuario","permissao","acesso"],      lambda: nav("usuarios")),
            Command("auditoria",  "Auditoria",       "Registro de ações",          "audit",       "Admin",     ["auditoria","log","historico"],       lambda: nav("auditoria")),
        ]
        self._commands = cmds
        return cmds

    def open(self, parent=None, query: str = ""):
        """Abre a busca global, opcionalmente já filtrada por ``query``."""
        if self._palette and self._palette.isVisible():
            self._palette._search.setText(query)
            self._palette._search.setFocus()
            return
        self._palette = CommandPalette(self._commands, parent, self._search_provider)
        self._palette._search.setText(query)
        self._palette.show()


command_registry = CommandRegistry.instance()

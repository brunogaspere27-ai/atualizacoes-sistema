"""
Dashboard Aurora v2.0 - CW Transportadora
Redesenho premium com KPIs refinados, gráficos executivos e ranking visual.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QFrame, QLabel, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont

from services.auth_service import auth_service
from services.dashboard_service import dashboard_service
from services.ranking_service import ranking_service
from telas.theme_aurora import aurora_theme_manager, AccentColor
from utils.avatar import AvatarWidget
from utils.components_aurora import (
    AuroraCard,
    AuroraButton,
    AuroraKPICard,
    ButtonStyle,
    CardVariant,
    AuroraProgressBar,
)
from utils.charts_aurora import AuroraLineChart, AuroraBarChart, AuroraMultiLineChart
from utils.helpers import formatar_moeda, formatar_peso


def _growth_text(value: float) -> str:
    sinal = "+" if value >= 0 else ""
    return f"{sinal}{value:.1f}%"


class _TopClienteRow(QFrame):
    def __init__(self, posicao: int, cliente: dict, max_frete: float, parent=None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing

        nome = cliente.get("cliente", "Cliente não informado")
        frete = float(cliente.get("frete", 0) or 0)
        notas = int(cliente.get("total_notas", 0) or 0)
        peso = float(cliente.get("peso", 0) or 0)
        percentual = float(cliente.get("percentual_medio", 0) or 0)
        progresso = int((frete / max_frete) * 100) if max_frete > 0 else 0

        self.setStyleSheet(f"""
        QFrame {{
            background: {c['bg_surface']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_XL}px;
        }}
        QFrame:hover {{
            background: {c['card_hover']};
            border-color: {c['border_default']};
        }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        rank = QLabel(f"{posicao:02d}")
        rank.setFixedSize(38, 38)
        rank.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        rank.setStyleSheet(f"""
        QLabel {{
            background: {c['aurora_soft']};
            color: {c['aurora']};
            border: 1px solid {c['aurora']}33;
            border-radius: 12px;
        }}
        """)
        layout.addWidget(rank)

        initials = "".join([parte[0] for parte in nome.split()[:2]]).upper() or "C"
        avatar = QLabel(initials[:2])
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        avatar.setStyleSheet(f"""
        QLabel {{
            background: {c['ember_soft']};
            color: {c['ember']};
            border: 1px solid {c['ember']}33;
            border-radius: 14px;
        }}
        """)
        layout.addWidget(avatar)

        info_col = QVBoxLayout()
        info_col.setSpacing(6)
        title = QLabel(nome)
        title.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_MD, bold=True))
        title.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        subtitle = QLabel(f"{notas} notas  •  {formatar_peso(peso)}  •  frete médio {percentual:.1f}%")
        subtitle.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM))
        subtitle.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        bar = AuroraProgressBar(AccentColor.AURORA)
        bar.setValue(progresso)
        bar.setTextVisible(False)
        info_col.addWidget(title)
        info_col.addWidget(subtitle)
        info_col.addWidget(bar)
        layout.addLayout(info_col, 1)

        value_col = QVBoxLayout()
        value_col.setSpacing(4)
        value_col.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        amount = QLabel(formatar_moeda(frete))
        amount.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_XL, QFont.Weight.Bold))
        amount.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        share = QLabel(f"{progresso}% do líder")
        share.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        share.setStyleSheet(f"color: {c['aurora']}; background: transparent;")
        value_col.addWidget(amount)
        value_col.addWidget(share)
        layout.addLayout(value_col)


class _InsightRow(QFrame):
    def __init__(self, titulo: str, detalhe: str, tag: str, accent: str, parent=None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing

        self.setStyleSheet(f"""
        QFrame {{
            background: {c['bg_surface']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_LG}px;
        }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        head = QHBoxLayout()
        title = QLabel(titulo)
        title.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        title.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        badge = QLabel(tag)
        badge.setStyleSheet(f"""
        QLabel {{
            background: {accent}20;
            color: {accent};
            border: 1px solid {accent}33;
            border-radius: 10px;
            padding: 4px 8px;
            font-weight: 600;
        }}
        """)
        head.addWidget(title)
        head.addStretch()
        head.addWidget(badge)
        layout.addLayout(head)

        detail_lbl = QLabel(detalhe)
        detail_lbl.setWordWrap(True)
        detail_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM))
        detail_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        layout.addWidget(detail_lbl)


class DashboardAurora(QWidget):
    """Dashboard premium com tema unificado e leitura executiva."""

    PERIODOS = ["Geral", "Este Mês", "Mês Anterior", "Este Ano"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tipo_periodo = "Geral"
        self.executivo = {}
        self.legado = {}
        self.ranking_clientes = []
        self._setup_ui()
        self._load_data()

        self._auto_refresh = QTimer(self)
        self._auto_refresh.setInterval(60_000)
        self._auto_refresh.timeout.connect(self._load_data)
        self._auto_refresh.start()

    def _setup_ui(self):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 3px; min-height: 40px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0; }}
        """)
        main_layout.addWidget(self.scroll)

        self.content = QWidget()
        self.content.setStyleSheet(f"background: {c['bg_primary']};")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(t.SPACING_3XL, t.SPACING_XL, t.SPACING_3XL, t.SPACING_2XL)
        self.content_layout.setSpacing(t.SPACING_XL)
        self.scroll.setWidget(self.content)

        self._build_header()
        self._build_period_selector()
        self._build_kpis()
        self._build_charts()
        self._build_bottom_area()
        self._build_footer()

    def _build_header(self):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        usuario = auth_service.usuario_atual or {}

        card = AuroraCard(variant=CardVariant.GLASS, accent_color=AccentColor.AURORA)
        row = QHBoxLayout()
        row.setSpacing(t.SPACING_LG)

        avatar_wrap = QFrame()
        avatar_wrap.setMinimumSize(72, 72)
        avatar_wrap.setMaximumSize(72, 72)
        avatar_wrap.setStyleSheet(f"""
        QFrame {{
            background: {c['aurora_soft']};
            border: 1px solid {c['aurora']}22;
            border-radius: 24px;
        }}
        """)
        avatar_layout = QVBoxLayout(avatar_wrap)
        avatar_layout.setContentsMargins(4, 4, 4, 4)
        avatar_layout.addWidget(
            AvatarWidget(
                usuario_id=usuario.get("id"),
                nome=usuario.get("nome_completo", ""),
                tamanho=62,
            )
        )
        row.addWidget(avatar_wrap)

        texto = QVBoxLayout()
        texto.setSpacing(6)
        hora = datetime.now().hour
        saudacao = "Bom dia" if hora < 12 else "Boa tarde" if hora < 18 else "Boa noite"
        primeiro_nome = (usuario.get("nome_completo") or "Usuário").split()[0]
        titulo = QLabel(f"{saudacao}, {primeiro_nome}")
        titulo.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_3XL, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        subtitulo = QLabel("O dashboard executivo concentra receita, operação e ranking com a mesma linguagem visual do restante do sistema.")
        subtitulo.setWordWrap(True)
        subtitulo.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_MD))
        subtitulo.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        texto.addWidget(titulo)
        texto.addWidget(subtitulo)
        row.addLayout(texto, 1)

        status_col = QVBoxLayout()
        status_col.setSpacing(10)
        self._header_timestamp = QLabel()
        self._header_timestamp.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        self._header_timestamp.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")

        self._context_chip = QLabel("")
        self._context_chip.setStyleSheet(f"""
        QLabel {{
            background: {c['aurora_soft']};
            color: {c['aurora']};
            border: 1px solid {c['aurora']}33;
            border-radius: 12px;
            padding: 7px 12px;
            font-weight: 600;
        }}
        """)
        btn_refresh = AuroraButton("Atualizar", ButtonStyle.GHOST, "refresh")
        btn_refresh.setMinimumHeight(36)
        btn_refresh.clicked.connect(self._load_data)
        status_col.addWidget(self._header_timestamp, 0, Qt.AlignmentFlag.AlignRight)
        status_col.addWidget(self._context_chip, 0, Qt.AlignmentFlag.AlignRight)
        status_col.addWidget(btn_refresh, 0, Qt.AlignmentFlag.AlignRight)
        row.addLayout(status_col)

        card.add_layout(row)
        self.content_layout.addWidget(card)

    def _build_period_selector(self):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing

        row = QHBoxLayout()
        row.setSpacing(t.SPACING_MD)
        self._period_buttons = []

        label = QLabel("Período")
        label.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        label.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        row.addWidget(label)

        for periodo in self.PERIODOS:
            btn = QPushButton(periodo)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(38)
            btn.clicked.connect(lambda checked=False, p=periodo: self._on_periodo_changed(p))
            row.addWidget(btn)
            self._period_buttons.append((btn, periodo))

        row.addStretch()
        self.content_layout.addLayout(row)
        self._update_period_buttons()

    def _build_kpis(self):
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(16)

        self.kpi_receita = AuroraKPICard("Receita total", "R$ 0,00", "+0.0%", "dollar_sign", AccentColor.FOREST)
        self.kpi_fretes = AuroraKPICard("Fretes finalizados", "0", "+0.0%", "truck", AccentColor.AURORA)
        self.kpi_ticket = AuroraKPICard("Ticket médio", "R$ 0,00", "+0.0%", "trending_up", AccentColor.OCEAN)
        self.kpi_lucro = AuroraKPICard("Lucro estimado", "R$ 0,00", "+0.0%", "piggy_bank", AccentColor.SUNSET)

        for idx, widget in enumerate([self.kpi_receita, self.kpi_fretes, self.kpi_ticket, self.kpi_lucro]):
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            grid.addWidget(widget, 0, idx)

        wrapper = QWidget()
        wrapper.setLayout(grid)
        self.content_layout.addWidget(wrapper)

    def _build_charts(self):
        t = aurora_cw_theme.spacing

        row = QHBoxLayout()
        row.setSpacing(t.SPACING_XL)

        self.card_financeiro = AuroraCard(
            "Receita, despesa e lucro",
            "chart",
            variant=CardVariant.GLOW,
            accent_color=AccentColor.AURORA,
        )
        self.chart_comparativo = AuroraMultiLineChart(
            [AccentColor.AURORA, AccentColor.SUNSET, AccentColor.FOREST]
        )
        self.chart_comparativo.setMinimumHeight(180)  # Reduzido de 300 para 180 (40%)
        self.card_financeiro.add_widget(self.chart_comparativo)
        row.addWidget(self.card_financeiro, 3)

        side_col = QVBoxLayout()
        side_col.setSpacing(t.SPACING_MD)

        self.card_receita = AuroraCard(
            "Receita mensal",
            "trending-up",
            variant=CardVariant.GLOW,
            accent_color=AccentColor.FOREST,
        )
        self.chart_receita = AuroraLineChart(AccentColor.FOREST)
        self.chart_receita.setMinimumHeight(120)  # Reduzido de 178 para 120
        self.card_receita.add_widget(self.chart_receita)
        side_col.addWidget(self.card_receita)

        self.card_fretes = AuroraCard(
            "Operação mensal",
            "bar-chart",
            variant=CardVariant.GLOW,
            accent_color=AccentColor.OCEAN,
        )
        self.chart_fretes = AuroraBarChart(AccentColor.OCEAN)
        self.chart_fretes.setMinimumHeight(120)  # Reduzido de 178 para 120
        self.card_fretes.add_widget(self.chart_fretes)
        side_col.addWidget(self.card_fretes)

        row.addLayout(side_col, 2)
        self.content_layout.addLayout(row)

    def _build_bottom_area(self):
        t = aurora_cw_theme.spacing

        row = QHBoxLayout()
        row.setSpacing(t.SPACING_XL)

        self.card_clientes = AuroraCard(
            "Top clientes",
            "trophy",
            variant=CardVariant.DEFAULT,
            accent_color=AccentColor.EMBER,
        )
        self._clientes_layout = QVBoxLayout()
        self._clientes_layout.setContentsMargins(0, 0, 0, 0)
        self._clientes_layout.setSpacing(10)
        self.card_clientes.add_layout(self._clientes_layout)
        row.addWidget(self.card_clientes, 3)

        self.card_insights = AuroraCard(
            "Radar operacional",
            "sparkles",
            variant=CardVariant.BORDERED,
            accent_color=AccentColor.AURORA,
        )
        self._insights_layout = QVBoxLayout()
        self._insights_layout.setContentsMargins(0, 0, 0, 0)
        self._insights_layout.setSpacing(10)
        self.card_insights.add_layout(self._insights_layout)
        row.addWidget(self.card_insights, 2)

        self.content_layout.addLayout(row)

    def _build_footer(self):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        footer = QLabel("© 2026 CW Transportadora")
        footer.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM))
        footer.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(footer)

    def _current_context(self):
        now = datetime.now()
        if self.tipo_periodo == "Este Mês":
            return "Mês", now.strftime("%m"), now.strftime("%Y"), "Mês atual"
        if self.tipo_periodo == "Mês Anterior":
            prev = (now.replace(day=1) - timedelta(days=1))
            return "Mês", prev.strftime("%m"), prev.strftime("%Y"), f"Mês anterior • {prev.strftime('%m/%Y')}"
        if self.tipo_periodo == "Este Ano":
            return "Ano", "", now.strftime("%Y"), f"Ano {now.strftime('%Y')}"
        return "Geral", "", now.strftime("%Y"), "Base consolidada"

    def _on_periodo_changed(self, periodo: str):
        self.tipo_periodo = periodo
        self._update_period_buttons()
        self._load_data()

    def _update_period_buttons(self):
        c = aurora_cw_theme.colors
        for btn, periodo in self._period_buttons:
            active = periodo == self.tipo_periodo
            btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['aurora'] if active else 'transparent'};
                color: {'#FFFFFF' if active else c['text_secondary']};
                border: 1px solid {c['aurora'] if active else c['border_default']};
                border-radius: 12px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {c['aurora_hover'] if active else c['aurora_soft']};
                color: {c['text_primary'] if not active else '#FFFFFF'};
                border-color: {c['aurora']};
            }}
            """)

    def _load_data(self):
        tipo, mes, ano, rotulo = self._current_context()
        self._context_chip.setText(rotulo)
        self._header_timestamp.setText(f"Atualizado às {datetime.now().strftime('%H:%M')}  •  visão {rotulo.lower()}")

        try:
            self.executivo = dashboard_service.carregar_dashboard_executivo(tipo, mes, ano)
            self.legado = dashboard_service.carregar_dashboard(tipo, mes, ano)
            self.ranking_clientes = ranking_service.carregar_ranking(tipo, mes, ano)[:12]
            self._update_ui(ano)
        except Exception as exc:
            self._render_fallback(str(exc))

    def _kpi(self, nome: str) -> dict:
        return (self.executivo.get("kpis") or {}).get(nome, {"valor": 0, "crescimento": 0})

    def _update_ui(self, ano: str):
        receita = float(self._kpi("receita_total").get("valor", 0) or 0)
        fretes = float(self._kpi("fretes_realizados").get("valor", 0) or 0)
        lucro = float(self._kpi("lucro_estimado").get("valor", 0) or 0)
        ticket = receita / fretes if fretes else 0

        self.kpi_receita.set_value(formatar_moeda(receita))
        self.kpi_receita.set_change(_growth_text(float(self._kpi("receita_total").get("crescimento", 0) or 0)))

        self.kpi_fretes.set_value(str(int(fretes)))
        self.kpi_fretes.set_change(_growth_text(float(self._kpi("fretes_realizados").get("crescimento", 0) or 0)))

        ticket_growth = float(self._kpi("valor_recebido").get("crescimento", 0) or 0)
        self.kpi_ticket.set_value(formatar_moeda(ticket))
        self.kpi_ticket.set_change(_growth_text(ticket_growth))

        self.kpi_lucro.set_value(formatar_moeda(lucro))
        self.kpi_lucro.set_change(_growth_text(float(self._kpi("lucro_estimado").get("crescimento", 0) or 0)))

        comparativo = self.executivo.get("comparativo") or {"receitas": [], "despesas": [], "lucros": [], "labels": []}
        labels = comparativo.get("labels") or []
        receitas = comparativo.get("receitas") or []
        despesas = comparativo.get("despesas") or []
        lucros = comparativo.get("lucros") or []

        x_data = list(range(len(labels)))
        if x_data:
            self.chart_comparativo.set_data(
                [
                    (x_data, receitas),
                    (x_data, despesas),
                    (x_data, lucros),
                ],
                labels=["Receita", "Despesa", "Lucro"],
            )
            spark = receitas[-10:] if len(receitas) >= 2 else [0, 0]
            self.kpi_receita.set_sparkline_data(spark)
            self.kpi_fretes.set_sparkline_data((self.executivo.get("fretes") or {}).get("valores", [])[-10:] or [0, 0])
            self.kpi_ticket.set_sparkline_data((self.executivo.get("combustivel") or {}).get("medias", [])[-10:] or [0, 0])
            self.kpi_lucro.set_sparkline_data(lucros[-10:] if len(lucros) >= 2 else [0, 0])

        receita_mensal = self.executivo.get("receita") or {"valores": [], "labels": []}
        y_receita = receita_mensal.get("valores") or []
        if y_receita:
            self.chart_receita.set_data(list(range(len(y_receita))), y_receita, f"Receita {ano}")

        fretes_mensal = self.executivo.get("fretes") or {"valores": [], "labels": []}
        y_fretes = fretes_mensal.get("valores") or []
        if y_fretes:
            self.chart_fretes.set_data(list(range(len(y_fretes))), y_fretes, fretes_mensal.get("labels") or [])

        self._render_top_clientes()
        self._render_insights()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout(child_layout)

    def _render_top_clientes(self):
        self._clear_layout(self._clientes_layout)
        if not self.ranking_clientes:
            vazio = QLabel("Nenhum cliente encontrado para o período selecionado.")
            vazio.setStyleSheet(f"color: {aurora_cw_theme.cw_theme.colors['text_tertiary']}; background: transparent;")
            self._clientes_layout.addWidget(vazio)
            return

        max_frete = max(float(item.get("frete", 0) or 0) for item in self.ranking_clientes) or 1
        for pos, cliente in enumerate(self.ranking_clientes, start=1):
            self._clientes_layout.addWidget(_TopClienteRow(pos, cliente, max_frete))

    def _render_insights(self):
        c = aurora_cw_theme.colors
        self._clear_layout(self._insights_layout)

        contas = dashboard_service.resumo_contas_receber_pagar(*self._current_context()[:3])
        manut = dashboard_service.resumo_manutencoes()
        combustivel = dashboard_service.resumo_combustivel_mes()
        atividades = dashboard_service.atividades_recentes(limite=3)

        receber = contas.get("Receber", {})
        pagar = contas.get("Pagar", {})

        blocos = [
            _InsightRow(
                "Recebimentos em aberto",
                f"Vencidas {formatar_moeda(receber.get('vencidas', 0))} • A vencer {formatar_moeda(receber.get('a_vencer', 0))}",
                "Financeiro",
                c["forest"],
            ),
            _InsightRow(
                "Contas a pagar",
                f"Vencidas {formatar_moeda(pagar.get('vencidas', 0))} • A vencer {formatar_moeda(pagar.get('a_vencer', 0))}",
                "Fluxo",
                c["crimson"],
            ),
            _InsightRow(
                "Frota e manutenção",
                f"{manut.get('atrasadas', 0)} atrasadas • {manut.get('agendadas', 0)} agendadas • combustível do mês {formatar_moeda(combustivel.get('total', 0))}",
                "Frota",
                c["ember"],
            ),
        ]

        for bloco in blocos:
            self._insights_layout.addWidget(bloco)

        for item in atividades:
            self._insights_layout.addWidget(
                _InsightRow(
                    item.get("titulo", "Atividade"),
                    item.get("detalhe", ""),
                    item.get("tipo", "Log"),
                    c["ocean"],
                )
            )

        self._insights_layout.addStretch()

    def _render_fallback(self, error_message: str):
        self.kpi_receita.set_value("—")
        self.kpi_fretes.set_value("—")
        self.kpi_ticket.set_value("—")
        self.kpi_lucro.set_value("—")
        self._clear_layout(self._clientes_layout)
        self._clear_layout(self._insights_layout)
        erro = QLabel(f"Não foi possível carregar o dashboard agora.\n{error_message}")
        erro.setWordWrap(True)
        erro.setStyleSheet(f"color: {aurora_cw_theme.cw_theme.colors['crimson']}; background: transparent;")
        self._clientes_layout.addWidget(erro)

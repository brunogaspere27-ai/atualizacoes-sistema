"""
Dashboard Executivo CW Transportadora - PySide6

Dashboard premium com KPIs financeiros/operacionais, gráficos pyqtgraph,
resumo de contas/combustível/manutenções, atividades recentes e próximas
entregas — layout inspirado em Linear (estrutura), Attio (cards) e Stripe
(gráficos).
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt

from services.dashboard_service import dashboard_service
from telas.theme_aurora import aurora_theme_manager, AccentColor
from utils.icons import get_pixmap
from utils.components import KPICard, ModernCard, ModernButton, ButtonStyle
from utils.charts import ChartCard, BarChart, DonutChart, MultiLineChart
from utils.helpers import formatar_moeda, formatar_peso


class Dashboard(QWidget):
    """Dashboard executivo moderno em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")

        self.kpis = {}
        self.fretes_status = []
        self.contas_resumo = {}
        self.combustivel_resumo = {}
        self.manutencoes_resumo = {}
        self.atividades = []
        self.entregas = []

        self._setup_ui()
        self._load_data()

    # ================================================================ UI
    def _setup_ui(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{ background: {colors['border_default']}; border-radius: 4px; min-height: 40px; }}
        QScrollBar::handle:vertical:hover {{ background: {colors['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0px; }}
        """)

        self.content = QWidget()
        self.content.setStyleSheet(f"background: {colors['bg_primary']};")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(tokens.SPACING_2XL, tokens.SPACING_XL, tokens.SPACING_2XL, tokens.SPACING_2XL)
        self.content_layout.setSpacing(tokens.SPACING_LG)
        self.content.setLayout(self.content_layout)
        self.scroll.setWidget(self.content)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        main_layout.addWidget(self.scroll)

        self._create_header()
        self._create_kpi_cards()
        self._create_charts()
        self._create_summary_cards()
        self._create_activity_section()

    def _create_header(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        header = QHBoxLayout()

        titulo_box = QVBoxLayout()
        titulo_box.setSpacing(2)
        titulo = QLabel("Olá, Administrador!")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        titulo_box.addWidget(titulo)

        subtitulo = QLabel("Aqui está o resumo geral da sua operação.")
        subtitulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        subtitulo.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        titulo_box.addWidget(subtitulo)

        header.addLayout(titulo_box)
        header.addStretch()

        lbl_periodo = QLabel("Período:")
        lbl_periodo.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        lbl_periodo.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        header.addWidget(lbl_periodo)

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo.setCurrentText(self.tipo_periodo)
        self.combo_periodo.setMinimumHeight(36)
        self.combo_periodo.setFixedWidth(130)
        self.combo_periodo.currentTextChanged.connect(self._update_period)
        header.addWidget(self.combo_periodo)

        self.content_layout.addLayout(header)

    def _create_kpi_cards(self):
        tokens = theme_manager.tokens

        cards_grid = QWidget()
        cards_grid.setStyleSheet("background: transparent;")
        cards_layout = QGridLayout()
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(tokens.SPACING_MD)
        for i in range(5):
            cards_layout.setColumnStretch(i, 1)
        cards_grid.setLayout(cards_layout)

        self.card_receita = KPICard("Receita Bruta", "R$ 0,00", icon_name="money", accent=AccentColor.AURORA)
        cards_layout.addWidget(self.card_receita, 0, 0)

        self.card_lucro = KPICard("Lucro Estimado", "R$ 0,00", icon_name="trending_up", accent=AccentColor.FOREST)
        cards_layout.addWidget(self.card_lucro, 0, 1)

        self.card_fretes_realizados = KPICard("Fretes Realizados", "0", icon_name="truck", accent=AccentColor.OCEAN)
        cards_layout.addWidget(self.card_fretes_realizados, 0, 2)

        self.card_fretes_andamento = KPICard("Fretes em Andamento", "0", icon_name="operations", accent=AccentColor.EMBER)
        cards_layout.addWidget(self.card_fretes_andamento, 0, 3)

        self.card_clientes = KPICard("Clientes Ativos", "0", icon_name="employees", accent=AccentColor.AURORA)
        cards_layout.addWidget(self.card_clientes, 0, 4)

        self.content_layout.addWidget(cards_grid)

    def _create_charts(self):
        tokens = theme_manager.tokens

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(tokens.SPACING_MD)

        self._chart_card_comparativo = ChartCard("Receita x Despesa")
        self._line_chart = MultiLineChart()
        self._chart_card_comparativo.set_chart_widget(self._line_chart)
        charts_layout.addWidget(self._chart_card_comparativo, stretch=3)

        self._chart_card_status = ChartCard("Fretes por Status")
        self._donut_chart = DonutChart()
        self._chart_card_status.set_chart_widget(self._donut_chart)
        charts_layout.addWidget(self._chart_card_status, stretch=2)

        self._chart_card_receita = ChartCard("Receita dos Últimos Meses")
        self._bar_chart = BarChart()
        self._chart_card_receita.set_chart_widget(self._bar_chart)
        charts_layout.addWidget(self._chart_card_receita, stretch=3)

        self.content_layout.addLayout(charts_layout)

    def _create_summary_cards(self):
        tokens = theme_manager.tokens

        row = QHBoxLayout()
        row.setSpacing(tokens.SPACING_MD)

        self.card_contas_receber = self._make_summary_card(
            "Contas a Receber", "financeiro"
        )
        row.addWidget(self.card_contas_receber, stretch=1)

        self.card_contas_pagar = self._make_summary_card(
            "Contas a Pagar", "financeiro"
        )
        row.addWidget(self.card_contas_pagar, stretch=1)

        self.card_combustivel = self._make_summary_card(
            "Combustível (Mês)", "combustivel"
        )
        row.addWidget(self.card_combustivel, stretch=1)

        self.card_manutencoes = self._make_summary_card(
            "Manutenções", "manutencao"
        )
        row.addWidget(self.card_manutencoes, stretch=1)

        self.content_layout.addLayout(row)

    def _make_summary_card(self, titulo: str, kind: str) -> QFrame:
        """Cria um card resumo com placeholders internos preenchidos depois."""
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        frame = QFrame()
        frame.setObjectName("summaryCard2")
        frame.setStyleSheet(f"""
        QFrame#summaryCard2 {{
            background: {colors['card_bg']}; border: 1px solid {colors['card_border']};
            border-radius: {tokens.RADIUS_LG}px;
        }}
        QFrame#summaryCard2:hover {{ border-color: {colors['border_strong']}; }}
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(tokens.SPACING_LG, tokens.SPACING_MD, tokens.SPACING_LG, tokens.SPACING_LG)
        layout.setSpacing(6)
        frame.setLayout(layout)

        title_lbl = QLabel(titulo.upper())
        title_lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS, bold=True))
        title_lbl.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        value_lbl = QLabel("R$ 0,00")
        value_lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_XL, bold=True))
        value_lbl.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        layout.addWidget(value_lbl)
        frame._value_label = value_lbl

        details_row = QHBoxLayout()
        details_row.setSpacing(tokens.SPACING_MD)

        detail_a = QVBoxLayout()
        detail_a.setSpacing(0)
        label_a = QLabel("")
        label_a.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS))
        label_a.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        value_a = QLabel("")
        value_a.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        value_a.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        detail_a.addWidget(label_a)
        detail_a.addWidget(value_a)
        details_row.addLayout(detail_a)
        frame._label_a = label_a
        frame._value_a = value_a

        detail_b = QVBoxLayout()
        detail_b.setSpacing(0)
        label_b = QLabel("")
        label_b.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS))
        label_b.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        value_b = QLabel("")
        value_b.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        value_b.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        detail_b.addWidget(label_b)
        detail_b.addWidget(value_b)
        details_row.addLayout(detail_b)
        frame._label_b = label_b
        frame._value_b = value_b

        details_row.addStretch()
        layout.addLayout(details_row)

        link = QLabel(f"Ver todas ›")
        link.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS, bold=True))
        link.setStyleSheet(f"color: {colors['brand']}; background: transparent;")
        layout.addWidget(link)

        return frame

    def _create_activity_section(self):
        tokens = theme_manager.tokens

        row = QHBoxLayout()
        row.setSpacing(tokens.SPACING_MD)

        atividades_card = ModernCard(title="Últimas Atividades", icon_name="history", padding=tokens.SPACING_LG)
        self.atividades_list = QWidget()
        self.atividades_list.setStyleSheet("background: transparent;")
        self.atividades_list_layout = QVBoxLayout()
        self.atividades_list_layout.setContentsMargins(0, 0, 0, 0)
        self.atividades_list_layout.setSpacing(tokens.SPACING_SM)
        self.atividades_list.setLayout(self.atividades_list_layout)
        atividades_card.add_widget(self.atividades_list)
        row.addWidget(atividades_card, stretch=1)

        entregas_card = ModernCard(title="Próximas Entregas", icon_name="truck", padding=tokens.SPACING_LG)
        self.entregas_list = QWidget()
        self.entregas_list.setStyleSheet("background: transparent;")
        self.entregas_list_layout = QVBoxLayout()
        self.entregas_list_layout.setContentsMargins(0, 0, 0, 0)
        self.entregas_list_layout.setSpacing(tokens.SPACING_SM)
        self.entregas_list.setLayout(self.entregas_list_layout)
        entregas_card.add_widget(self.entregas_list)
        row.addWidget(entregas_card, stretch=1)

        self.content_layout.addLayout(row)

    # ================================================================ Data
    def _load_data(self):
        self.kpis = dashboard_service.calcular_kpis(self.tipo_periodo, self.mes, self.ano)
        self.fretes_status = dashboard_service.resumo_fretes_status(self.tipo_periodo, self.mes, self.ano)
        self.contas_resumo = dashboard_service.resumo_contas_receber_pagar(self.tipo_periodo, self.mes, self.ano)
        self.combustivel_resumo = dashboard_service.resumo_combustivel_mes()
        self.manutencoes_resumo = dashboard_service.resumo_manutencoes()
        self.atividades = dashboard_service.atividades_recentes(4)
        self.entregas = dashboard_service.proximas_entregas(3)

        ano_grafico = self.ano or datetime.now().strftime("%Y")
        self.grafico_comparativo = dashboard_service.dados_graficos_comparativo_mensal(ano_grafico)
        self.grafico_receita = dashboard_service.dados_graficos_receita_mensal(ano_grafico)

        self._update_ui()

    def _fmt_trend(self, crescimento: float) -> str:
        seta = "↑" if crescimento >= 0 else "↓"
        return f"{seta} {abs(crescimento):.1f}% vs período anterior"

    def _update_ui(self):
        k = self.kpis

        self.card_receita.set_value(formatar_moeda(k.get("receita_total", {}).get("valor", 0)))
        self.card_receita.set_trend(self._fmt_trend(k.get("receita_total", {}).get("crescimento", 0)))

        self.card_lucro.set_value(formatar_moeda(k.get("lucro_estimado", {}).get("valor", 0)))
        self.card_lucro.set_trend(self._fmt_trend(k.get("lucro_estimado", {}).get("crescimento", 0)))

        self.card_fretes_realizados.set_value(str(int(k.get("fretes_realizados", {}).get("valor", 0))))
        self.card_fretes_realizados.set_trend(self._fmt_trend(k.get("fretes_realizados", {}).get("crescimento", 0)))

        self.card_fretes_andamento.set_value(str(int(k.get("fretes_andamento", {}).get("valor", 0))))
        self.card_fretes_andamento.set_trend(self._fmt_trend(k.get("fretes_andamento", {}).get("crescimento", 0)))

        self.card_clientes.set_value(str(int(k.get("clientes_ativos", {}).get("valor", 0))))
        self.card_clientes.set_trend(self._fmt_trend(k.get("clientes_ativos", {}).get("crescimento", 0)))

        self._atualizar_grafico_comparativo()
        self._atualizar_grafico_status()
        self._atualizar_grafico_receita()

        self._atualizar_card_contas(self.card_contas_receber, self.contas_resumo.get("Receber", {}))
        self._atualizar_card_contas(self.card_contas_pagar, self.contas_resumo.get("Pagar", {}))
        self._atualizar_card_combustivel()
        self._atualizar_card_manutencoes()

        self._update_atividades()
        self._update_entregas()

    def _atualizar_grafico_comparativo(self):
        colors = theme_manager.colors
        dados = self.grafico_comparativo or {}
        labels = dados.get("labels", [])
        receitas = dados.get("receitas", [])
        despesas = dados.get("despesas", [])
        self._line_chart.set_series(labels, [
            ("Receita", receitas, colors["success"]),
            ("Despesa", despesas, colors["error"]),
        ])

    def _atualizar_grafico_status(self):
        total = sum(v for _, v in self.fretes_status) or 0
        data = [(label, valor) for label, valor in self.fretes_status if valor > 0]
        center = str(total) if total else "0"
        self._donut_chart.set_data(data if data else [("Sem dados", 1)], center_text=center)

    def _atualizar_grafico_receita(self):
        dados = self.grafico_receita or {}
        labels = dados.get("labels", [])
        valores = dados.get("valores", [])
        # Últimos 6 meses até o mês atual
        mes_atual = int(datetime.now().strftime("%m"))
        inicio = max(0, mes_atual - 6)
        self._bar_chart.set_data(labels[inicio:mes_atual], valores[inicio:mes_atual])

    def _atualizar_card_contas(self, frame: QFrame, dados: dict):
        vencidas = dados.get("vencidas", 0)
        a_vencer = dados.get("a_vencer", 0)
        total = dados.get("total", vencidas + a_vencer)
        frame._value_label.setText(formatar_moeda(total))
        frame._label_a.setText("Vencidas")
        frame._value_a.setText(formatar_moeda(vencidas))
        frame._label_b.setText("A vencer")
        frame._value_b.setText(formatar_moeda(a_vencer))

    def _atualizar_card_combustivel(self):
        frame = self.card_combustivel
        dados = self.combustivel_resumo
        frame._value_label.setText(formatar_moeda(dados.get("total", 0)))
        frame._label_a.setText("Total (L)")
        frame._value_a.setText(f"{dados.get('litros', 0):.2f}")
        frame._label_b.setText("Média (R$/L)")
        frame._value_b.setText(formatar_moeda(dados.get("media_litro", 0)))

    def _atualizar_card_manutencoes(self):
        frame = self.card_manutencoes
        dados = self.manutencoes_resumo
        frame._value_label.setText(str(dados.get("total", 0)))
        frame._label_a.setText("Atrasadas")
        frame._value_a.setText(str(dados.get("atrasadas", 0)))
        frame._label_b.setText("Agendadas")
        frame._value_b.setText(str(dados.get("agendadas", 0)))

    def _update_atividades(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        for i in reversed(range(self.atividades_list_layout.count())):
            child = self.atividades_list_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        if not self.atividades:
            placeholder = QLabel("Nenhuma atividade recente")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
            placeholder.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
            self.atividades_list_layout.addWidget(placeholder)
            return

        badge_colors = {
            "Fretes": ("sky", "sky_soft"),
            "Coletas": ("emerald", "emerald_soft"),
            "Manutenção": ("amber", "amber_soft"),
        }

        for item in self.atividades:
            frame = QFrame()
            frame.setStyleSheet(f"""
            QFrame {{
                background: {colors['bg_tertiary']}; border: 1px solid {colors['border_subtle']};
                border-radius: {tokens.RADIUS_MD}px;
            }}
            QFrame:hover {{ border-color: {colors['border_strong']}; }}
            """)
            il = QHBoxLayout()
            il.setContentsMargins(tokens.SPACING_MD, tokens.SPACING_SM, tokens.SPACING_MD, tokens.SPACING_SM)
            il.setSpacing(tokens.SPACING_SM)
            frame.setLayout(il)

            text_box = QVBoxLayout()
            text_box.setSpacing(2)
            titulo = QLabel(item.get("titulo", ""))
            titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
            titulo.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
            text_box.addWidget(titulo)

            detalhe = QLabel(item.get("detalhe", ""))
            detalhe.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS))
            detalhe.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
            text_box.addWidget(detalhe)
            il.addLayout(text_box, stretch=1)

            tipo = item.get("tipo", "")
            key_bg, key_soft = badge_colors.get(tipo, ("brand", "brand_soft"))
            badge = QLabel(tipo)
            badge.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS, bold=True))
            badge.setStyleSheet(f"""
            color: {colors[key_bg]}; background: {colors[key_soft]};
            border-radius: {tokens.RADIUS_SM}px; padding: 2px 8px;
            """)
            il.addWidget(badge)

            self.atividades_list_layout.addWidget(frame)

    def _update_entregas(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        for i in reversed(range(self.entregas_list_layout.count())):
            child = self.entregas_list_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        if not self.entregas:
            placeholder = QLabel("Nenhuma entrega em andamento")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
            placeholder.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
            self.entregas_list_layout.addWidget(placeholder)
            return

        for item in self.entregas:
            frame = QFrame()
            frame.setStyleSheet(f"""
            QFrame {{
                background: {colors['bg_tertiary']}; border: 1px solid {colors['border_subtle']};
                border-radius: {tokens.RADIUS_MD}px;
            }}
            QFrame:hover {{ border-color: {colors['border_strong']}; }}
            """)
            il = QHBoxLayout()
            il.setContentsMargins(tokens.SPACING_MD, tokens.SPACING_SM, tokens.SPACING_MD, tokens.SPACING_SM)
            il.setSpacing(tokens.SPACING_SM)
            frame.setLayout(il)

            text_box = QVBoxLayout()
            text_box.setSpacing(2)
            titulo = QLabel(f"{item.get('quando', '')} - {item.get('titulo', '')}")
            titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
            titulo.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
            text_box.addWidget(titulo)

            detalhe = QLabel(item.get("detalhe", ""))
            detalhe.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS))
            detalhe.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
            text_box.addWidget(detalhe)
            il.addLayout(text_box, stretch=1)

            status = item.get("status", "")
            badge = QLabel(status)
            badge.setFont(theme_manager.get_font(tokens.FONT_SIZE_XS, bold=True))
            badge.setStyleSheet(f"""
            color: {colors['sky']}; background: {colors['sky_soft']};
            border-radius: {tokens.RADIUS_SM}px; padding: 2px 8px;
            """)
            il.addWidget(badge)

            self.entregas_list_layout.addWidget(frame)

    def _update_period(self):
        self.tipo_periodo = self.combo_periodo.currentText()
        self._load_data()

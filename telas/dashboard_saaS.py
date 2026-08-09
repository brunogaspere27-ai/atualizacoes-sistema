"""
Dashboard SaaS Premium v2.0 - CW Transportadora
Dashboard inspirado em Linear, Stripe, ClickUp, Vercel, Notion, Framer

Features:
- Layout SaaS premium
- Cards com cantos 18-20px
- Fundo #151515
- Borda #262626
- Gráficos estilo Stripe
- Espaçamento generoso
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QComboBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from config.settings import settings
from services.dashboard_service import dashboard_service
from services.auth_service import auth_service
from telas.theme_saaS import saas_theme
from utils.components_saaS import (
    SaaSCard, SaaSButton, SaaSKPICard, SaaSTable,
)
from utils.helpers import formatar_moeda, formatar_peso
from utils.avatar import AvatarWidget


class DashboardSaaS(QWidget):
    """Dashboard premium estilo SaaS."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")
        self.dados = {}
        self.top_destinos = []
        self.ranking_clientes = []
        self.extras = {}
        self._setup_ui()
        self._load_data()
        # Auto-refresh a cada 60s
        self._auto_refresh = QTimer(self)
        self._auto_refresh.setInterval(60_000)
        self._auto_refresh.timeout.connect(self._load_data)
        self._auto_refresh.start()

    def _setup_ui(self):
        c = saas_theme.COLORS
        t = saas_theme

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 4px; min-height: 40px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0; }}
        """)

        self.content = QWidget()
        self.content.setStyleSheet(f"background: {c['bg_primary']};")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(t.SPACING_3XL, t.SPACING_XL, t.SPACING_3XL, t.SPACING_2XL)
        self.content_layout.setSpacing(t.SPACING_2XL)
        self.content.setLayout(self.content_layout)
        self.scroll.setWidget(self.content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll)

        self._create_header()
        self._create_kpi_row()
        self._create_charts_section()
        self._create_rankings()

    def _create_header(self):
        c = saas_theme.COLORS
        t = saas_theme

        usuario = auth_service.usuario_atual or {}
        hora = datetime.now().hour
        saudacao = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")
        nome = usuario.get("nome_completo", "").split()[0] if usuario.get("nome_completo") else "Usuário"

        dias_pt = ["Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira",
                   "Sexta-feira","Sábado","Domingo"]
        meses_pt = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                    "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        now = datetime.now()
        data_str = f"{dias_pt[now.weekday()]}, {now.day} de {meses_pt[now.month-1]} de {now.year}"

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(t.SPACING_LG)
        header.setLayout(hl)

        # Avatar
        uid = usuario.get("id")
        avatar_w = AvatarWidget(usuario_id=uid, nome=usuario.get("nome_completo",""), tamanho=48)
        hl.addWidget(avatar_w)

        greet_col = QVBoxLayout()
        greet_col.setContentsMargins(0, 0, 0, 0)
        greet_col.setSpacing(4)

        greet_lbl = QLabel(f"{saudacao}, {nome}")
        greet_lbl.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_2XL, QFont.Weight.Bold))
        greet_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        greet_col.addWidget(greet_lbl)

        date_lbl = QLabel(data_str)
        date_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_MD))
        date_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        greet_col.addWidget(date_lbl)

        hl.addLayout(greet_col)
        hl.addStretch()

        # Refresh button
        btn_refresh = SaaSButton("Atualizar", "default", "refresh")
        btn_refresh.clicked.connect(self._load_data)
        hl.addWidget(btn_refresh)

        self.content_layout.addWidget(header)

    def _create_kpi_row(self):
        c = saas_theme.COLORS
        t = saas_theme

        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(t.SPACING_XL)
        kpi_grid.setContentsMargins(0, 0, 0, 0)

        # KPI 1: Receita Total
        self.kpi_receita = SaaSKPICard(
            "Receita Total",
            "R$ 0,00",
            "+12.5%",
            "trending-up"
        )
        kpi_grid.addWidget(self.kpi_receita, 0, 0)

        # KPI 2: Viagens
        self.kpi_viagens = SaaSKPICard(
            "Viagens Realizadas",
            "0",
            "+8.2%",
            "truck"
        )
        kpi_grid.addWidget(self.kpi_viagens, 0, 1)

        # KPI 3: Carga Transportada
        self.kpi_carga = SaaSKPICard(
            "Carga Transportada",
            "0 kg",
            "+15.3%",
            "package"
        )
        kpi_grid.addWidget(self.kpi_carga, 0, 2)

        # KPI 4: Margem Líquida
        self.kpi_margem = SaaSKPICard(
            "Margem Líquida",
            "0%",
            "+2.1%",
            "percent"
        )
        kpi_grid.addWidget(self.kpi_margem, 0, 3)

        kpi_container = QWidget()
        kpi_container.setLayout(kpi_grid)
        self.content_layout.addWidget(kpi_container)

    def _create_charts_section(self):
        c = saas_theme.COLORS
        t = saas_theme

        charts_row = QHBoxLayout()
        charts_row.setSpacing(t.SPACING_2XL)

        # Chart Card 1: Receita Mensal
        chart1_card = SaaSCard("Receita Mensal", "trending-up")
        chart1_layout = QVBoxLayout()
        chart1_layout.setContentsMargins(0, 0, 0, 0)
        chart1_layout.setSpacing(t.SPACING_MD)

        # Placeholder para gráfico
        chart_placeholder = QLabel()
        chart_placeholder.setMinimumHeight(280)
        chart_placeholder.setStyleSheet(f"""
        QLabel {{
            background: {c['bg_tertiary']};
            border-radius: {t.RADIUS_XL}px;
            border: 1px dashed {c['border_default']};
            color: {c['text_tertiary']};
        }}
        """)
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setText("📊 Gráfico de Receita\n(em desenvolvimento)")
        chart_placeholder.setFont(saas_theme.get_font(t.FONT_SIZE_MD))

        chart1_layout.addWidget(chart_placeholder)
        chart1_card.add_layout(chart1_layout)
        charts_row.addWidget(chart1_card, 2)

        # Chart Card 2: Viagens por Destino
        chart2_card = SaaSCard("Top Destinos", "map-pin")
        chart2_layout = QVBoxLayout()
        chart2_layout.setContentsMargins(0, 0, 0, 0)
        chart2_layout.setSpacing(t.SPACING_MD)

        chart2_placeholder = QLabel()
        chart2_placeholder.setMinimumHeight(280)
        chart2_placeholder.setStyleSheet(f"""
        QLabel {{
            background: {c['bg_tertiary']};
            border-radius: {t.RADIUS_XL}px;
            border: 1px dashed {c['border_default']};
            color: {c['text_tertiary']};
        }}
        """)
        chart2_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart2_placeholder.setText("📍 Mapa de Destinos\n(em desenvolvimento)")
        chart2_placeholder.setFont(saas_theme.get_font(t.FONT_SIZE_MD))

        chart2_layout.addWidget(chart2_placeholder)
        chart2_card.add_layout(chart2_layout)
        charts_row.addWidget(chart2_card, 1)

        self.content_layout.addLayout(charts_row)

    def _create_rankings(self):
        c = saas_theme.COLORS
        t = saas_theme

        ranking_card = SaaSCard("Ranking de Clientes", "trophy")
        ranking_layout = QVBoxLayout()
        ranking_layout.setContentsMargins(0, 0, 0, 0)
        ranking_layout.setSpacing(t.SPACING_MD)

        # Tabela de ranking
        self.ranking_table = SaaSTable()
        self.ranking_table.setColumnCount(4)
        self.ranking_table.setHorizontalHeaderLabels(["Cliente", "Viagens", "Receita", "Margem"])
        self.ranking_table.setMinimumHeight(350)

        ranking_layout.addWidget(self.ranking_table)
        ranking_card.add_layout(ranking_layout)

        self.content_layout.addWidget(ranking_card)

    def _load_data(self):
        """Carrega dados do dashboard."""
        try:
            self.dados = dashboard_service.obter_kpis(
                periodo=self.tipo_periodo,
                mes=self.mes,
                ano=self.ano
            )
            self.top_destinos = dashboard_service.obter_top_destinos(
                periodo=self.tipo_periodo,
                mes=self.mes,
                ano=self.ano,
                limite=5
            )
            self.ranking_clientes = dashboard_service.obter_ranking_clientes(
                periodo=self.tipo_periodo,
                mes=self.mes,
                ano=self.ano,
                limite=10
            )
            self.extras = dashboard_service.obter_extras(
                periodo=self.tipo_periodo,
                mes=self.mes,
                ano=self.ano
            )
            self._update_ui()
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")

    def _update_ui(self):
        """Atualiza UI com dados carregados."""
        c = saas_theme.COLORS

        # Atualizar KPIs
        receita = self.dados.get("receita_total", 0)
        for child in self.kpi_receita.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(formatar_moeda(receita))
                break

        viagens = self.dados.get("total_viagens", 0)
        for child in self.kpi_viagens.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(str(viagens))
                break

        carga = self.dados.get("carga_total", 0)
        for child in self.kpi_carga.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(formatar_peso(carga))
                break

        margem = self.dados.get("margem_liquida", 0)
        for child in self.kpi_margem.findChildren(QLabel):
            if child.font().bold() and child.font().pointSize() > 20:
                child.setText(f"{margem:.1f}%")
                break

        # Atualizar tabela de ranking
        self.ranking_table.setRowCount(0)
        for idx, cliente in enumerate(self.ranking_clientes):
            self.ranking_table.insertRow(idx)
            self.ranking_table.setItem(idx, 0, QTableWidgetItem(cliente.get("nome", "")))
            self.ranking_table.setItem(idx, 1, QTableWidgetItem(str(cliente.get("viagens", 0))))
            self.ranking_table.setItem(idx, 2, QTableWidgetItem(formatar_moeda(cliente.get("receita", 0))))
            self.ranking_table.setItem(idx, 3, QTableWidgetItem(f"{cliente.get('margem', 0):.1f}%"))

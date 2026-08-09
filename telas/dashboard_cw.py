"""
Dashboard Executivo CW Transportadora - Design System CW
Dashboard premium com KPIs financeiros/operacionais e gráficos reais
Inspiração: Linear, Stripe, Attio
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt

from ui.theme.cw_theme import cw_theme, CWSpacing
from ui.components import (
    KPICard, CWCard, CWButton, ButtonVariant, ButtonSize,
    CWChartCard, ChartType, CWEmptyState
)
from utils.helpers import formatar_moeda, formatar_peso
from services.dashboard_service import DashboardService


class DashboardCW(QWidget):
    """Dashboard executivo com Design System CW e dados reais."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")

        self.dashboard_service = DashboardService()
        self.kpis = {}
        self.chart_data = {}
        self.contas_resumo = {}
        self.combustivel_resumo = {}
        self.manutencoes_resumo = {}
        self.atividades = []

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura UI com Design System CW."""
        c = cw_theme.colors
        t = cw_theme.spacing

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{ background: {c['border_subtle']}; border-radius: 4px; min-height: 40px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['border_default']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0px; }}
        """)

        # Content area
        self.content = QWidget()
        self.content.setStyleSheet(f"background: {c['bg_primary']};")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(t._2XL, t.XL, t._2XL, t._2XL)
        self.content_layout.setSpacing(t.LG)
        self.content.setLayout(self.content_layout)
        self.scroll.setWidget(self.content)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        main_layout.addWidget(self.scroll)

        # Criar seções
        self._create_header()
        self._create_kpi_cards()
        self._create_charts_section()
        self._create_summary_cards()
        self._create_activity_section()

    def _create_header(self):
        """Cria header do dashboard."""
        c = cw_theme.colors
        t = cw_theme.spacing

        header = QHBoxLayout()

        # Título
        titulo_box = QVBoxLayout()
        titulo_box.setSpacing(t.XS)
        
        titulo = QLabel("Olá, Administrador!")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        titulo_box.addWidget(titulo)

        subtitulo = QLabel("Aqui está o resumo geral da sua operação.")
        subtitulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        subtitulo.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        titulo_box.addWidget(subtitulo)

        header.addLayout(titulo_box, 1)

        # Seletor de período
        self.periodo_combo = QComboBox()
        self.periodo_combo.addItems(["Geral", "Mês Atual", "Mês Anterior"])
        self.periodo_combo.setCurrentText(self.tipo_periodo)
        self.periodo_combo.setStyleSheet(f"""
        QComboBox {{
            background-color: {c['bg_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {cw_theme.radius.MD}px;
            padding: {t.SM}px {t.MD}px;
            font-size: {cw_theme.typography.FONT_SIZE_SM}px;
            color: {c['text_primary']};
            min-width: 150px;
        }}
        QComboBox:hover {{
            border-color: {c['border_strong']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {c['text_secondary']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['bg_primary']};
            border: 1px solid {c['border_default']};
            selection-background-color: {c['primary_soft']};
            selection-color: {c['primary']};
        }}
        """)
        self.periodo_combo.currentTextChanged.connect(self._on_periodo_changed)
        header.addWidget(self.periodo_combo)

        self.content_layout.addLayout(header)

    def _create_kpi_cards(self):
        """Cria cards de KPIs com dados reais."""
        c = cw_theme.colors
        t = cw_theme.spacing

        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(t.LG)

        # KPI: Receita Total
        receita_data = self.kpis.get('receita_total', {})
        receita_valor = receita_data.get('valor', 0)
        receita_crescimento = receita_data.get('crescimento', 0)
        
        self.kpi_receita = KPICard(
            title="Receita Total",
            value=formatar_moeda(receita_valor),
            subtitle="No período selecionado",
            trend=f"+{receita_crescimento:.1f}%" if receita_crescimento >= 0 else f"{receita_crescimento:.1f}%",
            trend_positive=receita_crescimento >= 0
        )
        kpi_layout.addWidget(self.kpi_receita, 0, 0)

        # KPI: Lucro Estimado
        lucro_data = self.kpis.get('lucro_estimado', {})
        lucro_valor = lucro_data.get('valor', 0)
        lucro_crescimento = lucro_data.get('crescimento', 0)
        
        self.kpi_lucro = KPICard(
            title="Lucro Estimado",
            value=formatar_moeda(lucro_valor),
            subtitle="Margem operacional",
            trend=f"+{lucro_crescimento:.1f}%" if lucro_crescimento >= 0 else f"{lucro_crescimento:.1f}%",
            trend_positive=lucro_crescimento >= 0
        )
        kpi_layout.addWidget(self.kpi_lucro, 0, 1)

        # KPI: Fretes Realizados
        fretes_data = self.kpis.get('fretes_realizados', {})
        fretes_valor = fretes_data.get('valor', 0)
        fretes_crescimento = fretes_data.get('crescimento', 0)
        
        self.kpi_fretes = KPICard(
            title="Fretes Realizados",
            value=str(int(fretes_valor)),
            subtitle="Viagens concluídas",
            trend=f"+{fretes_crescimento:.1f}%" if fretes_crescimento >= 0 else f"{fretes_crescimento:.1f}%",
            trend_positive=fretes_crescimento >= 0
        )
        kpi_layout.addWidget(self.kpi_fretes, 0, 2)

        # KPI: Clientes Ativos
        clientes_data = self.kpis.get('clientes_ativos', {})
        clientes_valor = clientes_data.get('valor', 0)
        clientes_crescimento = clientes_data.get('crescimento', 0)
        
        self.kpi_clientes = KPICard(
            title="Clientes Ativos",
            value=str(int(clientes_valor)),
            subtitle="No período selecionado",
            trend=f"+{clientes_crescimento:.1f}%" if clientes_crescimento >= 0 else f"{clientes_crescimento:.1f}%",
            trend_positive=clientes_crescimento >= 0
        )
        kpi_layout.addWidget(self.kpi_clientes, 0, 3)

        self.content_layout.addLayout(kpi_layout)

    def _create_charts_section(self):
        """Cria seção de gráficos com dados reais."""
        c = cw_theme.colors
        t = cw_theme.spacing

        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(t.LG)

        # Gráfico de Receita Mensal - dados reais
        receita_data = self.chart_data.get('receita', {})
        if not receita_data.get('labels') or not receita_data.get('valores'):
            # Dados fallback se não houver dados reais
            receita_data = {
                'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                'valores': [0, 0, 0, 0, 0, 0]
            }
        
        self.chart_receita = CWChartCard(
            "Receita Mensal",
            ChartType.LINE,
            receita_data
        )
        charts_layout.addWidget(self.chart_receita, 1)

        # Gráfico de Fretes por Status - dados reais
        fretes_status = self.dashboard_service.resumo_fretes_status(
            self.tipo_periodo, self.mes, self.ano
        )
        if not fretes_status:
            fretes_status = [("Concluídas", 0), ("Em andamento", 0), ("Pendentes", 0)]
        
        fretes_labels = [status[0] for status in fretes_status]
        fretes_valores = [status[1] for status in fretes_status]
        
        self.chart_fretes = CWChartCard(
            "Fretes por Status",
            ChartType.DONUT,
            {'labels': fretes_labels, 'valores': fretes_valores}
        )
        charts_layout.addWidget(self.chart_fretes, 1)

        self.content_layout.addLayout(charts_layout)

        # Gráfico de Despesas por Categoria - dados reais
        despesas_data = self.chart_data.get('despesas', {})
        if not despesas_data.get('labels') or not despesas_data.get('valores'):
            # Dados fallback se não houver dados reais
            despesas_data = {
                'labels': ['Combustível', 'Manutenção', 'Salários', 'Outros'],
                'valores': [0, 0, 0, 0]
            }
        
        self.chart_despesas = CWChartCard(
            "Despesas por Categoria",
            ChartType.BAR,
            despesas_data
        )
        self.content_layout.addWidget(self.chart_despesas)

    def _create_summary_cards(self):
        """Cria cards de resumo (contas, combustível, manutenção)."""
        c = cw_theme.colors
        t = cw_theme.spacing

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(t.LG)

        # Card Contas
        contas_card = CWCard(title="Contas a Pagar")
        contas_info = QLabel(f"Pendentes: {self.contas_resumo.get('pendentes', 0)}")
        contas_info.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        contas_info.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        contas_card.add_widget(contas_info)
        
        valor_contas = QLabel(formatar_moeda(self.contas_resumo.get('total', 0)))
        valor_contas.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        valor_contas.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
        contas_card.add_widget(valor_contas)
        
        contas_card.add_spacing()
        
        btn_contas = CWButton("Ver Contas", ButtonVariant.GHOST, ButtonSize.SM)
        contas_card.add_widget(btn_contas)
        
        summary_layout.addWidget(contas_card, 1)

        # Card Combustível
        combustivel_card = CWCard(title="Combustível")
        combustivel_info = QLabel(f"Abastecimentos: {self.combustivel_resumo.get('total', 0)}")
        combustivel_info.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        combustivel_info.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        combustivel_card.add_widget(combustivel_info)
        
        valor_combustivel = QLabel(formatar_moeda(self.combustivel_resumo.get('gasto', 0)))
        valor_combustivel.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        valor_combustivel.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
        combustivel_card.add_widget(valor_combustivel)
        
        combustivel_card.add_spacing()
        
        btn_combustivel = CWButton("Ver Abastecimentos", ButtonVariant.GHOST, ButtonSize.SM)
        combustivel_card.add_widget(btn_combustivel)
        
        summary_layout.addWidget(combustivel_card, 1)

        # Card Manutenção
        manutencao_card = CWCard(title="Manutenções")
        manutencao_info = QLabel(f"Em andamento: {self.manutencoes_resumo.get('andamento', 0)}")
        manutencao_info.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        manutencao_info.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        manutencao_card.add_widget(manutencao_info)
        
        valor_manutencao = QLabel(formatar_moeda(self.manutencoes_resumo.get('gasto', 0)))
        valor_manutencao.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        valor_manutencao.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
        manutencao_card.add_widget(valor_manutencao)
        
        manutencao_card.add_spacing()
        
        btn_manutencao = CWButton("Ver Manutenções", ButtonVariant.GHOST, ButtonSize.SM)
        manutencao_card.add_widget(btn_manutencao)
        
        summary_layout.addWidget(manutencao_card, 1)

        self.content_layout.addLayout(summary_layout)

    def _create_activity_section(self):
        """Cria seção de atividades recentes."""
        c = cw_theme.colors
        t = cw_theme.spacing

        atividades_card = CWCard(title="Atividades Recentes")
        
        if not self.atividades:
            empty_label = QLabel("Nenhuma atividade recente")
            empty_label.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
            empty_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            atividades_card.add_widget(empty_label)
        else:
            for atividade in self.atividades[:5]:
                atividade_label = QLabel(f"• {atividade}")
                atividade_label.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
                atividade_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
                atividades_card.add_widget(atividade_label)
        
        self.content_layout.addWidget(atividades_card)
        self.content_layout.addStretch()

    def _load_data(self):
        """Carrega dados reais do dashboard usando dashboard_service."""
        try:
            # Carregar KPIs executivos
            self.kpis = self.dashboard_service.calcular_kpis(
                self.tipo_periodo, self.mes, self.ano
            )
            
            # Carregar dados de gráficos
            dashboard_executivo = self.dashboard_service.carregar_dashboard_executivo(
                self.tipo_periodo, self.mes, self.ano
            )
            self.chart_data = dashboard_executivo
            
            # Carregar resumo de contas
            contas_resumo = self.dashboard_service.resumo_contas_receber_pagar(
                self.tipo_periodo, self.mes, self.ano
            )
            self.contas_resumo = {
                'pendentes': contas_resumo.get('Pagar', {}).get('total', 0),
                'total': contas_resumo.get('Pagar', {}).get('total', 0)
            }
            
            # Carregar resumo de combustível (usando dados de KPIs)
            combustivel_data = self.kpis.get('total_abastecido', {})
            self.combustivel_resumo = {
                'total': int(combustivel_data.get('valor', 0) / 100),  # Estimativa de abastecimentos
                'gasto': combustivel_data.get('valor', 0)
            }
            
            # Manutenções (placeholder - implementar quando houver serviço específico)
            self.manutencoes_resumo = {'andamento': 0, 'gasto': 0}
            
            # Atividades (placeholder - implementar quando houver serviço específico)
            self.atividades = []
            
        except Exception as e:
            print(f"Erro ao carregar dados do dashboard: {e}")
            # Fallback para dados vazios
            self.kpis = {}
            self.chart_data = {}
            self.contas_resumo = {'pendentes': 0, 'total': 0}
            self.combustivel_resumo = {'total': 0, 'gasto': 0}
            self.manutencoes_resumo = {'andamento': 0, 'gasto': 0}
            self.atividades = []

    def _on_periodo_changed(self, periodo):
        """Handler para mudança de período."""
        self.tipo_periodo = periodo
        self._load_data()
        self._update_ui()

    def _update_ui(self):
        """Atualiza UI com novos dados."""
        # Atualizar KPIs
        receita_data = self.kpis.get('receita_total', {})
        self.kpi_receita._value = formatar_moeda(receita_data.get('valor', 0))
        
        lucro_data = self.kpis.get('lucro_estimado', {})
        self.kpi_lucro._value = formatar_moeda(lucro_data.get('valor', 0))
        
        fretes_data = self.kpis.get('fretes_realizados', {})
        self.kpi_fretes._value = str(int(fretes_data.get('valor', 0)))
        
        clientes_data = self.kpis.get('clientes_ativos', {})
        self.kpi_clientes._value = str(int(clientes_data.get('valor', 0)))
        
        # Atualizar gráficos
        if hasattr(self, 'chart_receita'):
            receita_data = self.chart_data.get('receita', {})
            self.chart_receita.update_data(receita_data)
        
        if hasattr(self, 'chart_despesas'):
            despesas_data = self.chart_data.get('despesas', {})
            self.chart_despesas.update_data(despesas_data)

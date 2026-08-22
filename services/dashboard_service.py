"""
Serviço de dashboard.
"""


class DashboardService:
    def carregar_dashboard(self, tipo, mes, ano):
        return {
            "dados": {},
            "top_destinos": [],
            "ranking_clientes": [],
            "extras": {}
        }
    
    def carregar_dashboard_executivo(self, tipo="", mes="", ano="", data_inicio="", data_fim=""):
        return {
            "kpis": {},
            "receita": {"labels": [], "valores": []},
            "fretes": {"labels": [], "valores": []},
            "clientes": {"labels": [], "valores": []},
            "motoristas": {"labels": [], "valores": []},
            "despesas": {"labels": [], "valores": []},
            "combustivel": {"labels": [], "litros": [], "medias": []},
            "comparativo": {"labels": [], "receitas": [], "despesas": [], "lucros": []},
        }


dashboard_service = DashboardService()

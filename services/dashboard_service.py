"""
Serviço de dashboard.
"""
from datetime import datetime


class DashboardService:
    def calcular_kpis(self, tipo="transportadora", mes=None, ano=None):
        """Calcula KPIs do dashboard."""
        return {
            "total_fretes": 0,
            "receita_bruta": 0.0,
            "despesa_total": 0.0,
            "liquido": 0.0,
            "margem_percentual": 0.0,
            "fretes_pendentes": 0,
            "fretes_concluidos": 0,
            "total_notas": 0,
            "valor_notas": 0.0,
            "caminhoes_ativos": 0,
            "motoristas_ativos": 0,
            "clientes_ativos": 0,
            "km_total": 0.0,
            "litros_combustivel": 0.0,
            "custo_combustivel": 0.0,
            "custo_manutencao": 0.0,
            "contas_receber": 0.0,
            "contas_pagar": 0.0,
            "saldo_caixa": 0.0,
        }
    
    def resumo_fretes_status(self, tipo="transportadora", mes=None, ano=None):
        return []
    
    def resumo_contas_receber_pagar(self, tipo="transportadora", mes=None, ano=None):
        return {"receber": 0.0, "pagar": 0.0}
    
    def resumo_combustivel_mes(self):
        return {"litros": 0.0, "custo": 0.0, "km": 0.0, "media_km_l": 0.0}
    
    def resumo_manutencoes(self):
        return {"total": 0, "custo": 0.0, "pendentes": 0}
    
    def proximas_entregas(self, limite=8):
        return []
    
    def dados_graficos_comparativo_mensal(self, ano=None):
        return {
            "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
            "receitas": [0]*12,
            "despesas": [0]*12,
        }


dashboard_service = DashboardService()

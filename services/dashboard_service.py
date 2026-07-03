from __future__ import annotations

from typing import Any, Dict, List, Tuple

from utils.database import (
    conectar,
    dados_dashboard,
    top_destinos_dashboard,
    gerar_ranking_clientes_v6,
)


class DashboardService:
    def carregar_dashboard(self, tipo_periodo: str, mes: str, ano: str) -> Dict[str, Any]:
        return {
            "dados": dados_dashboard(tipo_periodo, mes, ano),
            "top_destinos": top_destinos_dashboard(tipo_periodo, mes, ano),
            "ranking_clientes": gerar_ranking_clientes_v6(tipo_periodo, mes, ano)[:4],
            "extras": self.buscar_extras(tipo_periodo, mes, ano),
        }

    def buscar_extras(self, tipo_periodo: str, mes: str, ano: str) -> Dict[str, Any]:
        conn = conectar()
        cursor = conn.cursor()

        filtro_notas = ""
        params_notas: List[str] = []
        filtro_folha = ""
        params_folha: List[str] = []

        if tipo_periodo == "Mês":
            filtro_notas = "WHERE substr(criado_em, 6, 2) = ? AND substr(criado_em, 1, 4) = ?"
            params_notas = [mes, ano]
            filtro_folha = "WHERE mes = ? AND ano = ?"
            params_folha = [mes, ano]
        elif tipo_periodo == "Ano":
            filtro_notas = "WHERE substr(criado_em, 1, 4) = ?"
            params_notas = [ano]
            filtro_folha = "WHERE ano = ?"
            params_folha = [ano]

        try:
            cursor.execute(f"""
                SELECT
                    COALESCE(SUM(valor_mercadoria), 0),
                    COALESCE(SUM(valor_frete), 0)
                FROM notas
                {filtro_notas}
            """, params_notas)
            valor_notas, frete_notas = cursor.fetchone()

            cursor.execute("""
                SELECT COALESCE(SUM(salario), 0), COUNT(*)
                FROM funcionarios
                WHERE status = 'Ativo'
            """)
            salarios_ativos, funcionarios_ativos = cursor.fetchone()

            cursor.execute(f"""
                SELECT
                    COALESCE(SUM(total), 0),
                    COALESCE(SUM(hora_extra), 0)
                FROM folha_funcionarios
                {filtro_folha}
            """, params_folha)
            total_folha, total_hora_extra = cursor.fetchone()
        finally:
            conn.close()

        return {
            "valor_notas": valor_notas or 0,
            "frete_notas": frete_notas or 0,
            "salarios_ativos": salarios_ativos or 0,
            "funcionarios_ativos": funcionarios_ativos or 0,
            "total_folha": total_folha or 0,
            "total_hora_extra": total_hora_extra or 0,
        }


dashboard_service = DashboardService()

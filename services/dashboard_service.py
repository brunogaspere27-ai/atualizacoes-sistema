"""
Servico de dashboard executivo com KPIs, graficos e comparativos.

Responsavel por todas as consultas de dados usadas pelo painel principal:
- 12 KPIs com comparacao de periodo anterior
- 7 fontes de dados para graficos
- Filtros: Hoje, Semana, Mes, Ano, Personalizado
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from utils.cache import runtime_cache
from utils.database import (
    conectar,
    dados_dashboard,
    top_destinos_dashboard,
    gerar_ranking_clientes_v6,
)
from utils.logger import get_logger
from utils.performance import timed_block

logger = get_logger(__name__)

# Nomes dos meses em portugues
_MESES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez",
]


def _build_period_filter(
    tipo_periodo: str,
    mes: str,
    ano: str,
    data_inicio: str = "",
    data_fim: str = "",
    col_data: str = "criado_em",
    date_format: str = "sqlite",
) -> Tuple[str, List[str]]:
    """
    Monta clausula WHERE para filtro de periodo.

    Args:
        tipo_periodo: Hoje | Semana | Mes | Ano | Personalizado | Geral
        mes: mes como string "01"-"12"
        ano: ano como string "2024"
        data_inicio: DD/MM/YYYY para personalizado
        data_fim: DD/MM/YYYY para personalizado
        col_data: coluna de data na tabela
        date_format: 'sqlite' (YYYY-MM-DD) ou 'br' (DD/MM/YYYY)

    Returns:
        Tuple (where_clause, params_list)
    """
    if date_format == "br":
        col_ano = f"substr({col_data}, 7, 4)"
        col_mes = f"substr({col_data}, 4, 2)"
        col_dia_full = f"substr({col_data}, 7, 4) || '-' || substr({col_data}, 4, 2) || '-' || substr({col_data}, 1, 2)"
    else:
        col_ano = f"substr({col_data}, 1, 4)"
        col_mes = f"substr({col_data}, 6, 2)"
        col_dia_full = f"substr({col_data}, 1, 10)"

    if tipo_periodo == "Hoje":
        hoje = datetime.now().strftime("%Y-%m-%d")
        return (f"WHERE {col_dia_full} = ?", [hoje])

    if tipo_periodo == "Semana":
        inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        fim = datetime.now().strftime("%Y-%m-%d")
        return (f"WHERE {col_dia_full} BETWEEN ? AND ?", [inicio, fim])

    if tipo_periodo == "Mês" and mes and ano:
        return (f"WHERE {col_mes} = ? AND {col_ano} = ?", [mes, ano])

    if tipo_periodo == "Ano" and ano:
        return (f"WHERE {col_ano} = ?", [ano])

    if tipo_periodo == "Personalizado" and data_inicio and data_fim:
        di = _parse_br_to_sqlite(data_inicio)
        df = _parse_br_to_sqlite(data_fim)
        return (f"WHERE {col_dia_full} BETWEEN ? AND ?", [di, df])

    return ("", [])


def _parse_br_to_sqlite(data_br: str) -> str:
    """Converte DD/MM/YYYY para YYYY-MM-DD."""
    try:
        parts = data_br.strip().split("/")
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
    except Exception:
        pass
    return data_br


def _get_previous_period_filter(
    tipo_periodo: str, mes: str, ano: str,
    data_inicio: str, data_fim: str,
    col_data: str, date_format: str,
) -> Tuple[str, List[str]]:
    """Calcula filtro do periodo anterior para comparacao."""
    if tipo_periodo == "Hoje":
        ontem = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if date_format == "br":
            col_dia = f"substr({col_data}, 7, 4) || '-' || substr({col_data}, 4, 2) || '-' || substr({col_data}, 1, 2)"
        else:
            col_dia = f"substr({col_data}, 1, 10)"
        return (f"WHERE {col_dia} = ?", [ontem])

    if tipo_periodo == "Semana":
        inicio = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        fim = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
        if date_format == "br":
            col_dia = f"substr({col_data}, 7, 4) || '-' || substr({col_data}, 4, 2) || '-' || substr({col_data}, 1, 2)"
        else:
            col_dia = f"substr({col_data}, 1, 10)"
        return (f"WHERE {col_dia} BETWEEN ? AND ?", [inicio, fim])

    if tipo_periodo == "Mês" and mes and ano:
        mes_int = int(mes)
        ano_int = int(ano)
        if mes_int == 1:
            mes_ant, ano_ant = 12, ano_int - 1
        else:
            mes_ant, ano_ant = mes_int - 1, ano_int
        return _build_period_filter(
            "Mês", f"{mes_ant:02d}", str(ano_ant), "", "", col_data, date_format
        )

    if tipo_periodo == "Ano" and ano:
        return _build_period_filter(
            "Ano", mes, str(int(ano) - 1), "", "", col_data, date_format
        )

    if tipo_periodo == "Personalizado" and data_inicio and data_fim:
        try:
            di = datetime.strptime(data_inicio.strip(), "%d/%m/%Y")
            df = datetime.strptime(data_fim.strip(), "%d/%m/%Y")
            duracao = (df - di).days + 1
            df_ant = di - timedelta(days=1)
            di_ant = df_ant - timedelta(days=duracao - 1)
            return _build_period_filter(
                "Personalizado", "", "",
                di_ant.strftime("%d/%m/%Y"),
                df_ant.strftime("%d/%m/%Y"),
                col_data, date_format,
            )
        except Exception:
            pass

    return ("", [])


def _calc_growth(current: float, previous: float) -> float:
    """Calcula percentual de crescimento."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / abs(previous)) * 100.0


class DashboardService:
    """Servico de dados para o dashboard executivo."""

    def __init__(self) -> None:
        self._ttl_dashboard = 10
        self._ttl_graficos = 20

    def _cache_key(
        self,
        tipo_periodo: str,
        mes: str = "",
        ano: str = "",
        data_inicio: str = "",
        data_fim: str = "",
        extra: str = "",
    ) -> tuple:
        return (tipo_periodo, mes, ano, data_inicio, data_fim, extra)

    # ------------------------------------------------------------------
    # Dashboard legado (compatibilidade)
    # ------------------------------------------------------------------

    def carregar_dashboard(self, tipo_periodo: str, mes: str, ano: str) -> Dict[str, Any]:
        cache_key = self._cache_key(tipo_periodo, mes, ano, extra="legado")

        def _load():
            # Uma unica conexao compartilhada para as 4 consultas desta operacao
            # (antes eram 4 conexoes SQLite abertas/fechadas em sequencia).
            with timed_block("dashboard.legado", extra=f"{tipo_periodo}|{mes}|{ano}"):
                conn = conectar()
                try:
                    return {
                        "dados": dados_dashboard(tipo_periodo, mes, ano, conn=conn),
                        "top_destinos": top_destinos_dashboard(tipo_periodo, mes, ano, conn=conn),
                        "ranking_clientes": gerar_ranking_clientes_v6(tipo_periodo, mes, ano, conn=conn)[:4],
                        "extras": self.buscar_extras(tipo_periodo, mes, ano, conn=conn),
                    }
                finally:
                    conn.close()

        return runtime_cache.get_or_set("dashboard", cache_key, _load, ttl_seconds=self._ttl_dashboard)

    def carregar_dashboard_executivo(
        self,
        tipo_periodo: str = "Geral",
        mes: str = "",
        ano: str = "",
        data_inicio: str = "",
        data_fim: str = "",
    ) -> Dict[str, Any]:
        cache_key = self._cache_key(tipo_periodo, mes, ano, data_inicio, data_fim, extra="executivo")

        def _load():
            with timed_block(
                "dashboard.executivo",
                extra=f"{tipo_periodo}|{mes}|{ano}|{data_inicio}|{data_fim}",
            ):
                return {
                    "kpis": self.calcular_kpis(tipo_periodo, mes, ano, data_inicio, data_fim),
                    "receita": self.dados_graficos_receita_mensal(ano),
                    "fretes": self.dados_graficos_fretes_mensal(ano),
                    "clientes": self.dados_graficos_clientes_lucrativos(ano),
                    "motoristas": self.dados_graficos_motoristas_faturamento(ano),
                    "despesas": self.dados_graficos_despesas_categoria(tipo_periodo, mes, ano),
                    "combustivel": self.dados_graficos_consumo_combustivel(ano),
                    "comparativo": self.dados_graficos_comparativo_mensal(ano),
                }

        return runtime_cache.get_or_set(
            "dashboard",
            cache_key,
            _load,
            ttl_seconds=self._ttl_dashboard,
        )

    def buscar_extras(
        self,
        tipo_periodo: str,
        mes: str,
        ano: str,
        conn: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Args:
            conn: conexao opcional ja aberta, reaproveitada por `carregar_dashboard`.
        """
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

        conexao_propria = conn is None
        if conexao_propria:
            conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT COALESCE(SUM(valor_mercadoria), 0),
                       COALESCE(SUM(valor_frete), 0)
                FROM notas {filtro_notas}
            """, params_notas)
            valor_notas, frete_notas = cursor.fetchone()

            cursor.execute("""
                SELECT COALESCE(SUM(salario), 0), COUNT(*)
                FROM funcionarios WHERE status = 'Ativo'
            """)
            salarios_ativos, funcionarios_ativos = cursor.fetchone()

            cursor.execute(f"""
                SELECT COALESCE(SUM(total), 0), COALESCE(SUM(hora_extra), 0)
                FROM folha_funcionarios {filtro_folha}
            """, params_folha)
            total_folha, total_hora_extra = cursor.fetchone()
        finally:
            if conexao_propria:
                conn.close()

        return {
            "valor_notas": valor_notas or 0,
            "frete_notas": frete_notas or 0,
            "salarios_ativos": salarios_ativos or 0,
            "funcionarios_ativos": funcionarios_ativos or 0,
            "total_folha": total_folha or 0,
            "total_hora_extra": total_hora_extra or 0,
        }

    # ------------------------------------------------------------------
    # KPIs executivos
    # ------------------------------------------------------------------

    def calcular_kpis(
        self,
        tipo_periodo: str = "Geral",
        mes: str = "",
        ano: str = "",
        data_inicio: str = "",
        data_fim: str = "",
    ) -> Dict[str, Dict[str, float]]:
        """
        Calcula 12 KPIs com comparacao de periodo anterior.

        Retorna dict com chaves:
            receita_total, lucro_estimado, fretes_realizados, fretes_andamento,
            clientes_ativos, motoristas_ativos, valor_recebido, valor_pendente,
            total_abastecido, consumo_medio, quilometragem, media_viagem
        Cada valor: {valor, valor_anterior, crescimento}
        """
        # Filtros para cada tabela (diferentes formatos de data)
        f_viagem_cur, p_viagem_cur = _build_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "data_saida", "br",
        )
        f_nota_cur, p_nota_cur = _build_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "criado_em", "sqlite",
        )
        f_conta_cur, p_conta_cur = _build_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "vencimento", "br",
        )
        f_abast_cur, p_abast_cur = _build_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "data_abastecimento", "br",
        )

        # Periodo anterior
        f_viagem_ant, p_viagem_ant = _get_previous_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "data_saida", "br",
        )
        f_nota_ant, p_nota_ant = _get_previous_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "criado_em", "sqlite",
        )
        f_conta_ant, p_conta_ant = _get_previous_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "vencimento", "br",
        )
        f_abast_ant, p_abast_ant = _get_previous_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim,
            "data_abastecimento", "br",
        )

        cache_key = self._cache_key(tipo_periodo, mes, ano, data_inicio, data_fim, extra="kpis")

        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                kpis = {}

                # 1. Receita total (SUM frete_total viagens)
                kpis["receita_total"] = self._kpi_soma(
                    cur, "viagens", "frete_total", f_viagem_cur, p_viagem_cur,
                    f_viagem_ant, p_viagem_ant,
                )

                # 2. Lucro estimado (SUM lucro_total viagens)
                kpis["lucro_estimado"] = self._kpi_soma(
                    cur, "viagens", "lucro_total", f_viagem_cur, p_viagem_cur,
                    f_viagem_ant, p_viagem_ant,
                )

                # 3. Fretes realizados (COUNT viagens finalizadas)
                sep_cur = "AND" if f_viagem_cur else "WHERE"
                sep_ant = "AND" if f_viagem_ant else "WHERE"
                kpis["fretes_realizados"] = self._kpi_count(
                    cur, "viagens",
                    f"{f_viagem_cur} {sep_cur} status = 'Finalizada'" if f_viagem_cur else "WHERE status = 'Finalizada'",
                    p_viagem_cur,
                    f"{f_viagem_ant} {sep_ant} status = 'Finalizada'" if f_viagem_ant else "WHERE status = 'Finalizada'",
                    p_viagem_ant,
                )

                # 4. Fretes em andamento
                kpis["fretes_andamento"] = self._kpi_count(
                    cur, "viagens",
                    f"{f_viagem_cur} {sep_cur} status = 'Em viagem'" if f_viagem_cur else "WHERE status = 'Em viagem'",
                    p_viagem_cur,
                    f"{f_viagem_ant} {sep_ant} status = 'Em viagem'" if f_viagem_ant else "WHERE status = 'Em viagem'",
                    p_viagem_ant,
                )

                # 5. Clientes ativos (COUNT DISTINCT destinatario em notas)
                kpis["clientes_ativos"] = self._kpi_count_distinct(
                    cur, "notas", "destinatario_id", f_nota_cur, p_nota_cur,
                    f_nota_ant, p_nota_ant,
                )

                # 6. Motoristas ativos (COUNT DISTINCT motorista em viagens)
                kpis["motoristas_ativos"] = self._kpi_count_distinct(
                    cur, "viagens", "motorista", f_viagem_cur, p_viagem_cur,
                    f_viagem_ant, p_viagem_ant,
                )

                # 7. Valor recebido (contas Receber Recebido)
                f_rec_cur = f"{f_conta_cur} {'AND' if f_conta_cur else 'WHERE'} tipo = 'Receber' AND status = 'Recebido'"
                f_rec_ant = f"{f_conta_ant} {'AND' if f_conta_ant else 'WHERE'} tipo = 'Receber' AND status = 'Recebido'"
                kpis["valor_recebido"] = self._kpi_soma(
                    cur, "contas", "valor", f_rec_cur, p_conta_cur,
                    f_rec_ant, p_conta_ant,
                )

                # 8. Valor pendente (contas Receber Pendente)
                f_pend_cur = f"{f_conta_cur} {'AND' if f_conta_cur else 'WHERE'} tipo = 'Receber' AND status = 'Pendente'"
                f_pend_ant = f"{f_conta_ant} {'AND' if f_conta_ant else 'WHERE'} tipo = 'Receber' AND status = 'Pendente'"
                kpis["valor_pendente"] = self._kpi_soma(
                    cur, "contas", "valor", f_pend_cur, p_conta_cur,
                    f_pend_ant, p_conta_ant,
                )

                # 9. Total abastecido (SUM valor_total abastecimentos)
                kpis["total_abastecido"] = self._kpi_soma(
                    cur, "abastecimentos", "valor_total", f_abast_cur, p_abast_cur,
                    f_abast_ant, p_abast_ant,
                )

                # 10. Consumo medio (AVG media_km_l abastecimentos)
                kpis["consumo_medio"] = self._kpi_avg(
                    cur, "abastecimentos", "media_km_l", f_abast_cur, p_abast_cur,
                    f_abast_ant, p_abast_ant,
                )

                # 11. Quilometragem (SUM km_atual abastecimentos - max km por veiculo)
                kpis["quilometragem"] = self._kpi_soma(
                    cur, "abastecimentos", "km_atual", f_abast_cur, p_abast_cur,
                    f_abast_ant, p_abast_ant,
                )

                # 12. Media por viagem (frete_total / total_viagens)
                receita = kpis["receita_total"]["valor"]
                total_viag = kpis["fretes_realizados"]["valor"]
                receita_ant = kpis["receita_total"]["valor_anterior"]
                total_viag_ant = kpis["fretes_realizados"]["valor_anterior"]
                media = receita / total_viag if total_viag > 0 else 0
                media_ant = receita_ant / total_viag_ant if total_viag_ant > 0 else 0
                kpis["media_viagem"] = {
                    "valor": media,
                    "valor_anterior": media_ant,
                    "crescimento": _calc_growth(media, media_ant),
                }

                return kpis
            finally:
                conn.close()

        return runtime_cache.get_or_set(
            "dashboard",
            cache_key,
            _load,
            ttl_seconds=self._ttl_dashboard,
        )

    def _kpi_soma(self, cur, tabela, coluna, f_cur, p_cur, f_ant, p_ant):
        if not re.match(r'^[a-zA-Z0-9_]+$', str(tabela)):
            raise ValueError("Invalid input")
        if not re.match(r'^[a-zA-Z0-9_]+$', str(coluna)):
            raise ValueError("Invalid input")
        cur.execute(f"SELECT COALESCE(SUM({coluna}), 0) FROM {tabela} {f_cur}", p_cur)
        val = cur.fetchone()[0]
        cur.execute(f"SELECT COALESCE(SUM({coluna}), 0) FROM {tabela} {f_ant}", p_ant)
        val_ant = cur.fetchone()[0]
        return {"valor": val, "valor_anterior": val_ant, "crescimento": _calc_growth(val, val_ant)}

    def _kpi_count(self, cur, tabela, f_cur, p_cur, f_ant, p_ant):
        cur.execute(f"SELECT COUNT(*) FROM {tabela} {f_cur}", p_cur)
        val = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) FROM {tabela} {f_ant}", p_ant)
        val_ant = cur.fetchone()[0]
        return {"valor": val, "valor_anterior": val_ant, "crescimento": _calc_growth(val, val_ant)}

    def _kpi_count_distinct(self, cur, tabela, coluna, f_cur, p_cur, f_ant, p_ant):
        cur.execute(f"SELECT COUNT(DISTINCT {coluna}) FROM {tabela} {f_cur}", p_cur)
        val = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(DISTINCT {coluna}) FROM {tabela} {f_ant}", p_ant)
        val_ant = cur.fetchone()[0]
        return {"valor": val, "valor_anterior": val_ant, "crescimento": _calc_growth(val, val_ant)}

    def _kpi_avg(self, cur, tabela, coluna, f_cur, p_cur, f_ant, p_ant):
        cur.execute(f"SELECT COALESCE(AVG({coluna}), 0) FROM {tabela} {f_cur}", p_cur)
        val = cur.fetchone()[0]
        cur.execute(f"SELECT COALESCE(AVG({coluna}), 0) FROM {tabela} {f_ant}", p_ant)
        val_ant = cur.fetchone()[0]
        return {"valor": val, "valor_anterior": val_ant, "crescimento": _calc_growth(val, val_ant)}

    # ------------------------------------------------------------------
    # Dados para graficos
    # ------------------------------------------------------------------

    def dados_graficos_receita_mensal(self, ano: str) -> Dict[str, Any]:
        """Receita por mes (12 barras) para grafico."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT substr(data_saida, 4, 2) AS mes,
                           COALESCE(SUM(frete_total), 0)
                    FROM viagens
                    WHERE substr(data_saida, 7, 4) = ?
                    GROUP BY mes
                    ORDER BY mes
                """, (ano,))
                rows = {r[0]: r[1] for r in cur.fetchall()}
            finally:
                conn.close()

            labels = _MESES[:]
            valores = [rows.get(f"{m:02d}", 0) for m in range(1, 13)]
            return {"labels": labels, "valores": valores}

        return runtime_cache.get_or_set(
            "dashboard_graficos",
            ("receita_mensal", ano),
            _load,
            ttl_seconds=self._ttl_graficos,
        )

    def dados_graficos_fretes_mensal(self, ano: str) -> Dict[str, Any]:
        """Fretes realizados por mes (12 barras)."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT substr(data_saida, 4, 2) AS mes,
                           COUNT(*)
                    FROM viagens
                    WHERE substr(data_saida, 7, 4) = ? AND status = 'Finalizada'
                    GROUP BY mes
                    ORDER BY mes
                """, (ano,))
                rows = {r[0]: r[1] for r in cur.fetchall()}
            finally:
                conn.close()

            labels = _MESES[:]
            valores = [rows.get(f"{m:02d}", 0) for m in range(1, 13)]
            return {"labels": labels, "valores": valores}

        return runtime_cache.get_or_set(
            "dashboard_graficos",
            ("fretes_mensal", ano),
            _load,
            ttl_seconds=self._ttl_graficos,
        )

    def dados_graficos_clientes_lucrativos(self, ano: str, top_n: int = 5) -> Dict[str, Any]:
        """Top clientes por frete no ano."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT COALESCE(c.nome, 'Nao informado') AS cliente,
                           COALESCE(SUM(n.valor_frete), 0) AS frete
                    FROM notas n
                    LEFT JOIN clientes c ON c.id = n.destinatario_id
                    WHERE substr(n.criado_em, 1, 4) = ?
                    GROUP BY c.nome
                    ORDER BY frete DESC
                    LIMIT ?
                """, (ano, top_n))
                rows = cur.fetchall()
            finally:
                conn.close()

            labels = [r[0] for r in rows]
            valores = [r[1] for r in rows]
            return {"labels": labels, "valores": valores}

        return runtime_cache.get_or_set(
            "dashboard_graficos",
            ("clientes_lucrativos", ano, top_n),
            _load,
            ttl_seconds=self._ttl_graficos,
        )

    def dados_graficos_motoristas_faturamento(self, ano: str, top_n: int = 5) -> Dict[str, Any]:
        """Top motoristas por frete no ano."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT COALESCE(motorista, 'Nao informado') AS motorista,
                           COALESCE(SUM(frete_total), 0) AS frete
                    FROM viagens
                    WHERE substr(data_saida, 7, 4) = ? AND status = 'Finalizada'
                    GROUP BY motorista
                    ORDER BY frete DESC
                    LIMIT ?
                """, (ano, top_n))
                rows = cur.fetchall()
            finally:
                conn.close()

            labels = [r[0] for r in rows]
            valores = [r[1] for r in rows]
            return {"labels": labels, "valores": valores}

        return runtime_cache.get_or_set(
            "dashboard_graficos",
            ("motoristas_faturamento", ano, top_n),
            _load,
            ttl_seconds=self._ttl_graficos,
        )

    def dados_graficos_despesas_categoria(
        self, tipo_periodo: str = "Geral", mes: str = "", ano: str = "",
    ) -> Dict[str, Any]:
        """Despesas por categoria (contas tipo=Pagar)."""
        cache_key = self._cache_key(tipo_periodo, mes, ano, extra="despesas_categoria")

        def _load():
            f, p = _build_period_filter(tipo_periodo, mes, ano, "", "", "vencimento", "br")
            sep = "AND" if f else "WHERE"
            sql = f"SELECT categoria, COALESCE(SUM(valor), 0) FROM contas {f} {sep} tipo = 'Pagar' GROUP BY categoria ORDER BY SUM(valor) DESC"

            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute(sql, p)
                rows = cur.fetchall()
            finally:
                conn.close()

            labels = [r[0] or "Sem categoria" for r in rows]
            valores = [r[1] for r in rows]
            return {"labels": labels, "valores": valores}

        return runtime_cache.get_or_set(
            "dashboard_graficos",
            cache_key,
            _load,
            ttl_seconds=self._ttl_graficos,
        )

    def dados_graficos_consumo_combustivel(self, ano: str) -> Dict[str, Any]:
        """Consumo de combustivel por mes (litros e media km/l)."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT substr(data_abastecimento, 4, 2) AS mes,
                           COALESCE(SUM(litros), 0),
                           COALESCE(AVG(media_km_l), 0)
                    FROM abastecimentos
                    WHERE substr(data_abastecimento, 7, 4) = ?
                    GROUP BY mes
                    ORDER BY mes
                """, (ano,))
                rows = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
            finally:
                conn.close()

            labels = _MESES[:]
            litros = [rows.get(f"{m:02d}", (0, 0))[0] for m in range(1, 13)]
            medias = [rows.get(f"{m:02d}", (0, 0))[1] for m in range(1, 13)]
            return {"labels": labels, "litros": litros, "medias": medias}

        return runtime_cache.get_or_set(
            "dashboard_graficos",
            ("combustivel", ano),
            _load,
            ttl_seconds=self._ttl_graficos,
        )

    def dados_graficos_comparativo_mensal(self, ano: str) -> Dict[str, Any]:
        """Receita vs Despesas vs Lucro por mes."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                # Receita por mes (viagens)
                cur.execute("""
                    SELECT substr(data_saida, 4, 2), COALESCE(SUM(frete_total), 0)
                    FROM viagens
                    WHERE substr(data_saida, 7, 4) = ? AND status = 'Finalizada'
                    GROUP BY substr(data_saida, 4, 2)
                """, (ano,))
                receita_map = {r[0]: r[1] for r in cur.fetchall()}

                # Despesas por mes (contas Pagar)
                cur.execute("""
                    SELECT substr(vencimento, 4, 2), COALESCE(SUM(valor), 0)
                    FROM contas
                    WHERE substr(vencimento, 7, 4) = ? AND tipo = 'Pagar'
                    GROUP BY substr(vencimento, 4, 2)
                """, (ano,))
                despesa_map = {r[0]: r[1] for r in cur.fetchall()}
            finally:
                conn.close()

            labels = _MESES[:]
            receitas = [receita_map.get(f"{m:02d}", 0) for m in range(1, 13)]
            despesas = [despesa_map.get(f"{m:02d}", 0) for m in range(1, 13)]
            lucros = [r - d for r, d in zip(receitas, despesas)]
            return {
                "labels": labels,
                "receitas": receitas,
                "despesas": despesas,
                "lucros": lucros,
            }

        return runtime_cache.get_or_set(
            "dashboard_graficos",
            ("comparativo_mensal", ano),
            _load,
            ttl_seconds=self._ttl_graficos,
        )


    # ------------------------------------------------------------------
    # Dashboard v2 — cards/gráficos adicionais (redesign visual)
    # Métodos somente-leitura, adicionais aos já existentes acima.
    # ------------------------------------------------------------------

    def resumo_fretes_status(
        self,
        tipo_periodo: str = "Geral", mes: str = "", ano: str = "",
        data_inicio: str = "", data_fim: str = "",
    ) -> List[Tuple[str, int]]:
        """Contagem de viagens agrupada por status, para o donut 'Fretes por Status'."""
        f, p = _build_period_filter(
            tipo_periodo, mes, ano, data_inicio, data_fim, "data_saida", "br",
        )
        cache_key = self._cache_key(tipo_periodo, mes, ano, data_inicio, data_fim, extra="fretes_status")

        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute(
                    f"SELECT COALESCE(NULLIF(status, ''), 'Sem status'), COUNT(*) "
                    f"FROM viagens {f} GROUP BY status ORDER BY COUNT(*) DESC",
                    p,
                )
                return [(row[0], row[1]) for row in cur.fetchall()]
            finally:
                conn.close()

        return runtime_cache.get_or_set(
            "dashboard_graficos", cache_key, _load, ttl_seconds=self._ttl_graficos,
        )

    def resumo_contas_receber_pagar(
        self, tipo_periodo: str = "Geral", mes: str = "", ano: str = "",
    ) -> Dict[str, Dict[str, float]]:
        """Contas a Receber/Pagar em aberto, separadas em vencidas x a vencer."""
        f, p = _build_period_filter(tipo_periodo, mes, ano, "", "", "vencimento", "br")
        hoje = datetime.now().strftime("%d/%m/%Y")
        hoje_sql = f"substr(?, 7, 4) || '-' || substr(?, 4, 2) || '-' || substr(?, 1, 2)"
        cache_key = self._cache_key(tipo_periodo, mes, ano, extra="contas_resumo")

        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                resultado: Dict[str, Dict[str, float]] = {}
                for tipo in ("Receber", "Pagar"):
                    sep = "AND" if f else "WHERE"
                    base = f"{f} {sep} tipo = ? AND status IN ('Pendente', 'Atrasado')"
                    data_col = "substr(vencimento, 7, 4) || '-' || substr(vencimento, 4, 2) || '-' || substr(vencimento, 1, 2)"

                    cur.execute(
                        f"SELECT COALESCE(SUM(valor), 0) FROM contas {base} "
                        f"AND {data_col} < ({hoje_sql})",
                        p + [tipo, hoje, hoje, hoje],
                    )
                    vencidas = cur.fetchone()[0] or 0

                    cur.execute(
                        f"SELECT COALESCE(SUM(valor), 0) FROM contas {base} "
                        f"AND {data_col} >= ({hoje_sql})",
                        p + [tipo, hoje, hoje, hoje],
                    )
                    a_vencer = cur.fetchone()[0] or 0

                    resultado[tipo] = {
                        "vencidas": vencidas,
                        "a_vencer": a_vencer,
                        "total": vencidas + a_vencer,
                    }
                return resultado
            finally:
                conn.close()

        return runtime_cache.get_or_set(
            "dashboard_graficos", cache_key, _load, ttl_seconds=self._ttl_dashboard,
        )

    def resumo_combustivel_mes(self) -> Dict[str, float]:
        """Totais de combustível do mês corrente (independente do filtro selecionado)."""
        mes_atual = datetime.now().strftime("%m")
        ano_atual = datetime.now().strftime("%Y")
        cache_key = self._cache_key("Mês", mes_atual, ano_atual, extra="combustivel_mes")

        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT COALESCE(SUM(valor_total), 0), COALESCE(SUM(litros), 0), "
                    "COALESCE(AVG(NULLIF(valor_litro, 0)), 0) FROM abastecimentos "
                    "WHERE substr(data_abastecimento, 4, 2) = ? AND substr(data_abastecimento, 7, 4) = ?",
                    (mes_atual, ano_atual),
                )
                total, litros, media_litro = cur.fetchone()
                return {
                    "total": total or 0,
                    "litros": litros or 0,
                    "media_litro": media_litro or 0,
                }
            finally:
                conn.close()

        return runtime_cache.get_or_set(
            "dashboard_graficos", cache_key, _load, ttl_seconds=self._ttl_dashboard,
        )

    def resumo_manutencoes(self) -> Dict[str, int]:
        """Manutenções agendadas x atrasadas (data_manutencao no passado e ainda pendentes)."""
        hoje = datetime.now().strftime("%d/%m/%Y")

        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                data_col = "substr(data_manutencao, 7, 4) || '-' || substr(data_manutencao, 4, 2) || '-' || substr(data_manutencao, 1, 2)"
                hoje_sql = "substr(?, 7, 4) || '-' || substr(?, 4, 2) || '-' || substr(?, 1, 2)"

                cur.execute(
                    f"SELECT COUNT(*) FROM manutencoes WHERE status IN ('Pendente', 'Agendado') "
                    f"AND {data_col} < ({hoje_sql})",
                    (hoje, hoje, hoje),
                )
                atrasadas = cur.fetchone()[0] or 0

                cur.execute(
                    f"SELECT COUNT(*) FROM manutencoes WHERE status IN ('Pendente', 'Agendado') "
                    f"AND {data_col} >= ({hoje_sql})",
                    (hoje, hoje, hoje),
                )
                agendadas = cur.fetchone()[0] or 0

                return {"atrasadas": atrasadas, "agendadas": agendadas, "total": atrasadas + agendadas}
            finally:
                conn.close()

        return runtime_cache.get_or_set(
            "dashboard_graficos", ("manutencoes_resumo",), _load, ttl_seconds=self._ttl_dashboard,
        )

    def atividades_recentes(self, limite: int = 4) -> List[Dict[str, str]]:
        """Últimas atividades do sistema (notas, coletas/viagens, manutenções) para o feed do dashboard."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                itens: List[Dict[str, str]] = []

                cur.execute(
                    "SELECT id, origem, destino, criado_em FROM notas ORDER BY criado_em DESC LIMIT ?",
                    (limite,),
                )
                for nid, origem, destino, criado_em in cur.fetchall():
                    itens.append({
                        "tipo": "Fretes",
                        "titulo": f"Novo frete criado",
                        "detalhe": f"Frete #{nid} - {origem or '-'} → {destino or '-'}",
                        "quando": criado_em or "",
                    })

                cur.execute(
                    "SELECT id, veiculo, descricao, criado_em, status FROM manutencoes ORDER BY criado_em DESC LIMIT ?",
                    (limite,),
                )
                for mid, veiculo, descricao, criado_em, status in cur.fetchall():
                    itens.append({
                        "tipo": "Manutenção",
                        "titulo": "Manutenção registrada" if status != "Pago" else "Manutenção concluída",
                        "detalhe": f"Veículo: {veiculo or '-'} - {descricao or ''}",
                        "quando": criado_em or "",
                    })

                itens.sort(key=lambda i: i.get("quando") or "", reverse=True)
                return itens[:limite]
            finally:
                conn.close()

        return runtime_cache.get_or_set(
            "dashboard_graficos", ("atividades_recentes", limite), _load, ttl_seconds=self._ttl_dashboard,
        )

    def proximas_entregas(self, limite: int = 3) -> List[Dict[str, str]]:
        """Viagens em andamento com previsão de retorno/entrega para o painel 'Próximas Entregas'."""
        def _load():
            conn = conectar()
            cur = conn.cursor()
            try:
                cur.execute(
                    """
                    SELECT v.id, v.motorista, v.data_retorno, v.status,
                           (SELECT n.destino FROM viagem_notas vn
                            JOIN notas n ON n.id = vn.nota_id
                            WHERE vn.viagem_id = v.id LIMIT 1) AS destino
                    FROM viagens v
                    WHERE v.status = 'Em viagem'
                    ORDER BY v.data_retorno ASC
                    LIMIT ?
                    """,
                    (limite,),
                )
                itens = []
                for vid, motorista, data_retorno, status, destino in cur.fetchall():
                    itens.append({
                        "titulo": f"Entrega #{vid}",
                        "detalhe": f"Motorista: {motorista or '-'} → {destino or 'Destino não informado'}",
                        "quando": data_retorno or "Sem previsão",
                        "status": status or "Em andamento",
                    })
                return itens
            finally:
                conn.close()

        return runtime_cache.get_or_set(
            "dashboard_graficos", ("proximas_entregas", limite), _load, ttl_seconds=self._ttl_dashboard,
        )


dashboard_service = DashboardService()

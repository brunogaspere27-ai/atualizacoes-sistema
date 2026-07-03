from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from utils.database import conectar, dados_dashboard, listar_viagens, gerar_ranking_clientes_v6


class RelatoriosService:
    def carregar_relatorio(self, tipo_periodo: str, mes: str, ano: str) -> Dict[str, Any]:
        dados = dados_dashboard(tipo_periodo, mes, ano)
        extras = self.buscar_extras(tipo_periodo, mes, ano)
        ranking = gerar_ranking_clientes_v6(tipo_periodo, mes, ano)

        receitas = extras["frete_notas"] + dados["frete_total"] + extras["contas_recebidas"]
        despesas = extras["folha"] + extras["combustivel"] + extras["manutencao"] + extras["contas_pagas"]
        lucro = receitas - despesas

        return {
            "dados": dados,
            "extras": extras,
            "ranking": ranking,
            "receitas": receitas,
            "despesas": despesas,
            "lucro": lucro,
        }

    def buscar_extras(self, tipo_periodo: str, mes: str, ano: str) -> Dict[str, Any]:
        conn = conectar()
        cursor = conn.cursor()

        filtro_notas = filtro_folha = filtro_comb = filtro_manut = filtro_contas = ""
        params_notas: List[str] = []
        params_folha: List[str] = []
        params_comb: List[str] = []
        params_manut: List[str] = []
        params_contas: List[str] = []

        if tipo_periodo == "Mês":
            filtro_notas = "WHERE substr(criado_em, 6, 2) = ? AND substr(criado_em, 1, 4) = ?"
            filtro_folha = "WHERE mes = ? AND ano = ?"
            filtro_comb = "WHERE substr(data_abastecimento, 4, 2) = ? AND substr(data_abastecimento, 7, 4) = ?"
            filtro_manut = "WHERE substr(data_manutencao, 4, 2) = ? AND substr(data_manutencao, 7, 4) = ?"
            filtro_contas = "WHERE substr(vencimento, 4, 2) = ? AND substr(vencimento, 7, 4) = ?"
            params_notas = params_folha = params_comb = params_manut = params_contas = [mes, ano]
        elif tipo_periodo == "Ano":
            filtro_notas = "WHERE substr(criado_em, 1, 4) = ?"
            filtro_folha = "WHERE ano = ?"
            filtro_comb = "WHERE substr(data_abastecimento, 7, 4) = ?"
            filtro_manut = "WHERE substr(data_manutencao, 7, 4) = ?"
            filtro_contas = "WHERE substr(vencimento, 7, 4) = ?"
            params_notas = params_folha = params_comb = params_manut = params_contas = [ano]

        try:
            cursor.execute(f"SELECT COALESCE(SUM(valor_mercadoria), 0), COALESCE(SUM(valor_frete), 0) FROM notas {filtro_notas}", params_notas)
            valor_notas, frete_notas = cursor.fetchone()

            cursor.execute(f"SELECT COALESCE(SUM(total), 0) FROM folha_funcionarios {filtro_folha}", params_folha)
            folha = cursor.fetchone()[0]

            cursor.execute(f"SELECT COALESCE(SUM(valor_total), 0) FROM abastecimentos {filtro_comb}", params_comb)
            combustivel = cursor.fetchone()[0]

            cursor.execute(f"SELECT COALESCE(SUM(valor), 0) FROM manutencoes {filtro_manut}", params_manut)
            manutencao = cursor.fetchone()[0]

            cursor.execute(f"""
                SELECT
                    COALESCE(SUM(CASE WHEN tipo = 'Receber' AND status = 'Recebido' THEN valor ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN tipo = 'Pagar' AND status = 'Pago' THEN valor ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN tipo = 'Receber' AND status NOT IN ('Recebido', 'Cancelado') THEN valor ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN tipo = 'Pagar' AND status NOT IN ('Pago', 'Cancelado') THEN valor ELSE 0 END), 0)
                FROM contas
                {filtro_contas}
            """, params_contas)
            contas_recebidas, contas_pagas, contas_a_receber, contas_a_pagar = cursor.fetchone()

            cursor.execute("SELECT data_abastecimento, veiculo, posto, valor_total FROM abastecimentos ORDER BY id DESC")
            abastecimentos = cursor.fetchall()

            cursor.execute("SELECT data_manutencao, veiculo, descricao, valor, status FROM manutencoes ORDER BY id DESC")
            manutencoes = cursor.fetchall()

            cursor.execute("SELECT tipo, descricao, pessoa, categoria, valor, vencimento, status FROM contas ORDER BY id DESC")
            contas = cursor.fetchall()
        finally:
            conn.close()

        return {
            "valor_notas": valor_notas or 0,
            "frete_notas": frete_notas or 0,
            "folha": folha or 0,
            "combustivel": combustivel or 0,
            "manutencao": manutencao or 0,
            "contas_recebidas": contas_recebidas or 0,
            "contas_pagas": contas_pagas or 0,
            "contas_a_receber": contas_a_receber or 0,
            "contas_a_pagar": contas_a_pagar or 0,
            "abastecimentos": abastecimentos,
            "manutencoes_lista": manutencoes,
            "contas_lista": contas,
        }

    def listar_viagens_periodo(self, tipo_periodo: str, mes: str, ano: str):
        return [viagem for viagem in listar_viagens() if self.data_no_periodo(viagem[1], tipo_periodo, mes, ano)]

    def data_no_periodo(self, data_texto: str | None, tipo_periodo: str, mes: str, ano: str) -> bool:
        if tipo_periodo == "Geral":
            return True
        if not data_texto:
            return False
        try:
            data = datetime.strptime(str(data_texto).split(" ")[0], "%d/%m/%Y")
            if tipo_periodo == "Mês":
                return data.strftime("%m") == mes and data.strftime("%Y") == ano
            if tipo_periodo == "Ano":
                return data.strftime("%Y") == ano
        except Exception:
            return False
        return True


relatorios_service = RelatoriosService()

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

from utils.database import conectar, listar_caminhoes, registrar_sync
from utils.logger import get_logger

logger = get_logger(__name__)


class FrotaService:
    def listar_abastecimentos(self, tipo_periodo: str, mes: str, ano: str, busca: str):
        where = []
        params = []

        if tipo_periodo == "Mês":
            where.append("substr(data_abastecimento, 4, 2) = ? AND substr(data_abastecimento, 7, 4) = ?")
            params.extend([mes, ano])
        elif tipo_periodo == "Ano":
            where.append("substr(data_abastecimento, 7, 4) = ?")
            params.append(ano)

        if busca:
            where.append("(veiculo LIKE ? OR motorista LIKE ? OR posto LIKE ?)")
            params.extend([f"%{busca}%", f"%{busca}%", f"%{busca}%"])

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT
                    id,
                    data_abastecimento,
                    veiculo,
                    motorista,
                    km_atual,
                    litros,
                    valor_litro,
                    valor_total,
                    media_km_l,
                    custo_km,
                    posto,
                    observacao
                FROM abastecimentos
                {where_sql}
                ORDER BY id DESC
            """, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def obter_abastecimento(self, abastecimento_id: Any):
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    id,
                    data_abastecimento,
                    veiculo,
                    motorista,
                    km_atual,
                    litros,
                    valor_litro,
                    valor_total,
                    media_km_l,
                    custo_km,
                    posto,
                    observacao
                FROM abastecimentos
                WHERE id = ?
            """, (abastecimento_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def salvar_abastecimento(self, abastecimento_id: Any, valores: Sequence[Any]) -> Any:
        conn = conectar()
        cursor = conn.cursor()
        try:
            if abastecimento_id:
                cursor.execute("""
                    UPDATE abastecimentos
                    SET data_abastecimento = ?,
                        veiculo = ?,
                        motorista = ?,
                        km_atual = ?,
                        litros = ?,
                        valor_litro = ?,
                        valor_total = ?,
                        media_km_l = ?,
                        custo_km = ?,
                        posto = ?,
                        observacao = ?
                    WHERE id = ?
                """, tuple(valores) + (abastecimento_id,))
                registrar_sync(cursor, "abastecimentos", abastecimento_id)
                registro_id = abastecimento_id
            else:
                cursor.execute("""
                    INSERT INTO abastecimentos (
                        data_abastecimento,
                        veiculo,
                        motorista,
                        km_atual,
                        litros,
                        valor_litro,
                        valor_total,
                        media_km_l,
                        custo_km,
                        posto,
                        observacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(valores))
                registro_id = cursor.lastrowid
                registrar_sync(cursor, "abastecimentos", registro_id)

            conn.commit()
            return registro_id
        finally:
            conn.close()

    def excluir_abastecimento(self, abastecimento_id: Any) -> None:
        conn = conectar()
        cursor = conn.cursor()
        try:
            registrar_sync(cursor, "abastecimentos", abastecimento_id, "DELETE")
            cursor.execute("DELETE FROM abastecimentos WHERE id = ?", (abastecimento_id,))
            conn.commit()
        finally:
            conn.close()

    def calcular_media_e_custo(
        self,
        veiculo: str,
        km_atual: float,
        litros: float,
        valor_total: float,
        abastecimento_id: Any = None,
    ) -> Tuple[float, float]:
        conn = conectar()
        cursor = conn.cursor()
        try:
            if abastecimento_id:
                cursor.execute("""
                    SELECT km_atual
                    FROM abastecimentos
                    WHERE veiculo = ?
                      AND id != ?
                      AND km_atual < ?
                    ORDER BY km_atual DESC
                    LIMIT 1
                """, (veiculo, abastecimento_id, km_atual))
            else:
                cursor.execute("""
                    SELECT km_atual
                    FROM abastecimentos
                    WHERE veiculo = ?
                      AND km_atual < ?
                    ORDER BY km_atual DESC
                    LIMIT 1
                """, (veiculo, km_atual))
            anterior = cursor.fetchone()
        finally:
            conn.close()

        if not anterior:
            return 0, 0

        km_rodado = km_atual - float(anterior[0] or 0)
        if km_rodado <= 0 or litros <= 0:
            return 0, 0

        media = km_rodado / litros
        custo_km = valor_total / km_rodado
        return media, custo_km

    def listar_manutencoes(self, tipo_periodo: str, mes: str, ano: str, busca: str):
        where = []
        params = []

        if tipo_periodo == "Mês":
            where.append("substr(data_manutencao, 4, 2) = ? AND substr(data_manutencao, 7, 4) = ?")
            params.extend([mes, ano])
        elif tipo_periodo == "Ano":
            where.append("substr(data_manutencao, 7, 4) = ?")
            params.append(ano)

        if busca:
            where.append("(veiculo LIKE ? OR oficina LIKE ? OR tipo LIKE ? OR descricao LIKE ?)")
            params.extend([f"%{busca}%", f"%{busca}%", f"%{busca}%", f"%{busca}%"])

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""

        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                SELECT
                    id,
                    data_manutencao,
                    veiculo,
                    km_atual,
                    tipo,
                    descricao,
                    oficina,
                    valor,
                    proxima_revisao_km,
                    status,
                    observacao
                FROM manutencoes
                {where_sql}
                ORDER BY id DESC
            """, params)
            return cursor.fetchall()
        finally:
            conn.close()

    def obter_manutencao(self, manutencao_id: Any):
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    id,
                    data_manutencao,
                    veiculo,
                    km_atual,
                    tipo,
                    descricao,
                    oficina,
                    valor,
                    proxima_revisao_km,
                    status,
                    observacao
                FROM manutencoes
                WHERE id = ?
            """, (manutencao_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def salvar_manutencao(self, manutencao_id: Any, valores: Sequence[Any]) -> Any:
        conn = conectar()
        cursor = conn.cursor()
        try:
            if manutencao_id:
                cursor.execute("""
                    UPDATE manutencoes
                    SET data_manutencao = ?,
                        veiculo = ?,
                        km_atual = ?,
                        tipo = ?,
                        descricao = ?,
                        oficina = ?,
                        valor = ?,
                        proxima_revisao_km = ?,
                        status = ?,
                        observacao = ?
                    WHERE id = ?
                """, tuple(valores) + (manutencao_id,))
                registrar_sync(cursor, "manutencoes", manutencao_id)
                registro_id = manutencao_id
            else:
                cursor.execute("""
                    INSERT INTO manutencoes (
                        data_manutencao,
                        veiculo,
                        km_atual,
                        tipo,
                        descricao,
                        oficina,
                        valor,
                        proxima_revisao_km,
                        status,
                        observacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(valores))
                registro_id = cursor.lastrowid
                registrar_sync(cursor, "manutencoes", registro_id)

            conn.commit()
            return registro_id
        finally:
            conn.close()

    def excluir_manutencao(self, manutencao_id: Any) -> None:
        conn = conectar()
        cursor = conn.cursor()
        try:
            registrar_sync(cursor, "manutencoes", manutencao_id, "DELETE")
            cursor.execute("DELETE FROM manutencoes WHERE id = ?", (manutencao_id,))
            conn.commit()
        finally:
            conn.close()

    # Tabelas permitidas para consulta de veículos — whitelist explícita para evitar SQL injection
    _TABELAS_VEICULOS_PERMITIDAS = frozenset({"abastecimentos", "manutencoes"})

    def listar_veiculos_disponiveis(self, tabela_historico: str) -> List[str]:
        if tabela_historico not in self._TABELAS_VEICULOS_PERMITIDAS:
            raise ValueError(f"Tabela não permitida: {tabela_historico!r}")

        nomes: List[str] = []

        try:
            for caminhao in listar_caminhoes():
                modelo = caminhao[2] or ""
                placa = caminhao[1] or ""
                nome = f"{modelo} - {placa}" if placa else modelo
                if nome.strip() and nome not in nomes:
                    nomes.append(nome)
        except Exception as erro:
            logger.warning(f"Erro ao listar caminhões para veículos disponíveis: {erro}")
            pass

        conn = conectar()
        cursor = conn.cursor()
        try:
            # tabela_historico validada pela whitelist acima — seguro usar f-string
            cursor.execute(f"""
                SELECT DISTINCT veiculo
                FROM {tabela_historico}
                WHERE veiculo IS NOT NULL
                  AND veiculo != ''
                ORDER BY veiculo
            """)
            for item in cursor.fetchall():
                nome = item[0]
                if nome and nome not in nomes:
                    nomes.append(nome)
        except Exception as erro:
            logger.warning(f"Erro ao listar veículos históricos da tabela {tabela_historico}: {erro}")
        finally:
            conn.close()

        if nomes:
            return nomes

        return [
            "Renault Master",
            "Caminhão 3/4 Branco",
            "Caminhão 3/4 Preto",
            "Caminhão Toco",
            "Carro",
        ]


frota_service = FrotaService()

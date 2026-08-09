"""Notas fiscais e manifestos: importacao, listagem, status."""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

from utils.logger import get_logger
from ._conexao import conectar, get_connection, registrar_sync
from .clientes import obter_ou_criar_cliente

logger = get_logger(__name__)


def salvar_nota(nota):
    """
    Salva uma nota, criando remetente/destinatário se necessário.

    Antes: abria até 5 conexões SQLite separadas na mesma operação
    (nota_existe, buscar_cliente_por_cnpj x2, criar_cliente x{0,2}, insert).
    Agora tudo roda em uma única conexão/transação.
    """
    chave_nfe = nota.get("chave_nfe") or nota.get("numero_cte")

    with get_connection() as conn:
        if nota_existe(chave_nfe, conn=conn):
            return False

        remetente_id = obter_ou_criar_cliente(
            nota.get("remetente_nome", ""),
            nota.get("remetente_cnpj", ""),
            nota.get("origem", ""),
            nota.get("uf_origem", ""),
            conn=conn,
        )

        destinatario_id = obter_ou_criar_cliente(
            nota.get("destinatario_nome", ""),
            nota.get("destinatario_cnpj", ""),
            nota.get("destino", ""),
            nota.get("uf_destino", ""),
            conn=conn,
        )

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notas (
                manifesto_id,
                chave_nfe,
                numero_cte,
                remetente_id,
                destinatario_id,
                valor_mercadoria,
                valor_frete,
                peso,
                origem,
                destino,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nota.get("manifesto_id"),
            chave_nfe,
            nota.get("numero_cte", ""),
            remetente_id,
            destinatario_id,
            nota.get("valor_mercadoria", 0),
            nota.get("valor_frete", 0),
            nota.get("peso", 0),
            nota.get("origem", ""),
            nota.get("destino", ""),
            nota.get("status", "Disponível")
        ))

        conn.commit()

    return True


def listar_notas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notas.id,
            notas.chave_nfe,
            notas.numero_cte,
            remetente.nome,
            destinatario.nome,
            notas.origem,
            notas.destino,
            notas.valor_frete,
            notas.peso,
            notas.status
        FROM notas
        LEFT JOIN clientes remetente
            ON remetente.id = notas.remetente_id
        LEFT JOIN clientes destinatario
            ON destinatario.id = notas.destinatario_id
        ORDER BY notas.id DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    return dados


def nota_existe(chave_nfe, conn: Optional[sqlite3.Connection] = None):
    """
    Args:
        conn: conexão opcional já aberta (ver `buscar_cliente_por_cnpj`).
    """
    conexao_propria = conn is None
    if conexao_propria:
        conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM notas WHERE chave_nfe = ?",
        (chave_nfe,)
    )

    resultado = cursor.fetchone()
    if conexao_propria:
        conn.close()

    return resultado is not None


def criar_manifesto(nome_arquivo):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO manifestos (nome_arquivo)
        VALUES (?)
    """, (nome_arquivo,))

    manifesto_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return manifesto_id


def listar_manifestos(tipo_periodo="Geral", mes=None, ano=None):

    conn = conectar()
    cursor = conn.cursor()

    filtro = ""
    params = []

    if tipo_periodo == "Mês" and mes and ano:
        mes = str(mes).zfill(2)
        ano = str(ano)
        filtro = "WHERE substr(manifestos.data_importacao, 6, 2) = ? AND substr(manifestos.data_importacao, 1, 4) = ?"
        params = [mes, ano]

    elif tipo_periodo == "Ano" and ano:
        ano = str(ano)
        filtro = "WHERE substr(manifestos.data_importacao, 1, 4) = ?"
        params = [ano]

    cursor.execute(f"""
        SELECT
            manifestos.id,
            manifestos.nome_arquivo,
            manifestos.data_importacao,
            COUNT(notas.id) as total_notas,
            COALESCE(SUM(notas.valor_mercadoria), 0) as valor_total_notas,
            COALESCE(SUM(notas.valor_frete), 0) as frete_total,
            COALESCE(SUM(notas.peso), 0) as peso_total
        FROM manifestos
        LEFT JOIN notas ON notas.manifesto_id = manifestos.id
        {filtro}
        GROUP BY manifestos.id
        ORDER BY manifestos.id DESC
    """, params)

    dados = cursor.fetchall()
    conn.close()

    return dados


def listar_notas_por_manifesto(manifesto_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notas.id,
            notas.chave_nfe,
            notas.numero_cte,
            remetente.nome,
            destinatario.nome,
            notas.origem,
            notas.destino,
            notas.valor_mercadoria,
            notas.valor_frete,
            notas.peso,
            notas.status
        FROM notas
        LEFT JOIN clientes remetente
            ON remetente.id = notas.remetente_id
        LEFT JOIN clientes destinatario
            ON destinatario.id = notas.destinatario_id
        WHERE notas.manifesto_id = ?
        ORDER BY notas.id DESC
    """, (manifesto_id,))

    dados = cursor.fetchall()
    conn.close()

    return dados


def apagar_manifesto(manifesto_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, nome_arquivo FROM manifestos WHERE id = ?",
            (manifesto_id,)
        )

        manifesto = cursor.fetchone()

        if not manifesto:
            raise Exception("Manifesto não encontrado.")

        cursor.execute(
            "SELECT id FROM notas WHERE manifesto_id = ?",
            (manifesto_id,)
        )

        notas_ids = [linha[0] for linha in cursor.fetchall()]

        for nota_id in notas_ids:
            registrar_sync(cursor, "notas", nota_id, "DELETE")

        registrar_sync(cursor, "manifestos", manifesto_id, "DELETE")

        cursor.execute(
            """
            DELETE FROM viagem_notas
            WHERE nota_id IN (
                SELECT id
                FROM notas
                WHERE manifesto_id = ?
            )
            """,
            (manifesto_id,)
        )

        cursor.execute(
            "DELETE FROM notas WHERE manifesto_id = ?",
            (manifesto_id,)
        )

        cursor.execute(
            "DELETE FROM manifestos WHERE id = ?",
            (manifesto_id,)
        )

        conn.commit()

        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def listar_notas_por_cliente(
    cliente_id: int,
    apenas_disponiveis: bool = True,
    excluir_vinculadas: bool = True
):
    """
    Lista notas filtradas por cliente.
    
    Args:
        cliente_id: ID do cliente (pode ser remetente ou destinatário)
        apenas_disponiveis: Se True, retorna apenas notas com status 'Disponível'
        excluir_vinculadas: Se True, exclui notas já vinculadas a alguma viagem
        
    Returns:
        Lista de tuplas com dados das notas
    """
    conn = conectar()
    cursor = conn.cursor()
    
    query = """
        SELECT
            notas.id,
            notas.numero_cte,
            notas.chave_nfe,
            CASE 
                WHEN notas.destinatario_id = ? THEN destinatario.nome
                WHEN notas.remetente_id = ? THEN remetente.nome
                ELSE COALESCE(destinatario.nome, remetente.nome)
            END as cliente_nome,
            CASE 
                WHEN notas.destinatario_id = ? THEN notas.destino
                WHEN notas.remetente_id = ? THEN notas.origem
                ELSE COALESCE(notas.destino, notas.origem)
            END as cidade,
            notas.peso,
            notas.valor_frete,
            manifestos.data_importacao as data,
            COALESCE(notas.status, 'Disponível') as status
        FROM notas
        LEFT JOIN clientes destinatario
            ON destinatario.id = notas.destinatario_id
        LEFT JOIN clientes remetente
            ON remetente.id = notas.remetente_id
        LEFT JOIN manifestos
            ON manifestos.id = notas.manifesto_id
        WHERE notas.destinatario_id = ? OR notas.remetente_id = ?
    """
    
    params = [cliente_id, cliente_id, cliente_id, cliente_id, cliente_id, cliente_id]
    
    if apenas_disponiveis:
        query += " AND notas.status = 'Disponível'"
    
    if excluir_vinculadas:
        query += """
            AND notas.id NOT IN (
                SELECT nota_id
                FROM viagem_notas
            )
        """
    
    query += " ORDER BY notas.id DESC"
    
    cursor.execute(query, params)
    dados = cursor.fetchall()
    conn.close()
    
    return dados


def calcular_resumo_notas(notas_ids: list, conn: Optional[sqlite3.Connection] = None):
    """
    Calcula resumo das notas selecionadas.
    
    Args:
        notas_ids: Lista de IDs das notas
        conn: conexão opcional já aberta (ver `dados_dashboard`).
        
    Returns:
        Dict com quantidade, peso_total, frete_total, volumes
    """
    if not notas_ids:
        return {
            "quantidade": 0,
            "peso_total": 0,
            "frete_total": 0,
            "volumes": 0
        }
    
    conexao_propria = conn is None
    if conexao_propria:
        conn = conectar()
    cursor = conn.cursor()
    
    placeholders = ",".join(["?"] * len(notas_ids))
    
    cursor.execute(f"""
        SELECT
            COUNT(*) as quantidade,
            COALESCE(SUM(peso), 0) as peso_total,
            COALESCE(SUM(valor_frete), 0) as frete_total
        FROM notas
        WHERE id IN ({placeholders})
    """, notas_ids)
    
    quantidade, peso_total, frete_total = cursor.fetchone()
    
    # Volumes é estimado como 1 volume por nota (pode ser ajustado no futuro)
    volumes = quantidade
    
    if conexao_propria:
        conn.close()
    
    return {
        "quantidade": quantidade or 0,
        "peso_total": peso_total or 0,
        "frete_total": frete_total or 0,
        "volumes": volumes or 0
    }



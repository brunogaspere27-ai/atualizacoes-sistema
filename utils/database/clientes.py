"""Consultas e cadastro de clientes."""

import sqlite3
from typing import Optional

from utils.logger import get_logger
from ._conexao import conectar

logger = get_logger(__name__)


def buscar_cliente_por_cnpj(cnpj, conn: Optional[sqlite3.Connection] = None):
    """
    Args:
        conn: conexão opcional já aberta, reaproveitada por `obter_ou_criar_cliente`
            e `salvar_nota` para evitar abrir várias conexões na mesma operação.
    """
    conexao_propria = conn is None
    if conexao_propria:
        conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM clientes WHERE cnpj = ?",
        (cnpj,)
    )

    resultado = cursor.fetchone()
    if conexao_propria:
        conn.close()

    if resultado:
        return resultado[0]

    return None


def criar_cliente(nome, cnpj, cidade="", uf="", conn: Optional[sqlite3.Connection] = None):
    """
    Args:
        conn: conexão opcional já aberta (ver `buscar_cliente_por_cnpj`).
    """
    conexao_propria = conn is None
    if conexao_propria:
        conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes
        (nome, cnpj, cidade, uf)
        VALUES (?, ?, ?, ?)
    """, (nome, cnpj, cidade, uf))

    cliente_id = cursor.lastrowid

    conn.commit()
    if conexao_propria:
        conn.close()

    return cliente_id


def obter_ou_criar_cliente(nome, cnpj, cidade="", uf="", conn: Optional[sqlite3.Connection] = None):
    """
    Args:
        conn: conexão opcional já aberta (ver `buscar_cliente_por_cnpj`).
    """
    if not cnpj:
        cnpj = nome

    cliente_id = buscar_cliente_por_cnpj(cnpj, conn=conn)

    if cliente_id:
        return cliente_id

    return criar_cliente(nome, cnpj, cidade, uf, conn=conn)


def buscar_clientes_por_nome(termo_busca: str):
    """
    Busca clientes pelo nome (destinatários).
    
    Args:
        termo_busca: Termo para busca (pode ser parcial)
        
    Returns:
        Lista de tuplas (id, nome, cnpj, cidade, uf)
    """
    conn = conectar()
    cursor = conn.cursor()
    
    termo = f"%{termo_busca}%"
    
    cursor.execute("""
        SELECT id, nome, cnpj, cidade, uf
        FROM clientes
        WHERE nome LIKE ?
        ORDER BY nome
        LIMIT 50
    """, (termo,))
    
    dados = cursor.fetchall()
    conn.close()
    
    return dados



"""Busca global offline-first para a interface PySide6.

As consultas usam somente o SQLite local, que é a fonte de verdade durante o
uso do aplicativo. Assim os mesmos resultados ficam disponíveis com ou sem
internet; a sincronização apenas mantém essa base atualizada.

Implementa busca inteligente estilo ERP profissional (Notion, Attio, Linear):
- Ignora maiúsculas/minúsculas
- Ignora acentos
- Aceita pesquisa parcial
- Busca simultânea em múltiplos campos
- Resultados agrupados por categoria
"""

from __future__ import annotations

import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from utils.database import get_connection_rows
from utils.logger import get_logger

logger = get_logger(__name__)


def normalizar_texto(valor: object) -> str:
    """Converte texto para uma forma comparável, sem acentos e sem caixa."""
    texto = unicodedata.normalize("NFKD", str(valor or ""))
    texto = "".join(char for char in texto if not unicodedata.combining(char))
    return " ".join(texto.casefold().split())


@dataclass(frozen=True)
class SearchResult:
    categoria: str
    titulo: str
    descricao: str
    tela: str
    registro_id: int | str
    icon: str
    cliente_data: tuple = None  # (id, nome) para clientes que vão para criar_viagem


class SearchService:
    """Consulta cadastros importantes com semântica consistente de pesquisa."""

    _SOURCES: Sequence[Dict[str, object]] = (
        # Clientes - busca em nome, razão social, fantasia, CPF/CNPJ, cidade, telefone
        {"table": "clientes", "category": "Clientes", "screen": "criar_viagem", "icon": "groups",
         "title": ("nome", "razao_social", "fantasia"), 
         "description": ("cnpj", "cpf", "cidade", "uf", "telefone")},
        
        # Notas - busca em número CTE, chave NFE, origem, destino, status
        {"table": "notas", "category": "Notas", "screen": "notas", "icon": "notes",
         "title": ("numero_cte", "chave_nfe"), 
         "description": ("origem", "destino", "status")},
        
        # Operações - busca em número, descrição, caminhão, placa, motorista
        {"table": "operacoes_sp", "category": "Operações", "screen": "operacoes", "icon": "operations",
         "title": ("nome_caminhao", "placa", "numero_operacao"), 
         "description": ("motorista", "descricao", "data_operacao", "cidade_origem", "cidade_destino")},
        
        # Viagens - busca em motorista, placa, cliente, cidade origem/destino
        {"table": "viagens", "category": "Viagens", "screen": "historico", "icon": "trips",
         "title": ("motorista", "placa", "cliente"), 
         "description": ("cidade_origem", "cidade_destino", "status", "data_saida", "data_retorno")},
        
        # Motoristas/Funcionários - busca em nome, cargo, telefone
        {"table": "funcionarios", "category": "Motoristas", "screen": "funcionarios", "icon": "badge",
         "title": ("nome",), 
         "description": ("cargo", "telefone", "cpf", "cnh", "status")},
        
        # Caminhões - busca em placa, modelo, ano, motorista
        {"table": "caminhoes", "category": "Caminhões", "screen": "manutencao", "icon": "truck",
         "title": ("placa", "modelo", "ano"), 
         "description": ("motorista", "marca", "cor", "status")},
        
        # Usuários - busca em nome, usuário, email
        {"table": "usuarios", "category": "Usuários", "screen": "usuarios", "icon": "user_circle",
         "title": ("nome_completo", "usuario"), 
         "description": ("email", "nivel_acesso", "telefone")},
    )

    def search(self, query: str, limit_per_group: int = 20) -> List[SearchResult]:
        """
        Retorna resultados parciais, sem acentos e sem sensibilidade a caixa.
        
        Implementa busca inteligente estilo ERP:
        - Pesquisa parcial: "sch" encontra "Schuster", "Transportes Schuster"
        - Ignora maiúsculas/minúsculas
        - Ignora acentos
        - Busca em múltiplos campos simultaneamente
        - Resultados agrupados por categoria
        - Query vazia retorna todos os registros (sem limite)
        
        Args:
            query: Termo de busca
            limit_per_group: Limite de resultados por categoria (padrão 20, ignorado se query vazia)
            
        Returns:
            Lista de SearchResult agrupados por categoria
        """
        terms = [term for term in normalizar_texto(query).split(" ") if term]

        resultados: List[SearchResult] = []
        try:
            with get_connection_rows() as conn:
                conn.create_function("NORMALIZE", 1, normalizar_texto)
                for source in self._SOURCES:
                    if terms:
                        resultados.extend(self._search_source(conn, source, terms, limit_per_group))
                    else:
                        # Query vazia: buscar todos os registros sem limite
                        resultados.extend(self._search_source_all(conn, source, limit=None))
        except sqlite3.Error as exc:
            logger.warning(f"Busca global indisponível temporariamente: {exc}")
        return resultados

    def _search_source(
        self, conn: sqlite3.Connection, source: Dict[str, object], terms: Iterable[str], limit: int
    ) -> List[SearchResult]:
        """
        Busca em uma tabela específica usando busca inteligente.
        
        Usa OR entre termos para pesquisa parcial mais flexível.
        Qualquer termo que corresponder em qualquer campo retornará o resultado.
        """
        table = str(source["table"])
        columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        if not columns or "id" not in columns:
            return []

        title_fields = [field for field in source["title"] if field in columns]
        description_fields = [field for field in source["description"] if field in columns]
        searchable = title_fields + description_fields
        if not searchable:
            return []

        # Usar OR entre termos para pesquisa parcial mais flexível
        # Se qualquer termo corresponder em qualquer campo, retorna o resultado
        predicates, params = [], []
        haystack = " || ' ' || ".join(f"COALESCE({field}, '')" for field in searchable)
        
        for term in terms:
            predicates.append(f"NORMALIZE({haystack}) LIKE ?")
            params.append(f"%{term}%")

        # Usar OR em vez de AND para pesquisa parcial mais flexível
        sql = f"SELECT id, {', '.join(searchable)} FROM {table} WHERE {' OR '.join(predicates)} LIMIT ?"
        rows = conn.execute(sql, [*params, limit]).fetchall()
        return [self._make_result(row, source, title_fields, description_fields) for row in rows]

    def _search_source_all(
        self, conn: sqlite3.Connection, source: Dict[str, object], limit: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Busca todos os registros de uma tabela (para query vazia).
        
        Args:
            conn: Conexão SQLite
            source: Configuração da fonte de dados
            limit: Limite de resultados (None = sem limite)
            
        Returns:
            Lista de SearchResult
        """
        table = str(source["table"])
        columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        if not columns or "id" not in columns:
            return []

        title_fields = [field for field in source["title"] if field in columns]
        description_fields = [field for field in source["description"] if field in columns]
        searchable = title_fields + description_fields
        if not searchable:
            return []

        if limit is not None:
            sql = f"SELECT id, {', '.join(searchable)} FROM {table} ORDER BY id DESC LIMIT ?"
            rows = conn.execute(sql, [limit]).fetchall()
        else:
            sql = f"SELECT id, {', '.join(searchable)} FROM {table} ORDER BY id DESC"
            rows = conn.execute(sql).fetchall()
        return [self._make_result(row, source, title_fields, description_fields) for row in rows]

    @staticmethod
    def _make_result(row, source: Dict[str, object], title_fields: List[str], description_fields: List[str]) -> SearchResult:
        """
        Cria um SearchResult a partir de uma linha do banco de dados.
        
        Formata o título de forma inteligente dependendo da categoria:
        - Notas: "NF 20314"
        - Viagens: "Viagem #105 · Motorista"
        - Operações: "Operação #421 · Descrição"
        - Outros: Primeiro campo disponível
        """
        # Helper para acessar campos de sqlite3.Row de forma segura
        def get_field(field_name: str, default: str = "") -> str:
            try:
                val = row[field_name]
                return str(val).strip() if val else default
            except (KeyError, IndexError):
                return default
        
        title_values = [get_field(field) for field in title_fields if get_field(field)]
        description_values = [get_field(field) for field in description_fields if get_field(field)]
        title = " · ".join(title_values) or f"Registro #{get_field('id')}"
        
        # Formatação especial por categoria
        if source["category"] == "Notas":
            cte = get_field("numero_cte")
            nfe = get_field("chave_nfe")
            if cte:
                title = f"CT-e {cte}"
            elif nfe:
                title = f"NFE {nfe[:20]}..."
            else:
                title = f"NF {title}"
        elif source["category"] == "Viagens":
            title = f"Viagem #{get_field('id')} · {title}"
        elif source["category"] == "Operações":
            title = f"Operação #{get_field('id')} · {title}"
        elif source["category"] == "Clientes":
            # Priorizar nome fantasia se disponível
            fantasia = get_field("fantasia")
            if fantasia:
                nome = get_field("nome")
                title = f"{fantasia} ({nome})" if nome else fantasia
        
        # Para clientes, incluir dados para pré-seleção na tela criar_viagem
        cliente_data = None
        if source["category"] == "Clientes":
            cliente_id = get_field("id")
            try:
                cliente_id = int(cliente_id)  # Converter para int
            except (ValueError, TypeError):
                cliente_id = 0
            cliente_nome = title  # Usar o title formatado como nome
            cliente_data = (cliente_id, cliente_nome)
        
        return SearchResult(
            categoria=str(source["category"]), 
            titulo=title,
            descricao=" · ".join(description_values) or "Cadastro do sistema",
            tela=str(source["screen"]), 
            registro_id=get_field("id"), 
            icon=str(source["icon"]),
            cliente_data=cliente_data,
        )


search_service = SearchService()

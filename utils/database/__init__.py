"""
Camada de acesso a dados (SQLite) do CW Transportadora.

Este pacote substitui o antigo modulo unico utils/database.py (1782 linhas),
dividido por dominio para facilitar manutencao:

- _conexao.py    conexao, schema, migracao, rastreamento de sync
- clientes.py    cadastro/consulta de clientes
- notas.py       notas fiscais e manifestos
- caminhoes.py   frota
- viagens.py     ciclo de vida de viagens
- relatorios.py  dashboard, ranking, top destinos, operacoes SP

Todo o codigo do resto do projeto continua funcionando sem alteracao:
`from utils.database import criar_banco` (ou qualquer outro nome publico)
funciona exatamente como antes, pois este __init__ reexporta tudo.
"""

from ._conexao import (
    PASTA_DADOS,
    DB_NAME,
    TABELAS_SYNC,
    migrar_banco_antigo,
    get_connection,
    get_connection_rows,
    tabela_existe_sqlite,
    conectar,
    agora_sync,
    marcar_registro_para_sync,
    obter_referencia_sync,
    registrar_sync,
    criar_indices,
    criar_banco,
    corrigir_tabela_viagem_notas,
    registrar_caminhoes_para_sync,
)

from .clientes import (
    buscar_cliente_por_cnpj,
    criar_cliente,
    obter_ou_criar_cliente,
    buscar_clientes_por_nome,
)

from .notas import (
    salvar_nota,
    listar_notas,
    nota_existe,
    criar_manifesto,
    listar_manifestos,
    listar_notas_por_manifesto,
    apagar_manifesto,
    listar_notas_por_cliente,
    calcular_resumo_notas,
)

from .caminhoes import (
    listar_caminhoes,
    apagar_todos_caminhoes,
    criar_caminhoes_padrao,
    cadastrar_caminhao,
)

from .viagens import (
    criar_viagem,
    apagar_viagem,
    listar_viagens,
    listar_notas_da_viagem,
    finalizar_viagem,
    buscar_detalhes_viagem,
)

from .relatorios import (
    dados_dashboard,
    top_destinos_dashboard,
    criar_operacao_sp,
    listar_operacoes_sp,
    gerar_ranking_clientes_v6,
)

__all__ = [
    "PASTA_DADOS", "DB_NAME", "TABELAS_SYNC",
    "migrar_banco_antigo", "get_connection", "get_connection_rows",
    "tabela_existe_sqlite", "conectar", "agora_sync",
    "marcar_registro_para_sync", "obter_referencia_sync", "registrar_sync",
    "criar_indices", "criar_banco", "corrigir_tabela_viagem_notas",
    "registrar_caminhoes_para_sync",
    "buscar_cliente_por_cnpj", "criar_cliente", "obter_ou_criar_cliente",
    "buscar_clientes_por_nome",
    "salvar_nota", "listar_notas", "nota_existe", "criar_manifesto",
    "listar_manifestos", "listar_notas_por_manifesto", "apagar_manifesto",
    "listar_notas_por_cliente", "calcular_resumo_notas",
    "listar_caminhoes", "apagar_todos_caminhoes", "criar_caminhoes_padrao",
    "cadastrar_caminhao",
    "criar_viagem", "apagar_viagem", "listar_viagens",
    "listar_notas_da_viagem", "finalizar_viagem", "buscar_detalhes_viagem",
    "dados_dashboard", "top_destinos_dashboard", "criar_operacao_sp",
    "listar_operacoes_sp", "gerar_ranking_clientes_v6",
]

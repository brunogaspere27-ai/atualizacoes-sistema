---
name: Conexão SQLite opcional (conn=None) no CW Transportadora
description: Padrão para evitar múltiplas conexões SQLite na mesma operação lógica sem reescrever a camada de dados nem introduzir pooling.
---

No projeto CW Transportadora (`utils/database.py`), funções de baixo nível que
fazem consultas (ex.: `dados_dashboard`, `listar_caminhoes`,
`calcular_resumo_notas`, `buscar_cliente_por_cnpj`) aceitam um parâmetro
opcional `conn: Optional[sqlite3.Connection] = None`.

- Se `conn` não for passada, a função abre e fecha sua própria conexão
  (comportamento simples, correto para chamadas isoladas).
- Se uma função orquestradora (ex.: `DashboardService.carregar_dashboard`,
  `RelatoriosService.carregar_relatorio`, `ViagemService.validar_capacidade`)
  precisa combinar várias dessas consultas na mesma operação, ela abre uma
  única conexão e a passa para cada chamada, evitando N conexões redundantes.

**Why:** o usuário pediu explicitamente para otimizar apenas os pontos onde
múltiplas conexões SQLite eram abertas dentro da mesma operação lógica — e
proibiu reescrever toda a camada de acesso a dados ou adicionar pool de
conexões (desnecessário para SQLite). Esse padrão já existia parcialmente no
código (`utils/importador_txt.py` tinha variantes `_cursor`, e
`criar_viagem` já usava `get_connection()` como context manager).

**How to apply:** ao adicionar uma nova função de consulta que pode ser
chamada tanto isoladamente quanto dentro de uma operação maior, siga o mesmo
padrão (`conn=None` + flag `conexao_propria` para decidir se fecha a conexão
no final) em vez de inventar uma abordagem diferente.

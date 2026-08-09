# Auditoria CW Transportadora - Refatoração Visual

## Arquitetura Atual

### Estrutura de Pastas
```
CW_TRANSPORTADORA atualizado/
├── config/              # Configurações
├── services/            # 28 serviços de negócio
├── telas/               # ~40 telas (Python/PySide6/CustomTkinter)
├── utils/               # Utilitários e componentes
├── testes/              # Testes
└── main_pyside6.py      # Entry point principal
```

### Sistemas de Tema Identificados
1. **Aurora** - Sistema com gradientes, glassmorphism, muito roxo
2. **PySide6** - Sistema básico de tema
3. **SaaS** - Outro sistema de tema

### Telas PySide6 (ativas)
- auditoria_pyside6.py
- combustivel_pyside6.py
- configuracoes_pyside6.py
- contas_pyside6.py
- criar_viagem_pyside6.py
- dashboard_pyside6.py
- funcionarios_pyside6.py
- gerenciar_usuarios_pyside6.py
- historico_pyside6.py
- historico_versoes_pyside6.py
- login_pyside6.py
- manutencao_pyside6.py
- notas_pyside6.py
- operacoes_pyside6.py
- perfil_pyside6.py
- ranking_pyside6.py
- relatorios_pyside6.py
- theme_pyside6.py

### Telas Aurora (parciais)
- login_aurora.py
- notas_aurora.py
- dashboard_aurora.py
- ranking_aurora.py
- operacoes_aurora.py
- theme_aurora.py

### Componentes Existentes
- components_aurora.py - Botões, cards com gradientes
- components.py - Componentes legados
- components_saaS.py - Outro sistema de componentes
- widgets.py - Widgets customizados

## Problemas Identificados

### 1. Identidade Visual
- ❌ Sistema Aurora usa muito roxo (viola requisito)
- ❌ Cor principal não é #D32F2F (Vermelho CW)
- ❌ Múltiplos gradientes exagerados
- ❌ Glassmorphism excessivo

### 2. Inconsistência
- ❌ 3 sistemas de temas diferentes
- ❌ Telas misturadas (PySide6 vs Aurora)
- ❌ Componentes duplicados
- ❌ Stylesheets espalhados

### 3. Componentes
- ❌ Botões com gradientes (não profissional)
- ❌ Cards com sombras grandes
- ❌ Ícones inconsistentes
- ❌ Tabelas estilo Qt padrão

### 4. Navegação
- ⚠️ Sidebar existe mas pode ser melhorado
- ⚠️ Header existe mas pode ser mais profissional
- ⚠️ Sistema de busca global existe

### 5. Funcionalidades
- ✅ Todos os serviços funcionam
- ✅ Banco de dados está intacto
- ✅ Lógica de negócio preservada

## Plano de Refatoração

### FASE 1: Design System CW Premium
- Criar novo tema baseado em #D32F2F
- Light mode premium como padrão
- Remover roxo completamente
- Tipografia Inter refinada
- Sistema de spacing consistente
- Border radius profissional (não exagerado)

### FASE 2: Componentes Base
- Botões sólidos (sem gradientes)
- Cards discretos (sem sombras grandes)
- Inputs modernos
- Tabelas profissionais
- Ícones consistentes

### FASE 3: Shell Principal
- Sidebar moderno SaaS
- Header profissional
- Navegação unificada

### FASE 4: Dashboard
- KPIs executivos
- Gráficos profissionais
- Layout hierárquico

### FASE 5: Telas Progressivas
1. Notas
2. Viagens (criar_viagem)
3. Clientes
4. Motoristas
5. Veículos
6. Combustível
7. Relatórios
8. Configurações

### FASE 6: Estados e Feedback
- Loading states
- Empty states
- Error states
- Toast notifications
- Dialogs modernos

## Estrutura Final Proposta

```
ui/
├── theme/
│   ├── cw_theme.py          # Design System CW
│   ├── colors.py            # Paleta CW
│   ├── typography.py        # Tipografia
│   └── tokens.py            # Spacing, radius, shadows
│
├── components/
│   ├── buttons/
│   │   ├── cw_button.py
│   │   └── button_group.py
│   ├── cards/
│   │   ├── cw_card.py
│   │   └── kpi_card.py
│   ├── inputs/
│   │   ├── cw_input.py
│   │   └── cw_select.py
│   ├── tables/
│   │   └── cw_table.py
│   ├── navigation/
│   │   ├── cw_sidebar.py
│   │   └── cw_header.py
│   └── feedback/
│       ├── cw_toast.py
│       └── cw_dialog.py
│
└── pages/
    ├── dashboard/
    ├── notas/
    ├── viagens/
    ├── clientes/
    └── ...
```

## Prioridade de Execução

1. Design System (sem quebrar funcionalidade)
2. Componentes base (reutilizáveis)
3. Shell (Sidebar + Header)
4. Dashboard (visão executiva)
5. Telas principais (Notas, Viagens)
6. Telas secundárias
7. Estados e feedback
8. Testes completos

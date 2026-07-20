# Guia de Migração: CustomTkinter → PySide6

## Visão Geral

Este documento descreve o processo de migração da interface do sistema CW Transportadora de CustomTkinter para PySide6 (Qt6), mantendo 100% das funcionalidades e da lógica de negócio.

## Status Atual

### ✅ Concluído

- [x] Análise da arquitetura existente
- [x] Avaliação de benefícios da migração
- [x] Design da nova arquitetura PySide6
- [x] Atualização de dependências (requirements.txt)
- [x] Sistema de temas claro/escuro
- [x] Sistema de ícones SVG
- [x] Componentes base reutilizáveis
- [x] Migração do main.py
- [x] Migração da tela de login
- [x] Migração do dashboard

### 🔄 Em Progresso

- [ ] Migração das telas restantes (18 telas)
- [ ] Implementação de tabelas profissionais
- [ ] Adição de animações discretas

### 📋 Pendente

- [ ] Testes de funcionalidade
- [ ] Documentação de componentes
- [ ] Deploy da nova versão

## Arquitetura Preservada

A arquitetura do sistema foi **100% preservada**:

```
CW_TRANSPORTADORA/
├── main.py (main_pyside6.py)          # Ponto de entrada (migrado)
├── config/                            # Configurações (preservado)
│   └── settings.py
├── services/                          # Lógica de negócio (preservado)
│   ├── auth_service.py
│   ├── dashboard_service.py
│   ├── sync_service.py
│   └── ...
├── utils/                             # Utilitários (preservado)
│   ├── database.py
│   ├── sync.py
│   └── icons.py (NOVO)
│   └── components.py (NOVO)
├── telas/                             # Interface (migrando)
│   ├── theme.py (preservado - compatibilidade)
│   ├── theme_pyside6.py (NOVO)
│   ├── login.py (preservado)
│   ├── login_pyside6.py (NOVO)
│   ├── dashboard.py (preservado)
│   ├── dashboard_pyside6.py (NOVO)
│   └── ... (demais telas)
└── migrations/                        # Banco de dados (preservado)
```

## Novos Componentes Criados

### 1. Sistema de Temas (`telas/theme_pyside6.py`)

- **ThemeManager**: Gerenciador central de temas
- **LightTheme**: Tema claro profissional
- **DarkTheme**: Tema escuro premium
- **AccentColor**: Cores de acento por categoria
- **ThemeTokens**: Tokens de design globais

**Uso:**
```python
from telas.theme_pyside6 import theme_manager, AccentColor

# Obter cor
cor = theme_manager.get_color("brand")

# Obter cor de acento
accent = theme_manager.get_accent(AccentColor.EMERALD)

# Alternar tema
theme_manager.toggle_mode()

# Aplicar stylesheet
app.setStyleSheet(theme_manager.get_stylesheet())
```

### 2. Sistema de Ícones (`utils/icons.py`)

- **IconProvider**: Provedor de ícones SVG
- **Ícones inline**: 50+ ícones SVG embutidos
- **Suporte a cores**: Ícones com cores dinâmicas

**Uso:**
```python
from utils.icons import get_icon, get_pixmap

# Obter QIcon
icon = get_icon("home", color="#DC2626")

# Obter QPixmap
pixmap = get_pixmap("dashboard", size=QSize(32, 32))
```

### 3. Componentes Base (`utils/components.py`)

- **ModernButton**: Botão com estilos variados
- **ModernCard**: Card com bordas arredondadas
- **ModernSidebar**: Sidebar de navegação
- **ModernHeader**: Header com título/subtítulo
- **ModernInput**: Input com validação visual
- **ModernComboBox**: ComboBox estilizado
- **KPICard**: Card de KPI com ícone
- **StatusBadge**: Badge de status

**Uso:**
```python
from utils.components import (
    ModernButton, ButtonStyle, ModernCard,
    KPICard, AccentColor
)

# Botão
btn = ModernButton("Salvar", ButtonStyle.PRIMARY, "save")

# Card
card = ModernCard("Título", parent=self)

# KPI
kpi = KPICard("Receita", "R$ 10.000", "Mês atual", "money", AccentColor.EMERALD)
```

## Como Migrar uma Tela

### Passo 1: Analisar a tela original

Estude a tela em `telas/nome_tela.py` para entender:
- Layout e componentes
- Conexões com services
- Eventos e callbacks
- Validações

### Passo 2: Criar nova tela PySide6

Crie `telas/nome_tela_pyside6.py`:

```python
"""
Tela [Nome] CW Transportadora - PySide6

Descrição da funcionalidade.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

from config.settings import settings
from services.nome_service import nome_service
from telas.theme_pyside6 import theme_manager, AccentColor
from utils.icons import get_icon
from utils.components import ModernCard, ModernButton, ButtonStyle

class TelaNome(QWidget):
    """Tela [Nome] moderna em PySide6."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Configura a interface."""
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL)
        layout.setSpacing(tokens.SPACING_XL)
        self.setLayout(layout)
        
        # Adicionar componentes...
    
    def _load_data(self):
        """Carrega dados dos services."""
        # Usar services existentes
        dados = nome_service.obter_dados()
        self._update_ui(dados)
    
    def _update_ui(self, dados):
        """Atualiza a interface com os dados."""
        # Atualizar componentes...
```

### Passo 3: Integrar no main.py

Adicione em `main_pyside6.py`:

```python
# Importar
from telas.nome_tela_pyside6 import TelaNome

# Adicionar método
def _load_tela_nome(self):
    """Carrega a tela [Nome]."""
    if "nome_tela" not in self.telas:
        self.telas["nome_tela"] = TelaNome()
        self.stacked_widget.addWidget(self.telas["nome_tela"])
    
    self.stacked_widget.setCurrentWidget(self.telas["nome_tela"])

# Adicionar no _load_tela
def _load_tela(self, tela: str):
    # ... código existente ...
    
    if tela == "nome_tela":
        self._load_tela_nome()
        return
```

### Passo 4: Testar

1. Execute `python main_pyside6.py`
2. Navegue até a tela migrada
3. Verifique funcionalidades
4. Compare com tela original

## Telas Pendentes de Migração

Prioridade sugerida (baseada em complexidade e uso):

### Alta Prioridade
1. **operacoes** - Transferências SP → Cascavel
2. **notas** - Importação de notas fiscais
3. **criar_viagem** - Montagem de viagens
4. **historico** - Histórico de viagens
5. **contas** - Contas a pagar/receber

### Média Prioridade
6. **relatorios** - Geração de relatórios
7. **funcionarios** - Gestão de funcionários
8. **combustivel** - Controle de abastecimento
9. **manutencao** - Manutenção da frota
10. **ranking_clientes** - Ranking de clientes

### Baixa Prioridade (Admin)
11. **configuracoes** - Configurações do sistema
12. **gerenciar_usuarios** - Gestão de usuários
13. **auditoria** - Logs de auditoria
14. **historico_versoes** - Histórico de versões
15. **publicar_versao** - Publicação de versões
16. **admin_atualizacoes** - Admin de atualizações
17. **alterar_senha** - Alteração de senha
18. **atualizacao** - Tela de atualização

## Padrões de Migração

### Substituição de Componentes

| CustomTkinter | PySide6 | Componente |
|---------------|---------|------------|
| `ctk.CTkButton` | `ModernButton` | Botão estilizado |
| `ctk.CTkEntry` | `ModernInput` | Input de texto |
| `ctk.CTkFrame` | `ModernCard` | Card/Container |
| `ctk.CTkLabel` | `QLabel` | Label |
| `ctk.CTkOptionMenu` | `ModernComboBox` | Dropdown |
| `ttk.Treeview` | `QTableView` | Tabela (TODO) |

### Substituição de Cores

```python
# Antes (CustomTkinter)
cor = self.cores["brand"]
fundo = self.cores["fundo"]

# Depois (PySide6)
cor = theme_manager.get_color("brand")
fundo = theme_manager.get_color("bg_primary")
```

### Substituição de Ícones

```python
# Antes (CustomTkinter - emoji)
icone = "🏠"

# Depois (PySide6 - SVG)
icone = get_icon("home")
```

### Substituição de Layouts

```python
# Antes (CustomTkinter)
widget.pack(fill="x", padx=10, pady=5)
widget.grid(row=0, column=0, sticky="ew")

# Depois (PySide6)
layout.addWidget(widget)
layout.addWidget(widget, stretch=1)
grid_layout.addWidget(widget, 0, 0)
```

## Implementação de Tabelas Profissionais

Para telas com tabelas (Treeview), implementar QTableView:

```python
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import QAbstractTableModel, Qt

class TableModel(QAbstractTableModel):
    """Modelo de tabela para dados."""
    
    def __init__(self, data, headers, parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = headers
    
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

# Uso
table = QTableView()
model = TableModel(dados, ["Col1", "Col2", "Col3"])
table.setModel(model)
```

## Adição de Animações

Para animações discretas:

```python
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

def animate_fade_in(widget):
    """Animação de fade-in."""
    opacity = widget.windowOpacity()
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(300)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.InOutQuad)
    animation.start()
```

## Testes

### Teste de Funcionalidade

Para cada tela migrada:

1. **Login**: Testar autenticação
2. **Navegação**: Testar acesso à tela
3. **CRUD**: Testar criação, leitura, atualização, exclusão
4. **Validações**: Testar validações de formulário
5. **Integração**: Testar integração com services

### Teste de UI

1. **Tema claro/escuro**: Testar alternância
2. **Responsividade**: Testar redimensionamento
3. **Acessibilidade**: Testar navegação por teclado
4. **Performance**: Testar tempo de carregamento

## Deploy

### Preparação

1. Atualizar `requirements.txt`:
```txt
PySide6==6.6.3
PySide6-Addons==6.6.3
```

2. Instalar dependências:
```bash
pip install -r requirements.txt
```

3. Testar nova versão:
```bash
python main_pyside6.py
```

### Migração de Produção

1. **Backup**: Fazer backup do banco de dados
2. **Teste**: Testar em ambiente de homologação
3. **Deploy**: Substituir `main.py` por `main_pyside6.py`
4. **Monitoramento**: Monitorar logs e erros

### Rollback

Se necessário, rollback é simples:
```bash
# Restaurar versão anterior
git checkout HEAD~1 main.py
python main.py
```

## Benefícios da Migração

### Visual
- ✅ Interface moderna de ERP 2026
- ✅ Sidebar com ícones SVG
- ✅ Cards elegantes e profissionais
- ✅ Tabelas com sorting/filtering
- ✅ Tema claro/escuro
- ✅ Tipografia moderna
- ✅ Espaçamentos consistentes

### Técnico
- ✅ Framework mais moderno (Qt6)
- ✅ Melhor performance
- ✅ Maior comunidade
- ✅ Melhor documentação
- ✅ Componentes mais avançados
- ✅ Suporte a animações nativas
- ✅ Melhor renderização de texto

### Manutenibilidade
- ✅ Código mais limpo
- ✅ Componentes reutilizáveis
- ✅ Sistema de temas centralizado
- ✅ Ícones escaláveis
- ✅ Separação clara de responsabilidades

## Suporte e Documentação

### Qt Documentation
- https://doc.qt.io/qtforpython/
- https://doc.qt.io/qt-6/

### PySide6 Documentation
- https://pyside6.readthedocs.io/

### Ícones
- https://lucide.dev/ (fonte dos ícones SVG)

## Próximos Passos

1. Migrar telas de alta prioridade
2. Implementar QTableView para tabelas
3. Adicionar animações discretas
4. Testar todas as funcionalidades
5. Documentar componentes customizados
6. Preparar deploy para produção

## Contato e Suporte

Para dúvidas ou problemas durante a migração:
- Consultar este guia
- Verificar documentação do Qt
- Analisar telas já migradas como referência

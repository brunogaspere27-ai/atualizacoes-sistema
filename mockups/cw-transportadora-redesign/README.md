# CW Transportadora - Redesign Mockup

Sistema de gestão de transportadora com interface Enterprise SaaS Modern.

## 📋 Visão Geral

Este mockup apresenta o redesign completo do sistema CW Transportadora, substituindo o design system "NEXUS v8.0" por uma interface moderna, profissional e confiável inspirada em plataformas SaaS B2B como Salesforce e HubSpot.

## 🎨 Design System

O projeto utiliza um design system completo documentado em `DESIGN_SYSTEM.md`, incluindo:

- **Paleta de Cores**: Professional Blue (IBM Blue vibrante) com cores de status e acentos
- **Tipografia**: Inter (texto) e JetBrains Mono (números/dados)
- **Espaçamento**: Escala baseada em unidades de 4px
- **Componentes**: Cards, botões, formulários, tabelas, badges, tabs
- **Dark Mode**: Suporte nativo a tema escuro

## 📁 Estrutura do Projeto

```
cw-transportadora-redesign/
├── assets/
│   ├── icons/           # Ícones SVG de navegação e ações
│   └── images/          # Imagens e ilustrações
├── css/
│   └── styles.css       # Folha de estilos principal
├── js/
│   └── app.js           # JavaScript da aplicação
├── index.html           # Página principal do sistema
├── login.html           # Página de login
├── DESIGN_SYSTEM.md     # Documentação do design system
└── README.md            # Este arquivo
```

## 🚀 Como Visualizar

### Opção 1: Abrir Diretamente no Navegador

1. Navegue até a pasta do projeto:
   ```
   C:\Users\bruno\OneDrive\Desktop\APLICATIVO ATT\CW_TRANSPORTADORA atualizado\mockups\cw-transportadora-redesign\
   ```

2. Dê duplo clique em `index.html` para abrir no navegador padrão

3. Para ver a tela de login, abra `login.html`

### Opção 2: Usar um Servidor Local (Recomendado)

Para uma experiência melhor com recursos do navegador, use um servidor local:

#### Com Python 3:
```bash
cd "C:\Users\bruno\OneDrive\Desktop\APLICATIVO ATT\CW_TRANSPORTADORA atualizado\mockups\cw-transportadora-redesign"
python -m http.server 8000
```

Depois acesse: `http://localhost:8000`

#### Com Node.js (http-server):
```bash
cd "C:\Users\bruno\OneDrive\Desktop\APLICATIVO ATT\CW_TRANSPORTADORA atualizado\mockups\cw-transportadora-redesign"
npx http-server
```

#### Com VS Code:
1. Abra a pasta no VS Code
2. Instale a extensão "Live Server"
3. Clique com botão direito em `index.html` e selecione "Open with Live Server"

## 📱 Telas Implementadas

O mockup inclui todas as 17 telas do sistema:

### Principal
1. **Dashboard Executivo** - Visão geral com 12 KPIs e 7 gráficos interativos

### Operacional
2. **Notas/Manifestos** - Importação de TXT, gestão de notas e manifestos
3. **Nova Operação** - Formulário para criar operações SP → Cascavel
4. **Criar Viagem** - Seleção de notas e organização de viagens
5. **Histórico de Viagens** - Lista de viagens com status e ações
6. **Ranking de Clientes** - Classificação por volume e valor

### Frota
7. **Combustível** - Registro de abastecimentos e consumo
8. **Manutenção** - Controle de revisões e alertas

### Financeiro
9. **Contas** - Gestão de contas a pagar e receber
10. **Relatórios** - Central de relatórios com filtros avançados

### Administração
11. **Funcionários** - Cadastro e gestão da equipe
12. **Gerenciar Usuários** - Controle de acesso e permissões
13. **Auditoria** - Log de ações do sistema
14. **Histórico de Versões** - Timeline de releases
15. **Configurações** - Dados da empresa e preferências

### Perfil
16. **Meu Perfil** - Configurações do usuário

### Autenticação
17. **Login** - Tela de autenticação

## 🎯 Características Principais

### Navegação
- **Sidebar fixa** com menu organizado por seções
- **Header fixo** com breadcrumb, busca global (Ctrl+K), notificações e perfil
- **Navegação SPA** entre telas sem recarregar a página

### Design System
- **Cores profissionais** com paleta IBM Blue
- **Tipografia moderna** com Inter e JetBrains Mono
- **Componentes consistentes** em todas as telas
- **Dark mode** suportado nativamente

### Responsividade
- Layout adaptável para diferentes tamanhos de tela
- Grid system flexível
- Sidebar colapsável em dispositivos móveis

### Acessibilidade
- Cores com contraste WCAG AA
- Estados de hover, focus e loading bem definidos
- Estrutura semântica HTML

## 🔧 Personalização

### Alterar Cores
Edite as variáveis CSS em `css/styles.css`:
```css
:root {
  --color-primary: #0F62FE;
  --color-primary-dark: #0043CE;
  /* ... */
}
```

### Modificar Telas
Cada tela é um template em `js/app.js` dentro do objeto `screens`. Para modificar uma tela, edite o HTML correspondente.

### Adicionar Novas Telas
1. Adicione o HTML no objeto `screens` em `js/app.js`
2. Adicione o item de navegação em `index.html`
3. Adicione o título no objeto `screenTitles` em `js/app.js`

## 📦 Próximos Passos para Implementação PySide6

Este mockup HTML/CSS serve como base para implementação em PySide6 (Qt6). Para converter:

1. **Estrutura**: Use QWidget para containers, QLayout para grids
2. **Estilos**: Converta CSS para QSS (Qt Style Sheets)
3. **Componentes**: Mapeie elementos HTML para widgets Qt:
   - `<button>` → QPushButton
   - `<input>` → QLineEdit/QComboBox
   - `<table>` → QTableWidget
   - Cards → QFrame com estilos
4. **Navegação**: Use QStackedWidget para alternar telas
5. **Ícones**: Converta SVG para recursos Qt ou use QIcon

## 📝 Notas Técnicas

- O mockup usa JavaScript vanilla para navegação SPA
- Ícones são SVG inline para simplicidade
- Gráficos são placeholders (devem ser implementados com biblioteca de charts)
- Formulários são visuais apenas (sem validação backend)
- Dados são mockados estáticos

## 🤝 Suporte

Para dúvidas ou sugestões sobre o redesign, consulte o documento de brief original ou entre em contato com a equipe de design.

## 📄 Licença

Este mockup é propriedade da CW Transportadora e faz parte do projeto de redesign do sistema de gestão.

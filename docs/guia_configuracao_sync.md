# Guia de Configuração de Sincronização - CW Transportadora

## Problema
O sistema não está sincronizando entre PCs porque a nuvem (Supabase) não está configurada.

## Solução - Passo a Passo

### 1. Criar conta no Supabase (GRATUITO)
1. Acesse: https://supabase.com
2. Clique em "Start your project"
3. Faça login com GitHub ou Google
4. Clique em "New Project"
5. Preencha:
   - **Name**: cw-transportadora
   - **Database Password**: (crie uma senha segura e ANOTE)
   - **Region**: South America (São Paulo)
6. Clique em "Create new project"
7. Aguarde cerca de 2 minutos para o projeto ser criado

### 2. Obter URL de Conexão
1. No painel do Supabase, clique em **Settings** (ícone de engrenagem)
2. Clique em **Database**
3. Role até encontrar **Connection string**
4. Clique em **URI** e copie a string
5. A string tem este formato:
   ```
   postgresql://postgres:[SUA_SENHA]@db.[PROJETO_ID].supabase.co:5432/postgres
   ```

### 3. Configurar no PC da Empresa
1. No projeto, abra o arquivo `.env.example`
2. Copie o conteúdo e crie um arquivo chamado `.env` (sem o .example)
3. Cole a URL do Supabase na linha `SUPABASE_URL=`
4. O arquivo `.env` deve ficar assim:
   ```
   SUPABASE_URL=postgresql://postgres:[SUA_SENHA]@db.[PROJETO_ID].supabase.co:5432/postgres?sslmode=require
   
   EMPRESA=CW TRANSPORTADORA
   CNPJ=
   TELEFONE=
   EMAIL=
   CIDADE=Cascavel
   UF=PR
   META_LUCRO=10000
   IMPOSTO_PERCENTUAL=3
   ALERTA_REVISAO=8000
   REVISAO_OBRIGATORIA=10000
   PASTA_RELATORIOS=relatorios_gerados
   INTERVALO_SYNC_SEGUNDOS=60
   ```
5. **IMPORTANTE**: O arquivo `.env` NÃO deve ser commitado no Git (já está no .gitignore)

### 4. Configurar no PC de Casa
1. Faça o mesmo processo: crie o arquivo `.env` com a MESMA URL do Supabase
2. A URL deve ser IDÊNTICA nos dois PCs

### 5. Primeira Sincronização
1. No PC da empresa, abra o sistema
2. O sistema irá automaticamente:
   - Criar as tabelas no Supabase
   - Enviar todos os dados locais para a nuvem
3. No PC de casa, abra o sistema
4. O sistema irá automaticamente:
   - Baixar todos os dados da nuvem
   - Sincronizar com o banco local

### 6. Como Funciona a Sincronização Automática
- O sistema sincroniza automaticamente a cada 60 segundos (configurável)
- Quando você adiciona/edita/deleta dados, eles são marcados para sync
- O sistema envia as mudanças para o Supabase
- O outro PC baixa as mudanças automaticamente
- Funciona mesmo offline (mudanças ficam pendentes e sincronizam quando voltar online)

### 7. Verificar Status da Sincronização
No sistema, você pode ver o status de sincronização na interface (se houver indicador).

## Troubleshooting

### Erro: "Nuvem desabilitada"
- Verifique se o arquivo `.env` existe
- Verifique se a URL do Supabase está preenchida
- Verifique se a URL está correta

### Erro de conexão
- Verifique sua internet
- Verifique se a senha do Supabase está correta
- Verifique se o projeto Supabase está ativo

### Dados não aparecendo no outro PC
- Aguarde o intervalo de sincronização (60 segundos)
- Verifique se ambos os PCs estão usando a MESMA URL do Supabase
- Reinicie o sistema em ambos os PCs

## Segurança
- NUNCA compartilhe seu arquivo `.env`
- NUNCA commitar o arquivo `.env` no Git
- Use uma senha forte no Supabase
- Mantenha seu projeto Supabase privado

## Custo
- Supabase tem plano GRATUITO com:
  - 500MB de banco de dados
  - 1GB de transferência/mês
  - Suficiente para uso pequeno/médio
- Se precisar mais, o plano Pro é barato (~$25/mês)

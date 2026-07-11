# Guia de Configuração e Uso - Auto-Update via GitHub

## Visão Geral

O módulo de Auto-Update do CW Transportadora utiliza o GitHub como CDN (Content Delivery Network) para distribuição automática de atualizações. O sistema suporta dois fluxos principais:

- **Fluxo Admin**: Automatiza o envio de novas versões para o repositório GitHub
- **Fluxo Cliente**: Verifica automaticamente novas versões e baixa via HTTPS

## Arquitetura

### Componentes

1. **GitHubReleaseService** (`services/github_release_service.py`)
   - Gerencia criação de releases no GitHub
   - Faz upload de instaladores
   - Atualiza automaticamente o `release.json`
   - Suporta autenticação via Personal Access Token

2. **GitHubUpdateService** (`services/github_update_service.py`)
   - Verifica atualizações via API do GitHub
   - Baixa instaladores via HTTPS
   - Valida integridade SHA-256
   - Implementa backup pré-instalação e rollback

3. **deploy_github.py**
   - Script de deploy automatizado para Admin
   - Atualiza versão, build, commit/push e release

4. **Configurações** (`config/settings.py`)
   - `github_repo_owner`: Proprietário do repositório
   - `github_repo_name`: Nome do repositório
   - `github_token`: Personal Access Token
   - `github_use_cdn`: Habilita uso do GitHub como CDN
   - `github_release_branch`: Branch para releases

## Configuração Inicial

### 1. Configurar Repositório GitHub

Crie um repositório no GitHub para armazenar as releases:
- Pode ser público ou privado
- Recomendado: privado para maior segurança

### 2. Gerar Personal Access Token (PAT)

Para repositórios privados ou para maior segurança:

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Configure as permissões:
   - `repo`: Full control of private repositories
   - `repo:status`: Access commit status
4. Copie o token gerado (só aparece uma vez!)

### 3. Configurar o Sistema

Edite o arquivo `configuracoes.json` ou use a tela de Configurações:

```json
{
  "github_repo_owner": "seu-usuario",
  "github_repo_name": "cw-transportadora",
  "github_token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "github_use_cdn": true,
  "github_release_branch": "main"
}
```

**Parâmetros:**
- `github_repo_owner`: Seu usuário GitHub
- `github_repo_name`: Nome do repositório
- `github_token`: Token gerado (opcional para repositórios públicos)
- `github_use_cdn`: `true` para usar GitHub como CDN
- `github_release_branch`: Branch principal (default: `main`)

## Fluxo Admin - Publicar Nova Versão

### Método 1: Script Automatizado (Recomendado)

Use o script `deploy_github.py` para automatizar todo o processo:

```bash
# Deploy completo (patch)
python deploy_github.py

# Deploy com incremento minor
python deploy_github.py minor

# Deploy com incremento major
python deploy_github.py major

# Apenas atualizar versão (sem build)
python deploy_github.py --no-build

# Deploy sem commit/push (para testes)
python deploy_github.py --skip-git
```

**O que o script faz:**
1. Atualiza versão no `versao.json`
2. Faz commit e push para o GitHub
3. Gera executável com PyInstaller
4. Gera instalador com Inno Setup
5. Cria release no GitHub
6. Faz upload do instalador
7. Atualiza `release.json` no repositório

### Método 2: Manual

Se preferir fazer manualmente:

1. **Atualizar versão:**
   ```bash
   python release.py minor
   ```

2. **Commit e push:**
   ```bash
   git add versao.json
   git commit -m "Release v1.1.0"
   git push
   ```

3. **Publicar no GitHub:**
   ```python
   from services.github_release_service import github_release_service, GitHubChannel
   from pathlib import Path

   success, release_info, error = github_release_service.publish_release(
       installer_path=Path("release/CW_Transportadora_v1.1.0_Setup.exe"),
       version="1.1.0",
       release_notes="Correções e melhorias",
       channel=GitHubChannel.STABLE
   )
   ```

## Fluxo Cliente - Verificar e Instalar Atualizações

### Verificação Automática

O sistema verifica automaticamente atualizações ao iniciar (após 3 segundos):

- Se `github_use_cdn = true` e GitHub configurado: usa `GitHubUpdateService`
- Caso contrário: usa `UpdateService` original (servidor próprio)

### Verificação Manual

Para verificar manualmente:

```python
from services.github_update_service import github_update_service, GitHubChannel

# Configurar canal
github_update_service.set_channel(GitHubChannel.STABLE)

# Verificar atualizações
resultado = github_update_service.check_for_updates()

if resultado["has_update"]:
    print(f"Nova versão: {resultado['latest_version']}")
    print(f"Download URL: {resultado['download_url']}")
    print(f"Notas: {resultado['release_notes']}")
```

### Download e Instalação

```python
# Download com progresso
def progress_callback(downloaded, total, speed, eta):
    print(f"Progresso: {downloaded}/{total} bytes ({speed/1024/1024:.2f} MB/s)")

success, file_path = github_update_service.download_update(
    download_url=resultado["download_url"],
    expected_sha256=resultado["sha256"],
    progress_callback=progress_callback
)

if success:
    # Instalar
    success, msg = github_update_service.install_update(file_path)
    if success:
        print("Instalação iniciada")
```

## Canais de Atualização

O sistema suporta três canais:

- **STABLE**: Versões estáveis (default)
- **BETA**: Versões em teste
- **DEV**: Versões de desenvolvimento

### Configurar Canal

```python
from services.github_release_service import GitHubChannel
from services.github_update_service import GitHubChannel

# Para publicar
github_release_service.publish_release(
    ...,
    channel=GitHubChannel.BETA
)

# Para verificar
github_update_service.set_channel(GitHubChannel.BETA)
```

## Segurança

### Autenticação

- **Repositórios Privados**: Token obrigatório
- **Repositórios Públicos**: Token opcional (recomendado para rate limits)

### Validação de Integridade

O sistema valida automaticamente:
- SHA-256 do arquivo baixado
- Tamanho do arquivo
- Corrupção durante download

### Backup e Rollback

Antes de instalar:
- Backup do banco de dados
- Backup das configurações
- Backup do `versao.json`

Em caso de falha:
- Rollback automático para backup
- Sistema permanece funcional

## Resiliência

### Tratamento de Falhas

1. **Sem Internet:**
   - Sistema continua funcionando offline
   - Tenta novamente na próxima verificação

2. **Download Corrompido:**
   - Validação SHA-256 detecta
   - Arquivo é removido
   - Nova tentativa na próxima verificação

3. **Falha na Instalação:**
   - Rollback automático
   - Sistema restaura estado anterior

4. **Rate Limits do GitHub:**
   - Implementado retry com delay
   - Token aumenta limites (5000 req/hora)

## Estrutura de Arquivos

```
CW_TRANSPORTADORA atualizado/
├── services/
│   ├── github_release_service.py    # Serviço de publicação
│   ├── github_update_service.py    # Serviço de atualização
│   └── release_service.py           # Serviço original (servidor próprio)
├── config/
│   └── settings.py                  # Configurações do GitHub
├── deploy_github.py                 # Script de deploy
├── release.py                       # Script de build
├── release.json                     # Metadados da versão (gerado)
└── versao.json                      # Versão atual
```

## release.json

Arquivo gerado automaticamente com metadados da versão:

```json
{
  "versao": "1.1.0",
  "nome": "CW Transportadora",
  "data": "11/07/2026",
  "canal": "stable",
  "installer_filename": "CW_Transportadora_v1.1.0_Setup.exe",
  "installer_size": 52428800,
  "sha256": "a1b2c3d4e5f6...",
  "release_notes": "Correções e melhorias",
  "published_by": "Deploy Automatizado",
  "github_tag": "v1.1.0",
  "github_release_url": "https://github.com/usuario/repo/releases/tag/v1.1.0",
  "github_download_url": "https://github.com/usuario/repo/releases/download/v1.1.0/CW_Transportadora_v1.1.0_Setup.exe",
  "published_at": "2026-07-11T12:00:00"
}
```

## Troubleshooting

### Erro: "Configuração do GitHub incompleta"

**Solução:** Configure `github_repo_owner` e `github_repo_name` no `configuracoes.json`.

### Erro: "Token do GitHub não configurado"

**Solução:** Configure `github_token` para repositórios privados ou para evitar rate limits.

### Erro: "release.json não encontrado"

**Solução:** Execute o deploy inicial com `deploy_github.py` para criar o primeiro release.

### Download lento ou falhando

**Solução:**
- Verifique conexão com internet
- Configure token para evitar rate limits
- Aumente `update_timeout` no `configuracoes.json`

### SHA-256 mismatch

**Solução:** O arquivo foi corrompido durante download. O sistema fará nova tentativa automaticamente.

## Boas Práticas

1. **Sempre use canais:**
   - Use STABLE para produção
   - Use BETA para testes internos
   - Use DEV para desenvolvimento

2. **Teste antes de publicar:**
   - Use `--skip-git` para testar localmente
   - Valide o instalador manualmente
   - Verifique notas de release

3. **Mantenha token seguro:**
   - Nunca commit o token
   - Use variáveis de ambiente em produção
   - Revoke tokens não utilizados

4. **Monitore rate limits:**
   - Use token para aumentar limites
   - Implemente cache se necessário
   - Evite verificações muito frequentes

5. **Documente releases:**
   - Escreva notas de release claras
   - Inclua breaking changes
   - Mencione novas features

## Exemplo Completo

### Primeiro Deploy

```bash
# 1. Configurar GitHub
# Editar configuracoes.json com suas credenciais

# 2. Deploy inicial
python deploy_github.py patch

# 3. Verificar no GitHub
# Acesse: https://github.com/seu-usuario/cw-transportadora/releases
```

### Atualização de Cliente

```bash
# 1. Cliente inicia o sistema
# Verificação automática após 3 segundos

# 2. Se houver atualização:
# - Dialogo aparece
# - Usuário aceita
# - Download inicia
# - Instalação é executada
# - Sistema reinicia
```

## Suporte

Para problemas ou dúvidas:
- Verifique os logs em `logs/`
- Consulte o troubleshooting acima
- Revise a configuração do GitHub

# Guia de Configuração - Sistema de Atualizações HTTP/HTTPS

**CW Transportadora**  
**Data:** 11/07/2026  
**Versão:** 1.0

---

## 1. Visão Geral

O sistema de atualizações do CW Transportadora agora utiliza **HTTP/HTTPS** como método principal de distribuição de versões. Isso permite:

- Publicar atualizações de qualquer lugar (casa, empresa, etc.)
- Distribuir para qualquer computador com acesso à internet
- Funcionar tanto em rede local quanto pela internet
- Não depender de pastas compartilhadas do Windows (SMB)

---

## 2. Arquitetura do Sistema

### 2.1 Fluxo de Publicação

```
Computador do Desenvolvedor (Casa)
    ↓
Gera instalador com release.py
    ↓
Publica via HTTP/HTTPS para servidor
    ↓
Servidor HTTP armazena:
    - /stable/version.json
    - /stable/CW_Transportadora_vX.X.X_Setup.exe
    - /beta/version.json
    - /beta/CW_Transportadora_vX.X.X_Setup.exe
    - /dev/version.json
    - /dev/CW_Transportadora_vX.X.X_Setup.exe
```

### 2.2 Fluxo de Atualização

```
Computador da Empresa
    ↓
Verifica version.json no servidor HTTP
    ↓
Compara versão local com versão do servidor
    ↓
Se nova versão disponível:
    ↓
Baixa instalador via HTTP
    ↓
Valida SHA-256
    ↓
Cria backup
    ↓
Instala atualização
```

---

## 3. Configuração do Servidor HTTP

### 3.1 Opção 1: Servidor Web Existente (Recomendado)

Se você já tem um servidor web (Apache, Nginx, IIS), pode usar:

**Estrutura de diretórios:**
```
/var/www/atualizacoes-cw/  (ou C:\inetpub\wwwroot\atualizacoes-cw\)
├── stable/
│   ├── version.json
│   └── CW_Transportadora_vX.X.X_Setup.exe
├── beta/
│   ├── version.json
│   └── CW_Transportadora_vX.X_X_Setup.exe
└── dev/
    ├── version.json
    └── CW_Transportadora_vX.X_X_Setup.exe
```

**Configuração do servidor:**
- Permitir upload de arquivos (POST)
- Permitir download de arquivos (GET)
- Configurar autenticação básica (opcional, mas recomendado)
- Configurar HTTPS (recomendado para segurança)

### 3.2 Opção 2: Servidor Simples com Python

Para testes ou uso interno, pode usar um servidor simples:

```bash
# No diretório onde deseja armazenar as atualizações
cd C:\Atualizacoes\CW_Transportadora

# Criar estrutura de diretórios
mkdir stable
mkdir beta
mkdir dev

# Iniciar servidor HTTP simples (porta 8000)
python -m http.server 8000

# Ou com upload habilitado (requer script adicional)
```

**Nota:** O servidor simples do Python não suporta upload nativamente. Para produção, use um servidor web completo.

### 3.3 Opção 3: Servidor na Nuvem

Você pode usar serviços como:
- **AWS S3** + CloudFront
- **Google Cloud Storage**
- **Azure Blob Storage**
- **DigitalOcean Spaces**
- **Outros serviços de armazenamento de arquivos**

Esses serviços geralmente fornecem:
- API HTTP para upload/download
- Autenticação via API keys
- HTTPS automático
- Alta disponibilidade
- CDN global

---

## 4. Configuração do Cliente

### 4.1 Configurar no `configuracoes.json`

```json
{
    "update_server_type": "http",
    "update_server_path": "https://seuservidor.com/atualizacoes-cw",
    "update_server_username": "usuario_http",
    "update_server_password": "senha_segura",
    "update_channel": "stable",
    "enable_auto_update": true,
    "update_url": "",
    "update_timeout": 30
}
```

**Explicação dos campos:**

- `update_server_type`: `"http"` ou `"https"` (recomendado)
- `update_server_path`: URL base do servidor (sem barra no final)
  - Ex: `https://updates.suaempresa.com/cw-transportadora`
  - Ex: `http://192.168.1.100:8000/atualizacoes`
- `update_server_username`: Usuário para autenticação básica HTTP (opcional)
- `update_server_password`: Senha para autenticação básica HTTP (opcional)
- `update_channel`: Canal de atualização (`"stable"`, `"beta"`, `"dev"`)
- `enable_auto_update`: Habilita verificação automática
- `update_url`: Deixe vazio para usar servidor próprio
- `update_timeout`: Timeout em segundos para requisições

### 4.2 Configurar Autenticação Básica (Opcional)

Para proteger o servidor de atualizações, configure autenticação básica HTTP:

**Apache (.htaccess):**
```apache
AuthType Basic
AuthName "Atualizacoes CW Transportadora"
AuthUserFile /path/to/.htpasswd
Require valid-user
```

**Nginx:**
```nginx
auth_basic "Atualizacoes CW Transportadora";
auth_basic_user_file /path/to/.htpasswd;
```

**IIS:**
- Configurar "Basic Authentication" no diretório virtual

**Gerar arquivo de senhas (.htpasswd):**
```bash
htpasswd -c /path/to/.htpasswd usuario_http
```

---

## 5. Processo de Publicação

### 5.1 Passo 1: Gerar Instalador

No computador de desenvolvimento:

```bash
cd "c:\Users\bruno\OneDrive\Desktop\atualizaçao sistema\CW_TRANSPORTADORA atualizado"
python release.py
```

Isso gera o instalador em `dist\CW_Transportadora_vX.X.X_Setup.exe`

### 5.2 Passo 2: Configurar Servidor

No `configuracoes.json` do computador de desenvolvimento:

```json
{
    "update_server_type": "https",
    "update_server_path": "https://seuservidor.com/atualizacoes-cw",
    "update_server_username": "usuario_http",
    "update_server_password": "senha_segura"
}
```

### 5.3 Passo 3: Publicar Versão

1. Abra o CW Transportadora
2. Faça login como usuário **Mestre**
3. Clique em **📤 Publicar Versão** no menu lateral
4. Selecione o instalador gerado pelo `release.py`
5. Edite as release notes
6. Selecione o canal (stable, beta, dev)
7. Clique em **Publicar**

O sistema irá:
- Calcular SHA-256 do arquivo
- Fazer upload do instalador para o servidor
- Fazer upload do version.json
- Validar o processo
- Registrar na auditoria
- Exibir resumo da publicação

### 5.4 Estrutura no Servidor

Após a publicação, o servidor terá:

```
https://seuservidor.com/atualizacoes-cw/
├── stable/
│   ├── version.json
│   └── CW_Transportadora_v6.1.0_Setup.exe
├── beta/
│   ├── version.json
│   └── CW_Transportadora_v6.2.0_Setup.exe
└── dev/
    ├── version.json
    └── CW_Transportadora_v6.3.0_Setup.exe
```

---

## 6. Configuração nos Computadores da Empresa

### 6.1 Passo 1: Configurar URL do Servidor

No `configuracoes.json` de cada computador:

```json
{
    "update_server_type": "https",
    "update_server_path": "https://seuservidor.com/atualizacoes-cw",
    "update_server_username": "usuario_http",
    "update_server_password": "senha_segura",
    "update_channel": "stable",
    "enable_auto_update": true
}
```

### 6.2 Passo 2: Verificar Conectividade

O sistema verificará automaticamente:
- Ao iniciar o aplicativo
- A cada intervalo configurado (padrão: verificação manual)

Para verificar manualmente:
1. Abra o CW Transportadora
2. Clique em **⚙️ Configurações**
3. Vá para a seção de atualizações
4. Clique em **Verificar Atualizações**

---

## 7. Segurança

### 7.1 Boas Práticas

- **Use HTTPS sempre que possível** para criptografar o tráfego
- **Configure autenticação básica** para proteger o servidor
- **Use senhas fortes** para autenticação HTTP
- **Valide certificados SSL** (já implementado no sistema)
- **Mantenha o servidor atualizado** com patches de segurança
- **Use firewall** para restringir acesso ao servidor
- **Monitore logs** do servidor para detectar acessos suspeitos

### 7.2 Validação de Integridade

O sistema implementa:
- **SHA-256** para validar integridade do instalador
- **Comparação de hash** antes e após download
- **Rejeição de arquivos corrompidos**
- **Backup automático** antes da instalação

### 7.3 Autenticação

- **Autenticação básica HTTP** (username/password)
- **Credenciais armazenadas** no `configuracoes.json`
- **Transmissão segura** via HTTPS

---

## 8. Solução de Problemas

### 8.1 Erro de Conexão

**Problema:** Não consegue conectar ao servidor

**Soluções:**
- Verifique se a URL está correta
- Verifique se o servidor está online
- Verifique se há firewall bloqueando
- Teste a URL no navegador
- Verifique se o certificado SSL é válido

### 8.2 Erro de Autenticação

**Problema:** Erro 401 Unauthorized

**Soluções:**
- Verifique usuário e senha
- Verifique se o servidor requer autenticação
- Verifique se o usuário tem permissão de acesso

### 8.3 Erro de Upload

**Problema:** Falha ao fazer upload

**Soluções:**
- Verifique se o servidor aceita método POST
- Verifique se há espaço em disco
- Verifique permissões de escrita no diretório
- Aumente o timeout se o arquivo for grande

### 8.4 Erro de Download

**Problema:** Falha ao baixar atualização

**Soluções:**
- Verifique conectividade com a internet
- Verifique se a URL do instalador está correta
- Verifique se o arquivo existe no servidor
- Aumente o timeout se a conexão for lenta

### 8.5 Erro de SSL

**Problema:** Erro de certificado SSL

**Soluções:**
- Verifique se o certificado é válido
- Verifique se a data do sistema está correta
- Para desenvolvimento, pode desabilitar verificação (não recomendado para produção)

---

## 9. Exemplo de Configuração Completa

### 9.1 Servidor: Nginx com HTTPS

**Configuração Nginx:**
```nginx
server {
    listen 443 ssl;
    server_name updates.suaempresa.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /atualizacoes-cw/ {
        alias /var/www/atualizacoes-cw/;
        
        # Autenticação básica
        auth_basic "Atualizacoes CW";
        auth_basic_user_file /etc/nginx/.htpasswd;

        # Permitir upload (POST)
        dav_methods PUT DELETE;
        dav_access user:rw;

        # Permitir download
        autoindex off;
    }
}
```

### 9.2 Cliente: configuracoes.json

```json
{
    "empresa": "CW TRANSPORTADORA",
    "tema": "Premium Escuro",
    "cor_tema": "Vermelho",
    "update_server_type": "https",
    "update_server_path": "https://updates.suaempresa.com/atualizacoes-cw",
    "update_server_username": "cw_updates",
    "update_server_password": "S3nh@S3gur@2026!",
    "update_channel": "stable",
    "enable_auto_update": true,
    "update_url": "",
    "update_timeout": 30
}
```

---

## 10. Alternativas ao Servidor Próprio

Se você não quer configurar um servidor HTTP, pode usar:

### 10.1 GitHub Releases (Gratuito)

O sistema já suporta GitHub como alternativa:

```json
{
    "update_server_type": "local",
    "update_server_path": "",
    "update_url": "https://api.github.com/repos/seu-usuario/cw-transportadora/releases/latest"
}
```

### 10.2 Serviços de Hospedagem de Arquivos

- **Dropbox** (com link direto)
- **Google Drive** (com link direto)
- **OneDrive** (com link direto)
- **AWS S3** (com CloudFront)

---

## 11. Resumo

O sistema de atualizações HTTP/HTTPS oferece:

✅ **Flexibilidade:** Publice de qualquer lugar  
✅ **Acessibilidade:** Computadores em qualquer lugar podem atualizar  
✅ **Segurança:** HTTPS + autenticação + validação SHA-256  
✅ **Simplicidade:** Configuração mínima no cliente  
✅ **Escalabilidade:** Funciona com poucos ou muitos computadores  
✅ **Independência:** Não depende de GitHub ou serviços externos  

Para começar:
1. Configure um servidor HTTP (ou use um existente)
2. Configure a URL no `configuracoes.json`
3. Publique a primeira versão usando "Publicar Versão"
4. Configure os computadores da empresa com a mesma URL
5. Pronto! O sistema funcionará automaticamente

---

**Fim do Guia**

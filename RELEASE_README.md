# Sistema de Release Automática - CW Transportadora

Sistema completo de automação de releases que simplifica todo o processo de distribuição do software CW Transportadora.

## Funcionalidades

✅ **Atualização automática de versão** - Incrementa major, minor ou patch automaticamente  
✅ **Geração de executável** - PyInstaller com configuração otimizada  
✅ **Geração de instalador** - Inno Setup com setup profissional  
✅ **Cálculo de SHA-256** - Verificação de integridade do instalador  
✅ **Atualização de arquivos de versão** - Atualiza `versao.json` automaticamente  
✅ **Upload para GitHub** - Opcional, via GitHub CLI  
✅ **Limpeza automática** - Remove builds anteriores  

## Pré-requisitos

### Obrigatórios
- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- Inno Setup 6 (Windows): https://jrsoftware.org/isdl.php

### Opcionais
- GitHub CLI (para upload automático): https://cli.github.com/

## Instalação

1. **Instalar PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Instalar Inno Setup:**
   - Baixe em: https://jrsoftware.org/isdl.php
   - Instale com as opções padrão

3. **(Opcional) Instalar GitHub CLI:**
   - Baixe em: https://cli.github.com/
   - Faça login: `gh auth login`

## Uso Básico

### Release Patch (incremento de patch)
```bash
python release.py
```
Ou:
```bash
python release.py patch
```

### Release Minor (nova funcionalidade)
```bash
python release.py minor
```

### Release Major (mudança quebrando compatibilidade)
```bash
python release.py major
```

## Opções Avançadas

### Apenas atualizar versão (sem build)
```bash
python release.py patch --no-build
```

### Apenas executável (sem instalador)
```bash
python release.py patch --no-installer
```

### Build e upload para GitHub
```bash
python release.py minor --upload
```

### Combinação de opções
```bash
python release.py major --no-installer --upload
```

## Estrutura de Arquivos Gerados

```
CW_TRANSPORTADORA atualizado/
├── release/
│   ├── CW_Transportadora_v6.0.1_Setup.exe    # Instalador final
│   ├── release_v6.0.1.json                   # Metadados do release
│   └── release_notes_v6.0.1.txt              # Notas de release
├── dist/
│   └── CW_Transportadora.exe                 # Executável standalone
├── build/
│   └── (arquivos temporários do PyInstaller)
├── build.spec                                 # Arquivo .spec gerado
├── installer.iss                              # Arquivo .iss gerado
└── versao.json                                # Versão atualizada
```

## Arquivos de Versão

### versao.json
```json
{
    "versao": "6.0.1",
    "nome": "CW Transportadora",
    "data": "10/07/2026"
}
```

### release_vX.X.X.json
```json
{
    "versao": "6.0.1",
    "data": "10/07/2026",
    "nome": "CW Transportadora",
    "installer_path": "C:\\...\\CW_Transportadora_v6.0.1_Setup.exe",
    "installer_size_mb": "45.23",
    "sha256": "a1b2c3d4...",
    "release_notes": "..."
}
```

## Integração com Sistema de Atualização

O sistema de release é compatível com o `update_service.py` do CW Transportadora:

1. **Versão é atualizada automaticamente** no `versao.json`
2. **SHA-256 é calculado** e incluído no release info
3. **Instalador é gerado** com nome versionado
4. **Upload para GitHub** cria release com tag versionada

O sistema de atualização verifica:
- Tag do release no GitHub (ex: `v6.0.1`)
- Asset `.exe` do release
- SHA-256 para verificação de integridade

## Troubleshooting

### Erro: PyInstaller não encontrado
```bash
pip install pyinstaller
```

### Erro: Inno Setup não encontrado
- Verifique se Inno Setup está instalado em:
  - `C:\Program Files (x86)\Inno Setup 6\`
  - `C:\Program Files\Inno Setup 6\`
- Se estiver em outro local, edite o caminho em `release.py`

### Erro: GitHub CLI não encontrado
```bash
# Baixe e instale em: https://cli.github.com/
gh auth login
```

### Erro: Permissão negada
Execute como administrador no Windows.

### Limpar builds anteriores manualmente
```bash
rmdir /s /q build dist release
```

## Boas Práticas

1. **Sempre teste antes do release:**
   ```bash
   python -m pytest testes/
   ```

2. **Use versionamento semântico:**
   - **MAJOR**: Mudanças incompatíveis
   - **MINOR**: Novas funcionalidades (compatível)
   - **PATCH**: Correções de bugs (compatível)

3. **Faça backup antes de major releases:**
   ```bash
   # Backup do banco e configurações
   ```

4. **Teste o instalador:**
   - Execute o instalador gerado
   - Verifique se o sistema funciona
   - Teste atualização de versão anterior

5. **Documente mudanças:**
   - Edite `release_notes_vX.X.X.txt` antes do upload
   - Inclua changelog detalhado

## Exemplo de Workflow Completo

```bash
# 1. Desenvolva e teste
python -m pytest testes/

# 2. Commit mudanças
git add .
git commit -m "Nova funcionalidade X"
git push

# 3. Faça release
python release.py minor --upload

# 4. Verifique no GitHub
# - Release criado com tag v6.1.0
# - Instalador uploadado
# - SHA-256 calculado
```

## Personalização

### Alterar configuração do PyInstaller
Edite o método `_generate_spec_file()` em `release.py`:
- Adicionar/remover arquivos de dados
- Configurar ícone
- Ajustar opções de compressão

### Alterar configuração do Inno Setup
Edite o método `_generate_iss_file()` em `release.py`:
- Mudar caminhos de instalação
- Adicionar atalhos
- Configurar páginas do wizard

### Alterar notas de release padrão
Edite o método `_generate_release_notes()` em `release.py`.

## Suporte

Para problemas ou sugestões:
- Verifique o troubleshooting acima
- Consulte logs em `logs/`
- Abra issue no repositório

## Licença

Este sistema de release é parte integrante do CW Transportadora.

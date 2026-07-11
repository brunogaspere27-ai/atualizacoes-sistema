---
name: Scaffolding do Gemma3 removido do CW Transportadora
description: Registro de que uma feature experimental de inferência local com Gemma3 foi removida por não ter uso real no sistema.
---

O repositório do CW Transportadora tinha arquivos (`models/gemma3_runner.py`,
`README_GEMMA3.md`, `requirements-gemma3.txt`, `config/gemma3.json`,
`scripts/setup_gemma3.ps1`) referentes a um experimento de inferência local
com o modelo Gemma3:12B. Foi confirmado (via grep) que nada no código da
aplicação principal (`main.py`, `telas/`, `services/`) importava ou referenciava
esses arquivos — era scaffolding solto, não uma feature integrada.

**Why:** removido como parte de uma limpeza de repositório pedida pelo
usuário; manter código morto/experimental sem uso real só adiciona ruído e
confunde sobre o que o sistema realmente faz.

**How to apply:** se o usuário mencionar Gemma3 ou pedir inferência local de
modelo no futuro, esse scaffolding não existe mais — teria que ser recriado do
zero.

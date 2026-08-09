"""
CW Transportadora - Entrypoint principal.

Este arquivo é um shim minimalista que delega para `main_pyside6.py`,
onde está a interface moderna em PySide6.

- Rodando `python main.py`         -> abre a interface NOVA (PySide6)
- Rodando `python main_pyside6.py` -> equivalente, mesma interface

A versão antiga em CustomTkinter foi preservada em `main_tkinter_legacy.py`
para consulta ou rollback pontual. Ela NÃO é mais usada em produção.

Para forçar a versão antiga (não recomendado):
    python main_tkinter_legacy.py
"""

from __future__ import annotations

import sys


class App:
    """Proxy compatível para a janela PySide6, carregado apenas ao instanciar.

    Mantém ``from main import App`` funcional para integrações antigas sem
    exigir a inicialização das bibliotecas visuais durante importações leves.
    """

    def __new__(cls, *args, **kwargs):
        from main_pyside6 import App as PySideApp
        return PySideApp(*args, **kwargs)


def _run_pyside6() -> None:
    """Importa e executa a aplicação PySide6 (importação tardia para não poluir o namespace)."""
    from main_pyside6 import main as _pyside_main

    _pyside_main()


if __name__ == "__main__":
    try:
        _run_pyside6()
    except ModuleNotFoundError as erro:
        # Guardrail: ambiente sem PySide6 instalado.
        sys.stderr.write(
            "\n[CW Transportadora] Não foi possível iniciar a interface PySide6.\n"
            f"Módulo ausente: {erro.name}\n\n"
            "Instale as dependências:\n"
            "    pip install -r requirements.txt\n\n"
            "Ou, temporariamente, use a versão legacy:\n"
            "    python main_tkinter_legacy.py\n"
        )
        sys.exit(1)

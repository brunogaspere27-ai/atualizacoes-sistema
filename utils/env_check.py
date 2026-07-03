"""
Verificação do arquivo .env ao iniciar o sistema.
"""
from __future__ import annotations
import os
from typing import Tuple


def verificar_configuracao_env() -> Tuple[bool, str]:
    from config.settings import settings
    url = os.getenv("SUPABASE_URL", "").strip()
    if url:
        return True, "Nuvem configurada. Sincronização ativada."
    env_path = settings.project_dir / ".env"
    if env_path.exists():
        return False, (
            "O arquivo '.env' existe, mas a variável SUPABASE_URL não está preenchida.\n\n"
            "Para ativar a sincronização entre PCs:\n"
            "  1. Abra o arquivo .env na pasta do sistema.\n"
            "  2. Preencha a linha:  SUPABASE_URL=<sua_url_do_supabase>\n"
            "  3. Reinicie o sistema.\n\n"
            "O sistema continuará funcionando em modo LOCAL até que isso seja feito."
        )
    return False, (
        "Arquivo '.env' não encontrado.\n\n"
        "Para ativar a sincronização entre PCs:\n"
        "  1. Copie o arquivo '.env.example' e renomeie para '.env'.\n"
        "  2. Preencha a linha:  SUPABASE_URL=<sua_url_do_supabase>\n"
        "  3. Reinicie o sistema.\n\n"
        "O sistema continuará funcionando em modo LOCAL até que isso seja feito.\n"
        "Execute 'configurar_env.py' para configurar automaticamente."
    )


def avisar_se_offline() -> bool:
    ok, mensagem = verificar_configuracao_env()
    if not ok:
        try:
            import tkinter as tk
            from tkinter import messagebox
            raiz_temp = tk.Tk()
            raiz_temp.withdraw()
            messagebox.showwarning("⚠️ Sincronização Desativada", mensagem, parent=raiz_temp)
            raiz_temp.destroy()
        except Exception:
            print(f"[AVISO] {mensagem}")
    return ok

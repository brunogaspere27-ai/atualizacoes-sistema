"""
Verificação de ambiente.
"""
import os


def verificar_configuracao_env():
    """Verifica se variáveis de ambiente estão configuradas."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        return False, "SUPABASE_URL e SUPABASE_KEY não configurados. Sincronização desativada."
    
    return True, "OK"
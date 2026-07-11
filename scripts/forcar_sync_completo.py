"""
Força a sincronização COMPLETA de todos os dados locais para o Supabase.
Execute em qualquer PC para garantir que nenhum dado fique faltando:
    python forcar_sync_completo.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
load_dotenv()

from config.settings import settings
from utils.sync import reparar_e_enfileirar_fila, sincronizar


def linha():
    print("=" * 60)


def main():
    if not os.getenv("SUPABASE_URL", "").strip():
        print()
        print("ERRO: SUPABASE_URL nao configurado!")
        print("Configure o arquivo .env antes de continuar.")
        print()
        input("ENTER para sair...")
        sys.exit(1)

    url = os.getenv("SUPABASE_URL", "")
    print()
    linha()
    print("  CW TRANSPORTADORA - Sincronizacao Completa para Nuvem")
    linha()
    print()
    print(f"  Banco local : {settings.db_path}")
    print(f"  Supabase    : {url[:45]}...")
    print()
    print("Fase 1 - Verificando e enfileirando dados locais...")
    print()

    adicionados = reparar_e_enfileirar_fila()

    print()
    if adicionados == 0:
        print("Todos os dados ja estavam na fila.")
    else:
        print(f"{adicionados} registros adicionados a fila de envio.")

    print()
    print("Fase 2 - Enviando para o Supabase e baixando novidades...")
    print("(pode levar alguns minutos)")
    print()

    try:
        r = sincronizar()
        print()
        linha()
        if r.get("offline"):
            print()
            print("SEM CONEXAO com o Supabase.")
            print(f"   {r.get('mensagem', '')}")
            print()
            print("   Verifique a internet e a URL no arquivo .env")
        elif r.get("status") == "ok":
            print()
            print("SINCRONIZACAO CONCLUIDA COM SUCESSO!")
            print()
            print(f"   Enviados  : {r.get('enviados', 0)} registros")
            print(f"   Baixados  : {r.get('baixados', 0)} registros")
            print(f"   Pendentes : {r.get('pendencias', 0)}")
            print()
            print("   Abra o sistema no outro PC - todos os dados estarao la.")
        elif r.get("status") == "partial":
            print()
            print(f"Parcial: {r.get('enviados',0)} enviados, {r.get('erros',0)} erros.")
            pend = r.get("pendencias", 0)
            if pend:
                print(f"   {pend} registros ainda pendentes. Rode novamente.")
        else:
            print()
            print(f"Erro: {r.get('mensagem', 'Sem detalhes')}")
        linha()
    except Exception as e:
        print(f"Erro ao sincronizar: {e}")
        print("Tente abrir o sistema normalmente.")

    print()
    input("ENTER para sair...")


if __name__ == "__main__":
    main()

"""Diagnostic script to verify theme is loaded correctly at runtime."""
from config.settings import settings
from telas.theme import setup_theme, criar_header

cores = setup_theme(settings)
tema = getattr(settings, "tema", "NOT SET")

print("=" * 60)
print("  THEME DIAGNOSTIC REPORT")
print("=" * 60)
print(f"\n  Active theme: {tema}")
print(f"\n  Key theme tokens:")
for key in ["font_family", "fundo", "header_bg", "header_tag",
            "header_title", "header_subtitle", "header",
            "texto", "texto_suave", "principal", "sidebar",
            "sidebar_card", "hover", "card_bg"]:
    val = cores.get(key, "MISSING")
    print(f"    {key:20s} = {val}")

print(f"\n  All keys ({len(cores)}): {sorted(cores.keys())}")

# Verify criar_header is callable
print(f"\n  criar_header callable: {callable(criar_header)}")
print(f"  criar_header module:   {criar_header.__module__}")

# Verify screen files have the imports
import importlib
screens = [
    "telas.contas", "telas.combustivel", "telas.manutencao",
    "telas.configuracoes", "telas.operacoes", "telas.notas",
    "telas.funcionarios", "telas.historico",
]
print(f"\n  Screen import check:")
for mod_name in screens:
    try:
        mod = importlib.import_module(mod_name)
        src = open(mod.__file__).read()
        has_setup = "setup_theme" in src
        has_criar = "criar_header" in src
        has_arial = '"Arial"' in src
        has_segoe = '"Segoe UI"' in src
        status = "OK" if (has_setup and has_criar and not has_arial) else "ISSUE"
        issues = []
        if not has_setup: issues.append("no setup_theme")
        if not has_criar: issues.append("no criar_header")
        if has_arial: issues.append(f'STILL HAS "Arial"')
        if has_segoe: issues.append(f'STILL HAS "Segoe UI"')
        detail = f" [{', '.join(issues)}]" if issues else ""
        print(f"    {mod_name:30s} {status}{detail}")
    except Exception as e:
        print(f"    {mod_name:30s} ERROR: {e}")

print("\n" + "=" * 60)

import customtkinter as ctk


def setup_theme(settings) -> dict:
    """Configure global theme and return a colors dict used by the UI."""
    tema = getattr(settings, "tema", "Vermelho CW")

    if tema in ("Premium Escuro", "Claro"):
        ctk.set_appearance_mode("dark" if tema == "Premium Escuro" else "light")
    else:
        ctk.set_appearance_mode("light")

    ctk.set_default_color_theme("blue")

    cores = settings.obter_cores_tema()

    # Cores aprimoradas para melhor visual
    cores.setdefault("card_bg", "#FFFFFF" if tema == "Claro" else "#1F2937")
    cores.setdefault("card_text", "#111827" if tema == "Claro" else "#FFFFFF")
    cores.setdefault("muted_border", "#E5E7EB" if tema == "Claro" else "#374151")
    cores.setdefault("surface", "#FFFFFF" if tema == "Claro" else "#111827")
    cores.setdefault("surface_alt", "#F8FAFC" if tema == "Claro" else "#1F2937")
    cores.setdefault("accent", cores.get("principal", "#DC2626"))
    
    # Cores adicionais para profissionalismo
    cores.setdefault("success", "#10B981")
    cores.setdefault("warning", "#F59E0B")
    cores.setdefault("error", "#EF4444")
    cores.setdefault("info", "#3B82F6")
    cores.setdefault("shadow", "rgba(0, 0, 0, 0.1)")
    cores.setdefault("text_muted", "#6B7280" if tema == "Claro" else "#9CA3AF")
    cores.setdefault("divider", "#E5E7EB" if tema == "Claro" else "#374151")

    return cores

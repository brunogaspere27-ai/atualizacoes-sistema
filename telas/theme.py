"""
Design system CW Transportadora v7 — dark-only, denso, com acentos por categoria.

Único modo suportado: escuro (Premium Escuro).
Cor de marca: vermelho CW (#EF4444). Acentos secundários usados nos KPIs e
ícones de menu: emerald, sky, amber, violet, cyan, rose.
"""

import customtkinter as ctk

# ── Tokens globais ───────────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI"
PADDING_X = 24
HEADER_RADIUS = 16
CARD_RADIUS = 14

# Paleta base (Tailwind slate + acentos escolhidos)
_TOKENS = {
    # Superfícies
    "bg":            "#0B1120",   # fundo da área de conteúdo
    "bg_alt":        "#0F172A",   # fundo alternativo (sidebar/rodapé)
    "surface":       "#111827",   # cards
    "surface_2":     "#182234",   # cards hover / campos
    "surface_3":     "#1F2A3B",   # divisores fortes
    "border":        "#1E293B",   # bordas suaves de card
    "border_strong": "#334155",

    # Texto
    "text":          "#F1F5F9",
    "text_muted":    "#94A3B8",
    "text_soft":     "#64748B",

    # Marca
    "brand":         "#EF4444",   # CW red
    "brand_hover":   "#DC2626",
    "brand_soft":    "#3B1D1D",   # fundo tinta para tags/badges vermelhos

    # Acentos por categoria (usados em KPI, menu icons)
    "emerald":       "#10B981",
    "emerald_soft": "#0F2A24",
    "sky":           "#38BDF8",
    "sky_soft":     "#0E2536",
    "amber":         "#F59E0B",
    "amber_soft":   "#2A1F0F",
    "violet":        "#A855F7",
    "violet_soft":  "#241533",
    "cyan":          "#06B6D4",
    "cyan_soft":    "#0B2A34",
    "rose":          "#F43F5E",
    "rose_soft":    "#2A121A",

    # Estados
    "success":       "#22C55E",
    "warning":       "#F59E0B",
    "error":         "#EF4444",
    "info":          "#3B82F6",
}


def setup_theme(settings) -> dict:
    """Aplica o tema escuro CW v7 e devolve o dict de cores.

    Ignora `settings.tema` — apenas escuro é suportado nesta versão.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    c = dict(_TOKENS)

    # Aliases de compatibilidade com o código antigo (main.py, telas/*).
    c["fundo"]          = c["bg"]
    c["sidebar"]        = c["bg_alt"]
    c["sidebar_card"]   = c["surface"]
    c["header"]         = c["surface"]
    c["header_bg"]      = c["surface"]
    c["header_tag"]     = c["brand"]
    c["header_title"]   = c["text"]
    c["header_subtitle"] = c["text_muted"]
    c["principal"]      = c["brand"]
    c["hover"]          = c["surface_2"]
    c["texto"]          = c["text"]
    c["texto_suave"]    = c["text_muted"]
    c["card_bg"]        = c["surface"]
    c["card_text"]      = c["text"]
    c["muted_border"]   = c["border"]
    c["surface_alt"]    = c["surface_2"]
    c["accent"]         = c["brand"]
    c["divider"]        = c["surface_3"]
    c["shadow"]         = "#000000"

    c["font_family"] = FONT_FAMILY
    return c


def criar_header(master, tag: str, titulo: str, subtitulo: str, cores: dict, **grid_kwargs):
    """Header enxuto usado por todas as telas. Compatível com a assinatura antiga."""
    ff = cores["font_family"]

    topo = ctk.CTkFrame(master, fg_color=cores["surface"], corner_radius=HEADER_RADIUS,
                        border_width=1, border_color=cores["border"])

    if grid_kwargs:
        topo.grid(**grid_kwargs)
    else:
        topo.pack(fill="x", padx=PADDING_X, pady=(18, 12))

    ctk.CTkLabel(topo, text=tag.upper(),
                 font=(ff, 11, "bold"), text_color=cores["brand"]
                 ).pack(anchor="w", padx=22, pady=(16, 0))

    ctk.CTkLabel(topo, text=titulo,
                 font=(ff, 26, "bold"), text_color=cores["text"]
                 ).pack(anchor="w", padx=22, pady=(2, 0))

    if subtitulo:
        ctk.CTkLabel(topo, text=subtitulo,
                     font=(ff, 12), text_color=cores["text_muted"]
                     ).pack(anchor="w", padx=22, pady=(0, 16))
    else:
        ctk.CTkFrame(topo, fg_color="transparent", height=14).pack()

    return topo

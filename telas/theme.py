import customtkinter as ctk

# ── Design tokens globais ────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI"
PADDING_X = 25
HEADER_RADIUS = 20


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

    # Background padrão para telas
    cores.setdefault("fundo", "#F4F6F8" if tema != "Premium Escuro" else "#111827")

    # Cores do header escuro padrão
    cores.setdefault("header_bg", cores.get("header", "#1F2937"))
    cores.setdefault("header_tag", "#93c5fd")
    cores.setdefault("header_title", cores.get("texto", "#FFFFFF"))
    cores.setdefault("header_subtitle", cores.get("texto_suave", "#cbd5e1"))

    # Tokens de fonte
    cores["font_family"] = FONT_FAMILY

    return cores


def criar_header(master, tag: str, titulo: str, subtitulo: str, cores: dict, **grid_kwargs):
    """
    Cria o header escuro padronizado usado em todas as telas.

    Args:
        master: Widget pai onde o header será inserido.
        tag: Texto pequeno superior (ex: "FINANCEIRO", "FROTA").
        titulo: Título principal do header.
        subtitulo: Descrição secundária.
        cores: Dict de cores retornado por ``setup_theme()``.
        **grid_kwargs: Parâmetros extras para .pack() ou .grid().

    Returns:
        O CTkFrame do header criado.
    """
    ff = cores["font_family"]

    topo = ctk.CTkFrame(master, fg_color=cores["header_bg"], corner_radius=HEADER_RADIUS)

    # Suporta tanto pack quanto grid via kwargs
    if grid_kwargs:
        topo.grid(**grid_kwargs)
    else:
        topo.pack(fill="x", padx=PADDING_X, pady=(20, 15))

    ctk.CTkLabel(
        topo,
        text=tag.upper(),
        font=(ff, 13, "bold"),
        text_color=cores["header_tag"],
    ).pack(anchor="w", padx=24, pady=(18, 0))

    ctk.CTkLabel(
        topo,
        text=titulo,
        font=(ff, 34, "bold"),
        text_color=cores["header_title"],
    ).pack(anchor="w", padx=24)

    if subtitulo:
        ctk.CTkLabel(
            topo,
            text=subtitulo,
            font=(ff, 14),
            text_color=cores["header_subtitle"],
        ).pack(anchor="w", padx=24, pady=(0, 18))
    else:
        # Padding inferior quando não há subtítulo
        ctk.CTkFrame(topo, fg_color="transparent", height=18).pack()

    return topo

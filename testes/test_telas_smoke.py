"""Testes de smoke para telas e utilitários de UI."""

import customtkinter as ctk
import pytest

from utils.loading_overlay import LoadingOverlay, show_loading


SCREENS = [
    ("telas.dashboard", "Dashboard"),
    ("telas.operacoes", "TelaOperacoes"),
    ("telas.notas", "TelaNotas"),
    ("telas.criar_viagem", "TelaCriarViagem"),
    ("telas.historico", "TelaHistorico"),
    ("telas.ranking_clientes", "TelaRankingClientes"),
    ("telas.combustivel", "TelaCombustivel"),
    ("telas.contas", "TelaContas"),
    ("telas.relatorios", "TelaRelatorios"),
    ("telas.manutencao", "TelaManutencao"),
    ("telas.funcionarios", "TelaFuncionarios"),
    ("telas.configuracoes", "TelaConfiguracoes"),
]


@pytest.fixture
def tk_root():
    try:
        root = ctk.CTk()
    except Exception:
        pytest.skip("Tkinter/Tcl não disponível neste ambiente")
    root.withdraw()
    frame = ctk.CTkFrame(root)
    frame.pack(fill="both", expand=True)
    yield frame
    root.destroy()


@pytest.mark.parametrize("module_name,class_name", SCREENS)
def test_tela_instancia_sem_erro(tk_root, module_name, class_name):
    module = __import__(module_name, fromlist=[class_name])
    screen_class = getattr(module, class_name)
    widget = screen_class(tk_root)
    widget.pack(fill="both", expand=True)
    tk_root.update()
    widget.destroy()


def test_loading_overlay_cria_e_destrói(tk_root):
    overlay = show_loading(tk_root, "Processando...")
    tk_root.update()
    overlay.set_message("Quase pronto...")
    overlay.destroy()


def test_loading_overlay_destroy_seguro_sem_spinner(tk_root):
    overlay = LoadingOverlay.__new__(LoadingOverlay)
    ctk.CTkFrame.__init__(overlay, tk_root, fg_color="#374151")
    overlay.spinner = None
    overlay.label = None
    overlay.destroy()

"""
Tela de Login do sistema CW Transportadora.

Interface moderna e profissional, compativel com o restante do sistema.
Features:
- Campos usuario e senha
- Botao mostrar/ocultar senha
- Checkbox 'Lembrar de mim'
- Feedback visual de erros
- Loading indicator durante autenticacao
"""

from __future__ import annotations

import threading
from typing import Callable, Optional

import customtkinter as ctk
from tkinter import messagebox

from config.settings import settings
from services.auth_service import (
    auth_service,
    ContaBloqueadaError,
    ContaInativaError,
    CredenciaisInvalidasError,
)
from services.auditoria_service import auditoria_service, ACAO_LOGIN, ACAO_LOGIN_FALHOU
from telas.theme import setup_theme
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaLogin(ctk.CTkFrame):
    """Tela de login embutida no container principal do App."""

    def __init__(self, master, on_login_sucesso: Callable):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])

        self._on_login_sucesso = on_login_sucesso
        self._senha_visivel = False
        self._autenticando = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._criar_interface()

        # Bind Enter para login (sera aplicado nos entries em _criar_interface)

    def _criar_interface(self) -> None:
        ff = self.cores["font_family"]
        cor_principal = self.cores.get("principal", "#DC2626")

        # Container centralizado
        container = ctk.CTkFrame(
            self,
            fg_color="white" if self.cores.get("fundo", "#F3F4F6") != "#111827" else "#1F2937",
            corner_radius=24,
            width=460,
            height=580,
        )
        container.grid(row=0, column=0)
        container.grid_propagate(False)

        # Logo / Titulo
        ctk.CTkLabel(
            container,
            text="CW",
            font=(ff, 48, "bold"),
            text_color=cor_principal,
        ).pack(pady=(40, 2))

        ctk.CTkLabel(
            container,
            text="CW TRANSPORTADORA",
            font=(ff, 16, "bold"),
            text_color=self.cores.get("texto", "#111827"),
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            container,
            text="Sistema de Gestao Logistica",
            font=(ff, 12),
            text_color=self.cores.get("texto_suave", "#6B7280"),
        ).pack(pady=(0, 30))

        # Campo Usuario
        frame_usuario = ctk.CTkFrame(container, fg_color="transparent")
        frame_usuario.pack(fill="x", padx=40, pady=(0, 12))

        ctk.CTkLabel(
            frame_usuario,
            text="Usuario",
            font=(ff, 12, "bold"),
            text_color=self.cores.get("texto_suave", "#6B7280"),
        ).pack(anchor="w", pady=(0, 4))

        self.entry_usuario = ctk.CTkEntry(
            frame_usuario,
            height=44,
            font=(ff, 14),
            placeholder_text="Digite seu usuario",
            border_color="#D1D5DB",
            fg_color="#F9FAFB",
            text_color="#111827",
        )
        self.entry_usuario.pack(fill="x")
        self.entry_usuario.bind("<Return>", lambda e: self._tentar_login())

        # Campo Senha
        frame_senha = ctk.CTkFrame(container, fg_color="transparent")
        frame_senha.pack(fill="x", padx=40, pady=(0, 6))

        ctk.CTkLabel(
            frame_senha,
            text="Senha",
            font=(ff, 12, "bold"),
            text_color=self.cores.get("texto_suave", "#6B7280"),
        ).pack(anchor="w", pady=(0, 4))

        frame_senha_input = ctk.CTkFrame(frame_senha, fg_color="transparent")
        frame_senha_input.pack(fill="x")

        self.entry_senha = ctk.CTkEntry(
            frame_senha_input,
            height=44,
            font=(ff, 14),
            placeholder_text="Digite sua senha",
            show="*",
            border_color="#D1D5DB",
            fg_color="#F9FAFB",
            text_color="#111827",
        )
        self.entry_senha.pack(side="left", fill="x", expand=True)
        self.entry_senha.bind("<Return>", lambda e: self._tentar_login())

        self.btn_toggle_senha = ctk.CTkButton(
            frame_senha_input,
            text="Mostrar",
            width=75,
            height=44,
            font=(ff, 11, "bold"),
            fg_color="#E5E7EB",
            hover_color="#D1D5DB",
            text_color="#374151",
            command=self._toggle_senha,
        )
        self.btn_toggle_senha.pack(side="right", padx=(6, 0))

        # Checkbox Lembrar de mim
        self.check_lembrar = ctk.CTkCheckBox(
            container,
            text="Lembrar de mim",
            font=(ff, 12),
            text_color=self.cores.get("texto_suave", "#6B7280"),
            fg_color=cor_principal,
            hover_color=self.cores.get("hover", "#B91C1C"),
            border_color="#D1D5DB",
        )
        self.check_lembrar.pack(anchor="w", padx=40, pady=(8, 0))

        # Label de erro
        self.label_erro = ctk.CTkLabel(
            container,
            text="",
            font=(ff, 11),
            text_color="#DC2626",
            wraplength=360,
        )
        self.label_erro.pack(pady=(6, 0))

        # Botao Entrar
        self.btn_entrar = ctk.CTkButton(
            container,
            text="ENTRAR",
            height=48,
            font=(ff, 15, "bold"),
            fg_color=cor_principal,
            hover_color=self.cores.get("hover", "#B91C1C"),
            corner_radius=12,
            command=self._tentar_login,
        )
        self.btn_entrar.pack(fill="x", padx=40, pady=(18, 0))

        # Loading label
        self.label_loading = ctk.CTkLabel(
            container,
            text="",
            font=(ff, 11),
            text_color=self.cores.get("texto_suave", "#6B7280"),
        )
        self.label_loading.pack(pady=(8, 0))

        # Versao
        ctk.CTkLabel(
            container,
            text="Versao 6.0",
            font=(ff, 10),
            text_color=self.cores.get("texto_suave", "#6B7280"),
        ).pack(side="bottom", pady=(0, 18))

    def _toggle_senha(self) -> None:
        self._senha_visivel = not self._senha_visivel
        self.entry_senha.configure(show="" if self._senha_visivel else "*")
        self.btn_toggle_senha.configure(
            text="Ocultar" if self._senha_visivel else "Mostrar"
        )

    def _tentar_login(self) -> None:
        if self._autenticando:
            return

        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            self.label_erro.configure(text="Preencha usuario e senha.")
            return

        self._autenticando = True
        self.label_erro.configure(text="")
        self.label_loading.configure(text="Autenticando...")
        self.btn_entrar.configure(state="disabled", text="ENTRANDO...")

        def _tarefa():
            try:
                dados = auth_service.login(usuario, senha)

                # Registrar auditoria de login
                auditoria_service.registrar(
                    ACAO_LOGIN,
                    modulo="auth",
                    registro_afetado=dados["usuario"],
                    detalhes=f"Login bem-sucedido",
                    usuario_id=dados["id"],
                    usuario_nome=dados["nome_completo"],
                )

                # Salvar sessao se "Lembrar de mim" marcado
                if self.check_lembrar.get():
                    auth_service.salvar_sessao(dados)

                self.after(0, lambda: self._on_login_sucesso(dados))

            except ContaBloqueadaError as erro:
                self.after(
                    0, lambda: self._mostrar_erro(str(erro))
                )
                self.after(
                    0,
                    lambda: auditoria_service.registrar(
                        ACAO_LOGIN_FALHOU,
                        modulo="auth",
                        registro_afetado=usuario,
                        detalhes=f"Conta bloqueada",
                    ),
                )
            except ContaInativaError as erro:
                self.after(0, lambda: self._mostrar_erro(str(erro)))
            except CredenciaisInvalidasError as erro:
                self.after(0, lambda: self._mostrar_erro(str(erro)))
                self.after(
                    0,
                    lambda: auditoria_service.registrar(
                        ACAO_LOGIN_FALHOU,
                        modulo="auth",
                        registro_afetado=usuario,
                        detalhes=f"Credenciais invalidas",
                    ),
                )
            except Exception as erro:
                logger.error(f"Erro inesperado no login: {erro}")
                self.after(
                    0,
                    lambda: self._mostrar_erro("Erro interno. Tente novamente."),
                )
            finally:
                self.after(0, self._resetar_estado_botao)
                self._autenticando = False

        threading.Thread(target=_tarefa, daemon=True).start()

    def _mostrar_erro(self, mensagem: str) -> None:
        if not self.winfo_exists():
            return
        self.label_erro.configure(text=mensagem)
        self.label_loading.configure(text="")
        self.entry_senha.delete(0, "end")
        self.entry_senha.focus_set()

    def _resetar_estado_botao(self) -> None:
        if not self.winfo_exists():
            return
        self.btn_entrar.configure(state="normal", text="ENTRAR")
        self.label_loading.configure(text="")

    def destruir_binds(self) -> None:
        """Remove binds dos entries para nao interferir com o app principal."""
        try:
            self.entry_usuario.unbind("<Return>")
            self.entry_senha.unbind("<Return>")
        except Exception:
            pass

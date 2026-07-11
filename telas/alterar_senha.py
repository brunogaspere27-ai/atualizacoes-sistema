"""
Modal de alteracao de senha do sistema CW Transportadora.

Usado tanto para:
- Primeiro login obrigatorio (deve_alterar_senha = 1)
- Alteracao voluntaria da propria senha

Features:
- Validacao de forca da senha (8 chars, maiuscula, numero, especial)
- Barra visual de forca da senha
- Impede reutilizacao da senha atual
"""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk
from tkinter import messagebox

from config.settings import settings
from services.auth_service import auth_service, SenhaFracaError, validar_forca_senha
from services.usuario_service import usuario_service
from services.auditoria_service import auditoria_service, ACAO_SENHA_ALTERADA
from telas.theme import setup_theme
from utils.logger import get_logger

logger = get_logger(__name__)


class ModalAlterarSenha(ctk.CTkToplevel):
    """Janela modal para alteracao de senha."""

    def __init__(
        self,
        master,
        obrigatorio: bool = False,
        on_sucesso: Optional[Callable] = None,
    ):
        self.cores = setup_theme(settings)
        super().__init__(master)

        self._obrigatorio = obrigatorio
        self._on_sucesso = on_sucesso

        self.title("Alterar Senha" if not obrigatorio else "Primeiro Acesso - Altere sua Senha")
        self.geometry("480x580")
        self.resizable(False, False)

        if obrigatorio:
            self.protocol("WM_DELETE_WINDOW", lambda: None)  # Impede fechar

        self.grab_set()
        self._criar_interface()

    def _criar_interface(self) -> None:
        ff = self.cores["font_family"]
        cor_principal = self.cores.get("principal", "#DC2626")

        # Header
        ctk.CTkLabel(
            self,
            text="Alterar Senha" if not self._obrigatorio else "Bem-vindo! Altere sua Senha",
            font=(ff, 22, "bold"),
            text_color=self.cores.get("texto", "#111827"),
        ).pack(pady=(24, 4))

        if self._obrigatorio:
            ctk.CTkLabel(
                self,
                text="Por seguranca, e obrigatorio alterar a senha inicial.",
                font=(ff, 12),
                text_color="#DC2626",
            ).pack(pady=(0, 16))
        else:
            ctk.CTkLabel(
                self,
                text="Informe a senha atual e escolha uma nova senha.",
                font=(ff, 12),
                text_color=self.cores.get("texto_suave", "#6B7280"),
            ).pack(pady=(0, 16))

        # Card principal
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        # Senha atual
        self._criar_campo(card, "Senha atual", self._get_entry_senha_atual)
        self.entry_senha_atual = self._entry_atual

        # Nova senha
        self._criar_campo(card, "Nova senha", self._get_entry_nova_senha)
        self.entry_nova_senha = self._entry_nova

        # Barra de forca
        self.progress_forca = ctk.CTkProgressBar(card, width=380, height=8)
        self.progress_forca.pack(padx=24, pady=(0, 2))
        self.progress_forca.set(0)

        self.label_forca = ctk.CTkLabel(
            card, text="Forca da senha", font=(ff, 10), text_color="#6B7280"
        )
        self.label_forca.pack(anchor="w", padx=24, pady=(0, 10))

        self.entry_nova_senha.bind("<KeyRelease>", self._atualizar_forca)

        # Confirmar nova senha
        self._criar_campo(card, "Confirmar nova senha", self._get_entry_confirmar)
        self.entry_confirmar = self._entry_confirmar

        # Label de erro
        self.label_erro = ctk.CTkLabel(
            card, text="", font=(ff, 11), text_color="#DC2626", wraplength=400
        )
        self.label_erro.pack(pady=(4, 0))

        # Botao Salvar
        ctk.CTkButton(
            card,
            text="SALVAR NOVA SENHA",
            height=46,
            font=(ff, 14, "bold"),
            fg_color=cor_principal,
            hover_color=self.cores.get("hover", "#B91C1C"),
            corner_radius=12,
            command=self._salvar,
        ).pack(fill="x", padx=24, pady=(10, 18))

        # Botao Cancelar (apenas se nao for obrigatorio)
        if not self._obrigatorio:
            ctk.CTkButton(
                card,
                text="Cancelar",
                height=38,
                font=(ff, 12),
                fg_color="transparent",
                hover_color="#F3F4F6",
                text_color="#6B7280",
                command=self.destroy,
            ).pack(pady=(0, 14))

    def _criar_campo(self, parent, label_text, getter_fn) -> None:
        ff = self.cores["font_family"]
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(10, 0))

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=(ff, 12, "bold"),
            text_color="#374151",
        ).pack(anchor="w", pady=(0, 4))

        entry = ctk.CTkEntry(
            frame,
            height=42,
            font=(ff, 13),
            show="*",
            border_color="#D1D5DB",
            fg_color="#F9FAFB",
            text_color="#111827",
        )
        entry.pack(fill="x")

        # Armazenar referencia
        if "atual" in label_text.lower():
            self._entry_atual = entry
        elif "confirmar" in label_text.lower():
            self._entry_confirmar = entry
        else:
            self._entry_nova = entry

    def _get_entry_senha_atual(self):
        return self._entry_atual

    def _get_entry_nova_senha(self):
        return self._entry_nova

    def _get_entry_confirmar(self):
        return self._entry_confirmar

    def _atualizar_forca(self, event=None) -> None:
        senha = self.entry_nova_senha.get()
        forca = 0

        if len(senha) >= 8:
            forca += 1
        if len(senha) >= 12:
            forca += 1
        if any(c.isupper() for c in senha):
            forca += 1
        if any(c.isdigit() for c in senha):
            forca += 1
        if any(not c.isalnum() for c in senha):
            forca += 1

        percent = forca / 5
        self.progress_forca.set(percent)

        cores_forca = {
            0: ("#DC2626", "Muito fraca"),
            1: ("#DC2626", "Fraca"),
            2: ("#F59E0B", "Razoavel"),
            3: ("#F59E0B", "Boa"),
            4: ("#10B981", "Forte"),
            5: ("#059669", "Muito forte"),
        }
        cor, texto = cores_forca.get(forca, ("#DC2626", "Muito fraca"))
        self.progress_forca.configure(progress_color=cor)
        self.label_forca.configure(text=f"Forca da senha: {texto}", text_color=cor)

    def _salvar(self) -> None:
        senha_atual = self.entry_senha_atual.get()
        nova_senha = self.entry_nova_senha.get()
        confirmar = self.entry_confirmar.get()

        if not senha_atual:
            self.label_erro.configure(text="Informe a senha atual.")
            return

        if not nova_senha:
            self.label_erro.configure(text="Informe a nova senha.")
            return

        if nova_senha != confirmar:
            self.label_erro.configure(text="As senhas nao conferem.")
            return

        if nova_senha == senha_atual:
            self.label_erro.configure(text="A nova senha deve ser diferente da atual.")
            return

        erro = validar_forca_senha(nova_senha)
        if erro:
            self.label_erro.configure(text=erro)
            return

        usuario = auth_service.usuario_atual
        if not usuario:
            self.label_erro.configure(text="Sessao expirada. Faca login novamente.")
            return

        try:
            usuario_service.alterar_propria_senha(
                usuario["id"], senha_atual, nova_senha
            )

            # Atualizar dados do usuario em memoria
            usuario["deve_alterar_senha"] = False

            auditoria_service.registrar(
                ACAO_SENHA_ALTERADA,
                modulo="auth",
                registro_afetado=usuario["usuario"],
                detalhes="Usuario alterou propria senha",
            )

            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")

            if self._on_sucesso:
                self._on_sucesso()

            self.destroy()

        except ValueError as erro:
            self.label_erro.configure(text=str(erro))
        except SenhaFracaError as erro:
            self.label_erro.configure(text=str(erro))
        except Exception as erro:
            logger.error(f"Erro ao alterar senha: {erro}")
            self.label_erro.configure(text="Erro inesperado. Tente novamente.")

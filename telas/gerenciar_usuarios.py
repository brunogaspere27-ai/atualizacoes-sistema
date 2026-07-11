"""
Tela de gerenciamento de usuarios do sistema CW Transportadora.

Acessivel apenas pelo Administrador Mestre.

Features:
- Tabela com todos os usuarios
- Criar / Editar / Excluir usuarios
- Ativar / Desativar contas
- Redefinir senha
- Alterar nivel de acesso
- Configurar permissoes por modulo e acao
"""

from __future__ import annotations

from tkinter import messagebox, ttk
from typing import Dict, Optional

import customtkinter as ctk

from config.settings import settings
from services.auth_service import MODULOS_PERMISSOES, auth_service, SenhaFracaError
from services.usuario_service import usuario_service
from services.auditoria_service import (
    auditoria_service,
    ACAO_USUARIO_CRIADO,
    ACAO_USUARIO_EXCLUIDO,
    ACAO_USUARIO_ATIVADO,
    ACAO_USUARIO_DESATIVADO,
    ACAO_PERMISSAO_ALTERADA,
    ACAO_SENHA_REDEFINIDA,
    ACAO_NIVEL_ALTERADO,
)
from telas.theme import setup_theme, criar_header
from utils.logger import get_logger

logger = get_logger(__name__)

_NIVEIS = ["comum", "operacional", "mestre"]
_ACOES_PERMISSAO = ["visualizar", "criar", "editar", "excluir", "exportar", "sincronizar"]


class TelaGerenciarUsuarios(ctk.CTkFrame):
    """Tela de administracao de usuarios (apenas mestre)."""

    def __init__(self, master):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])

        self._criar_layout()
        self._carregar_usuarios()

    def _criar_layout(self) -> None:
        criar_header(
            self,
            tag="ADMINISTRACAO",
            titulo="Gerenciar Usuarios",
            subtitulo="Crie, edite e controle permissoes dos usuarios do sistema.",
            cores=self.cores,
        )

        # Barra de botoes
        barra = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        barra.pack(fill="x", padx=25, pady=(8, 10))

        ctk.CTkButton(
            barra,
            text="+ Novo Usuario",
            height=40,
            font=(self.cores["font_family"], 13, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._abrir_modal_criar,
        ).pack(side="left", padx=12, pady=10)

        ctk.CTkButton(
            barra,
            text="Atualizar",
            height=40,
            font=(self.cores["font_family"], 13, "bold"),
            fg_color="#111827",
            hover_color="#374151",
            command=self._carregar_usuarios,
        ).pack(side="right", padx=12, pady=10)

        # Tabela
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        colunas = (
            "id", "nome", "usuario", "nivel", "status",
            "ultimo_login", "criado_em",
        )
        self.tabela = ttk.Treeview(card, columns=colunas, show="headings", height=18)

        titulos = {
            "id": "ID",
            "nome": "Nome Completo",
            "usuario": "Usuario",
            "nivel": "Nivel",
            "status": "Status",
            "ultimo_login": "Ultimo Login",
            "criado_em": "Criado em",
        }
        larguras = {
            "id": 50, "nome": 220, "usuario": 130, "nivel": 110,
            "status": 90, "ultimo_login": 150, "criado_em": 150,
        }

        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, anchor="center", width=larguras[col])

        self.tabela.pack(fill="both", expand=True, padx=15, pady=15)
        self.tabela.bind("<Double-1>", self._on_duplo_clique)

        # Botoes de acao abaixo da tabela
        acoes = ctk.CTkFrame(card, fg_color="transparent")
        acoes.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkButton(
            acoes, text="Editar", width=100, height=36,
            font=(self.cores["font_family"], 12, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8",
            command=self._editar_selecionado,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            acoes, text="Ativar/Desativar", width=130, height=36,
            font=(self.cores["font_family"], 12, "bold"),
            fg_color="#F59E0B", hover_color="#D97706",
            command=self._toggle_ativo,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            acoes, text="Redefinir Senha", width=140, height=36,
            font=(self.cores["font_family"], 12, "bold"),
            fg_color="#8B5CF6", hover_color="#7C3AED",
            command=self._redefinir_senha,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            acoes, text="Permissoes", width=110, height=36,
            font=(self.cores["font_family"], 12, "bold"),
            fg_color="#10B981", hover_color="#059669",
            command=self._abrir_permissoes,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            acoes, text="Excluir", width=90, height=36,
            font=(self.cores["font_family"], 12, "bold"),
            fg_color="#DC2626", hover_color="#B91C1C",
            command=self._excluir_selecionado,
        ).pack(side="right", padx=4)

    def _carregar_usuarios(self) -> None:
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for u in usuario_service.listar_usuarios():
            status = "Ativo" if u["ativo"] else "Inativo"
            if u["bloqueado_ate"]:
                status = "Bloqueado"
            self.tabela.insert("", "end", values=(
                u["id"],
                u["nome_completo"],
                u["usuario"],
                u["nivel_acesso"].capitalize(),
                status,
                u["ultimo_login"] or "Nunca",
                u["criado_em"] or "",
            ))

    def _get_usuario_selecionado(self) -> Optional[int]:
        sel = self.tabela.selection()
        if not sel:
            messagebox.showwarning("Atencao", "Selecione um usuario na tabela.")
            return None
        return int(self.tabela.item(sel[0], "values")[0])

    # ── Modal Criar/Editar ────────────────────────────────────────────────────

    def _abrir_modal_criar(self, usuario_id: Optional[int] = None) -> None:
        dados = usuario_service.obter_usuario(usuario_id) if usuario_id else None
        ModalCriarEditarUsuario(
            self,
            dados=dados,
            on_salvo=self._carregar_usuarios,
        )

    def _on_duplo_clique(self, event) -> None:
        uid = self._get_usuario_selecionado()
        if uid:
            self._abrir_modal_criar(uid)

    def _editar_selecionado(self) -> None:
        uid = self._get_usuario_selecionado()
        if uid:
            self._abrir_modal_criar(uid)

    # ── Acoes ──────────────────────────────────────────────────────────────────

    def _toggle_ativo(self) -> None:
        uid = self._get_usuario_selecionado()
        if not uid:
            return
        dados = usuario_service.obter_usuario(uid)
        if not dados:
            return

        if dados["ativo"]:
            if not messagebox.askyesno(
                "Desativar Usuario",
                f"Deseja desativar o usuario '{dados['usuario']}'?",
            ):
                return
            usuario_service.desativar_usuario(uid)
            auditoria_service.registrar(
                ACAO_USUARIO_DESATIVADO, "usuarios", dados["usuario"],
            )
        else:
            usuario_service.ativar_usuario(uid)
            auditoria_service.registrar(
                ACAO_USUARIO_ATIVADO, "usuarios", dados["usuario"],
            )

        self._carregar_usuarios()

    def _redefinir_senha(self) -> None:
        uid = self._get_usuario_selecionado()
        if not uid:
            return

        if not messagebox.askyesno(
            "Redefinir Senha",
            "Isso vai gerar uma nova senha temporaria.\nO usuario sera obrigado a altera-la no proximo login.\n\nContinuar?",
        ):
            return

        try:
            senha_temp = usuario_service.redefinir_senha(uid)
            auditoria_service.registrar(
                ACAO_SENHA_REDEFINIDA, "usuarios", str(uid),
            )
            messagebox.showinfo(
                "Senha Redefinida",
                f"Nova senha temporaria:\n\n{senha_temp}\n\nInforme ao usuario com seguranca.",
            )
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def _excluir_selecionado(self) -> None:
        uid = self._get_usuario_selecionado()
        if not uid:
            return

        dados = usuario_service.obter_usuario(uid)
        if not dados:
            return

        if not messagebox.askyesno(
            "Excluir Usuario",
            f"ATENCAO!\n\nDeseja excluir permanentemente o usuario '{dados['usuario']}'?\nEsta acao nao pode ser desfeita.",
        ):
            return

        try:
            usuario_service.excluir_usuario(uid)
            auditoria_service.registrar(
                ACAO_USUARIO_EXCLUIDO, "usuarios", dados["usuario"],
            )
            self._carregar_usuarios()
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def _abrir_permissoes(self) -> None:
        uid = self._get_usuario_selecionado()
        if not uid:
            return
        dados = usuario_service.obter_usuario(uid)
        if not dados:
            return
        if dados["nivel_acesso"] == "mestre":
            messagebox.showinfo(
                "Administrador Mestre",
                "O mestre tem acesso total. Permissoes nao sao configuraveis.",
            )
            return
        if dados["nivel_acesso"] == "operacional":
            messagebox.showinfo(
                "Administrador Operacional",
                "Operacionais tem acesso completo (exceto administracao de usuarios).\nPermissoes individuais nao sao aplicaveis.",
            )
            return
        ModalPermissoes(self, uid, dados["nome_completo"], on_salvo=self._carregar_usuarios)


# ── Modal Criar/Editar Usuario ──────────────────────────────────────────────────

class ModalCriarEditarUsuario(ctk.CTkToplevel):
    def __init__(self, master, dados=None, on_salvo=None):
        self.cores = setup_theme(settings)
        super().__init__(master)

        self._dados = dados
        self._editando = dados is not None
        self._on_salvo = on_salvo

        self.title("Editar Usuario" if self._editando else "Novo Usuario")
        self.geometry("460x480")
        self.resizable(False, False)
        self.grab_set()

        self._criar_interface()

    def _criar_interface(self) -> None:
        ff = self.cores["font_family"]

        ctk.CTkLabel(
            self,
            text="Editar Usuario" if self._editando else "Criar Novo Usuario",
            font=(ff, 22, "bold"),
        ).pack(pady=(20, 16))

        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Nome completo
        self.entry_nome = self._campo(card, "Nome completo")
        if self._dados:
            self.entry_nome.insert(0, self._dados.get("nome_completo", ""))

        # Usuario
        self.entry_usuario = self._campo(card, "Usuario (login)")
        if self._dados:
            self.entry_usuario.insert(0, self._dados.get("usuario", ""))

        # Senha (apenas na criacao)
        if not self._editando:
            self.entry_senha = self._campo(card, "Senha inicial")
        else:
            self.entry_senha = None

        # Nivel de acesso
        frame_nivel = ctk.CTkFrame(card, fg_color="transparent")
        frame_nivel.pack(fill="x", padx=20, pady=(8, 0))
        ctk.CTkLabel(
            frame_nivel, text="Nivel de acesso",
            font=(ff, 12, "bold"), text_color="#374151",
        ).pack(anchor="w")
        self.combo_nivel = ctk.CTkComboBox(
            frame_nivel,
            values=_NIVEIS,
            height=40,
            font=(ff, 13),
        )
        self.combo_nivel.pack(fill="x", pady=(2, 0))
        if self._dados:
            self.combo_nivel.set(self._dados.get("nivel_acesso", "comum"))

        # Label erro
        self.label_erro = ctk.CTkLabel(
            card, text="", font=(ff, 11), text_color="#DC2626", wraplength=380,
        )
        self.label_erro.pack(pady=(6, 0))

        # Botao salvar
        ctk.CTkButton(
            card,
            text="SALVAR" if not self._editando else "ATUALIZAR",
            height=44,
            font=(ff, 14, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._salvar,
        ).pack(fill="x", padx=20, pady=(12, 16))

        if self._editando:
            ctk.CTkButton(
                card, text="Cancelar", height=36,
                font=(ff, 12), fg_color="transparent",
                hover_color="#F3F4F6", text_color="#6B7280",
                command=self.destroy,
            ).pack(pady=(0, 12))

    def _campo(self, parent, label) -> ctk.CTkEntry:
        ff = self.cores["font_family"]
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(8, 0))
        ctk.CTkLabel(
            frame, text=label, font=(ff, 12, "bold"), text_color="#374151",
        ).pack(anchor="w")
        entry = ctk.CTkEntry(
            frame, height=40, font=(ff, 13),
            border_color="#D1D5DB", fg_color="#F9FAFB", text_color="#111827",
        )
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _salvar(self) -> None:
        nome = self.entry_nome.get().strip()
        usuario = self.entry_usuario.get().strip()
        nivel = self.combo_nivel.get()

        if not nome:
            self.label_erro.configure(text="Informe o nome completo.")
            return
        if not usuario:
            self.label_erro.configure(text="Informe o nome de usuario.")
            return

        try:
            if self._editando:
                # Apenas nivel pode ser editado
                if nivel != self._dados.get("nivel_acesso"):
                    usuario_service.alterar_nivel_acesso(self._dados["id"], nivel)
                    auditoria_service.registrar(
                        ACAO_NIVEL_ALTERADO, "usuarios", usuario,
                        detalhes=f"Nivel alterado para '{nivel}'",
                    )
            else:
                senha = self.entry_senha.get() if self.entry_senha else ""
                if not senha:
                    self.label_erro.configure(text="Informe a senha inicial.")
                    return
                uid = usuario_service.criar_usuario(
                    nome, usuario, senha, nivel,
                    auth_service.usuario_atual["id"],
                )
                auditoria_service.registrar(
                    ACAO_USUARIO_CRIADO, "usuarios", usuario,
                    detalhes=f"Nivel: {nivel}",
                )

            if self._on_salvo:
                self._on_salvo()
            self.destroy()

        except (ValueError, SenhaFracaError) as erro:
            self.label_erro.configure(text=str(erro))
        except Exception as erro:
            logger.error(f"Erro ao salvar usuario: {erro}")
            self.label_erro.configure(text="Erro inesperado.")


# ── Modal Permissoes ────────────────────────────────────────────────────────────

class ModalPermissoes(ctk.CTkToplevel):
    def __init__(self, master, usuario_id: int, nome: str, on_salvo=None):
        self.cores = setup_theme(settings)
        super().__init__(master)

        self._usuario_id = usuario_id
        self._on_salvo = on_salvo
        self._checkboxes: Dict[str, Dict[str, ctk.BooleanVar]] = {}

        self.title(f"Permissoes - {nome}")
        self.geometry("620x650")
        self.resizable(False, False)
        self.grab_set()

        self._criar_interface()

    def _criar_interface(self) -> None:
        ff = self.cores["font_family"]
        permissoes = usuario_service.obter_permissoes(self._usuario_id)

        ctk.CTkLabel(
            self, text="Configurar Permissoes",
            font=(ff, 20, "bold"),
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            self,
            text="Marque as acoes permitidas para cada modulo.",
            font=(ff, 12), text_color="#6B7280",
        ).pack(pady=(0, 10))

        # Scroll area
        scroll = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=16)
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Header row
        header_frame = ctk.CTkFrame(scroll, fg_color="#F3F4F6", corner_radius=8)
        header_frame.pack(fill="x", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            header_frame, text="Modulo", font=(ff, 11, "bold"),
            text_color="#374151", width=160, anchor="w",
        ).pack(side="left", padx=8, pady=6)

        for acao in _ACOES_PERMISSAO:
            ctk.CTkLabel(
                header_frame, text=acao.capitalize(), font=(ff, 9, "bold"),
                text_color="#374151", width=75, anchor="center",
            ).pack(side="left", padx=2, pady=6)

        # Rows
        for modulo, nome_modulo in MODULOS_PERMISSOES.items():
            if modulo in ("usuarios", "auditoria"):
                continue  # Exclusivos do mestre

            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)

            ctk.CTkLabel(
                row, text=nome_modulo, font=(ff, 12),
                text_color="#111827", width=160, anchor="w",
            ).pack(side="left", padx=8, pady=4)

            self._checkboxes[modulo] = {}
            perm_modulo = permissoes.get(modulo, {})

            for acao in _ACOES_PERMISSAO:
                var = ctk.BooleanVar(value=perm_modulo.get(acao, False))
                self._checkboxes[modulo][acao] = var

                cb = ctk.CTkCheckBox(
                    row, text="", width=75,
                    variable=var,
                    fg_color="#2563EB",
                    hover_color="#1D4ED8",
                )
                cb.pack(side="left", padx=2, pady=4)

        # Botao salvar
        ctk.CTkButton(
            self, text="SALVAR PERMISSOES", height=44,
            font=(ff, 14, "bold"),
            fg_color="#10B981", hover_color="#059669",
            command=self._salvar,
        ).pack(fill="x", padx=16, pady=(4, 14))

    def _salvar(self) -> None:
        permissoes: Dict[str, Dict[str, bool]] = {}
        for modulo, acoes_vars in self._checkboxes.items():
            permissoes[modulo] = {
                acao: var.get() for acao, var in acoes_vars.items()
            }

        try:
            usuario_service.salvar_permissoes(self._usuario_id, permissoes)
            auditoria_service.registrar(
                ACAO_PERMISSAO_ALTERADA, "usuarios", str(self._usuario_id),
                detalhes="Permissoes atualizadas",
            )
            messagebox.showinfo("Sucesso", "Permissoes salvas com sucesso!")
            if self._on_salvo:
                self._on_salvo()
            self.destroy()
        except Exception as erro:
            logger.error(f"Erro ao salvar permissoes: {erro}")
            messagebox.showerror("Erro", str(erro))

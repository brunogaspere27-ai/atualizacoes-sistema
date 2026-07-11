"""
Tela de Publicação de Versões - CW Transportadora

Interface para usuários Mestre publicarem novas versões no servidor próprio.
Seguindo princípios SOLID e desacoplada da lógica de negócio.

Features:
- Seleção do instalador .exe
- Detecção automática de versão
- Cálculo automático de SHA-256
- Edição de release notes
- Barra de progresso durante publicação
- Validação de integridade
- Auditoria completa
"""

from __future__ import annotations

import threading
import shutil
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional, Callable

import customtkinter as ctk

from config.settings import settings
from services.release_service import release_service, Channel, ReleaseInfo
from services.auditoria_service import auditoria_service, ACAO_PUBLICAR_VERSAO
from services.auth_service import auth_service
from telas.theme import setup_theme
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaPublicarVersao(ctk.CTkToplevel):
    """Tela para publicação de novas versões no servidor próprio."""

    def __init__(self, master, on_publicacao_concluida: Optional[Callable] = None):
        super().__init__(master)
        self.cores = setup_theme(settings)
        self._ff = self.cores["font_family"]
        self._on_publicacao_concluida = on_publicacao_concluida
        self._publicando = False
        self._installer_path: Optional[Path] = None
        self._version: Optional[str] = None
        self._sha256: Optional[str] = None
        self._size_mb: Optional[float] = None

        self.title("Publicar Nova Versão")
        self.geometry("700x750")
        self.resizable(False, False)
        self.configure(fg_color=self.cores["fundo"])
        self.grab_set()

        self._criar_interface()

    def _criar_interface(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=self.cores["header_bg"], corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header, text="Publicar Nova Versão",
            font=(self._ff, 24, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header, text="Distribuir atualização para todos os computadores",
            font=(self._ff, 13), text_color=self.cores["texto_suave"],
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Container principal
        container = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16)
        container.pack(fill="both", expand=True, padx=20, pady=16)

        # Seção: Seleção do Instalador
        self._criar_secao_instalador(container)

        # Seção: Informações da Versão
        self._criar_secao_informacoes(container)

        # Seção: Release Notes
        self._criar_secao_release_notes(container)

        # Seção: Canal de Publicação
        self._criar_secao_canal(container)

        # Barra de Progresso
        self._criar_barra_progresso(container)

        # Botões
        self._criar_botoes(container)

    def _criar_secao_instalador(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(20, 12))

        ctk.CTkLabel(
            frame, text="Instalador",
            font=(self._ff, 14, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w")

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", pady=(8, 0))

        self._entry_instalador = ctk.CTkEntry(
            row, placeholder_text="Selecione o arquivo .exe do instalador",
            font=(self._ff, 12)
        )
        self._entry_instalador.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._btn_selecionar = ctk.CTkButton(
            row, text="Selecionar", width=100,
            font=(self._ff, 12, "bold"),
            command=self._selecionar_instalador
        )
        self._btn_selecionar.pack(side="right")

    def _criar_secao_informacoes(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(
            frame, text="Informações da Versão",
            font=(self._ff, 14, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w")

        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(8, 0))

        # Versão
        ctk.CTkLabel(
            grid_frame, text="Versão:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._entry_versao = ctk.CTkEntry(
            grid_frame, placeholder_text="Ex: 6.1.0 (detectado automaticamente)",
            font=(self._ff, 12), width=150
        )
        self._entry_versao.grid(row=0, column=1, sticky="w")

        # SHA-256 (readonly)
        ctk.CTkLabel(
            grid_frame, text="SHA-256:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))

        self._entry_sha256 = ctk.CTkEntry(
            grid_frame, placeholder_text="Calculado automaticamente",
            font=(self._ff, 10)
        )
        self._entry_sha256.grid(row=1, column=1, sticky="w", pady=(8, 0))
        self._entry_sha256.configure(state="disabled")

        # Tamanho
        ctk.CTkLabel(
            grid_frame, text="Tamanho:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0))

        self._label_tamanho = ctk.CTkLabel(
            grid_frame, text="--",
            font=(self._ff, 12), text_color=self.cores["texto"]
        )
        self._label_tamanho.grid(row=2, column=1, sticky="w", pady=(8, 0))

    def _criar_secao_release_notes(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=12)

        ctk.CTkLabel(
            frame, text="Notas da Versão (Release Notes)",
            font=(self._ff, 14, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w")

        self._text_notes = ctk.CTkTextbox(
            frame, fg_color=self.cores["surface"], font=(self._ff, 12),
            text_color=self.cores["texto"], wrap="word", height=120
        )
        self._text_notes.pack(fill="both", expand=True, pady=(8, 0))
        
        # Texto padrão
        notes_padrao = """Mudanças nesta versão:

- Correção de bugs
- Melhorias de performance
- Novas funcionalidades

Para instalar:
1. Baixe o instalador
2. Execute o instalador
3. Siga as instruções"""
        self._text_notes.insert("1.0", notes_padrao)

    def _criar_secao_canal(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(12, 8))

        ctk.CTkLabel(
            frame, text="Canal de Publicação",
            font=(self._ff, 14, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w")

        self._segment_canal = ctk.CTkSegmentedButton(
            frame, values=["Stable", "Beta", "Dev"],
            font=(self._ff, 12, "bold"),
            command=self._on_canal_change
        )
        self._segment_canal.set("Stable")
        self._segment_canal.pack(fill="x", pady=(8, 0))

    def _criar_barra_progresso(self, parent):
        self._progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._progress_frame.pack(fill="x", padx=20, pady=(12, 8))

        self._progress_bar = ctk.CTkProgressBar(
            self._progress_frame, width=600, height=16
        )
        self._progress_bar.pack()
        self._progress_bar.set(0)

        self._label_status = ctk.CTkLabel(
            self._progress_frame, text="",
            font=(self._ff, 11), text_color=self.cores["texto_suave"]
        )
        self._label_status.pack(pady=(4, 0))

    def _criar_botoes(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(8, 20))

        self._btn_publicar = ctk.CTkButton(
            btn_frame, text="Publicar Versão", height=46, width=200,
            font=(self._ff, 14, "bold"),
            fg_color=self.cores.get("principal", "#DC2626"),
            hover_color=self.cores.get("hover", "#B91C1C"),
            command=self._iniciar_publicacao
        )
        self._btn_publicar.pack(side="left", padx=(0, 10))

        self._btn_cancelar = ctk.CTkButton(
            btn_frame, text="Cancelar", height=46, width=120,
            font=(self._ff, 14, "bold"),
            fg_color="#6B7280", hover_color="#4B5563",
            command=self.destroy
        )
        self._btn_cancelar.pack(side="left")

    def _selecionar_instalador(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o Instalador",
            filetypes=[("Executáveis", "*.exe"), ("Todos os arquivos", "*.*")]
        )

        if not file_path:
            return

        self._installer_path = Path(file_path)
        self._entry_instalador.configure(text=str(self._installer_path))

        # Validar arquivo
        if not self._installer_path.exists():
            messagebox.showerror("Erro", "Arquivo não encontrado")
            self._entry_instalador.configure(text="")
            self._installer_path = None
            return

        if self._installer_path.stat().st_size == 0:
            messagebox.showerror("Erro", "Arquivo vazio")
            self._entry_instalador.configure(text="")
            self._installer_path = None
            return

        # Calcular informações
        self._calcular_informacoes()

    def _calcular_informacoes(self):
        """Calcula SHA-256, tamanho e extrai versão."""
        if not self._installer_path:
            return

        # Exibir mensagem de carregamento
        self._label_status.configure(text="Calculando hash SHA-256...")
        self.update()

        def _calcular():
            try:
                # Calcular SHA-256
                self._sha256 = release_service._calculate_sha256(self._installer_path)
                
                # Calcular tamanho
                self._size_mb = release_service._get_file_size_mb(self._installer_path)
                
                # Extrair versão do nome do arquivo
                self._version = release_service._extract_version_from_filename(self._installer_path.name)
                
                # Atualizar UI na thread principal
                if self.winfo_exists():
                    self.after(0, self._atualizar_ui_informacoes)
            except Exception as e:
                logger.error(f"Erro ao calcular informações: {e}")
                if self.winfo_exists():
                    self.after(0, lambda: messagebox.showerror("Erro", f"Erro ao calcular informações: {e}"))

        threading.Thread(target=_calcular, daemon=True).start()

    def _atualizar_ui_informacoes(self):
        """Atualiza a UI com as informações calculadas."""
        if self._version:
            self._entry_versao.configure(text=self._version)
        
        if self._sha256:
            self._entry_sha256.configure(state="normal")
            self._entry_sha256.configure(text=self._sha256)
            self._entry_sha256.configure(state="disabled")
        
        if self._size_mb:
            self._label_tamanho.configure(text=f"{self._size_mb:.2f} MB")
        
        self._label_status.configure(text="Informações calculadas com sucesso")

    def _on_canal_change(self, value):
        """Callback quando o canal é alterado."""
        pass

    def _iniciar_publicacao(self):
        """Inicia o processo de publicação."""
        if self._publicando:
            return

        # Validações
        if not self._installer_path:
            messagebox.showerror("Erro", "Selecione o instalador")
            return

        version = self._entry_versao.get().strip()
        if not version:
            messagebox.showerror("Erro", "Informe a versão")
            return

        release_notes = self._text_notes.get("1.0", "end").strip()
        if not release_notes:
            messagebox.showerror("Erro", "Informe as notas da versão")
            return

        # Mapear canal
        canal_map = {
            "Stable": Channel.STABLE,
            "Beta": Channel.BETA,
            "Dev": Channel.DEV,
        }
        canal = canal_map.get(self._segment_canal.get(), Channel.STABLE)

        # Iniciar publicação
        self._publicando = True
        self._btn_publicar.configure(state="disabled", text="Publicando...")
        self._btn_cancelar.configure(state="disabled")
        self._btn_selecionar.configure(state="disabled")

        def _tarefa():
            def progress_callback(message: str, progress: int, total: int) -> None:
                if self.winfo_exists():
                    pct = progress / total if total > 0 else 0
                    self.after(0, lambda: self._progress_bar.set(pct))
                    self.after(0, lambda: self._label_status.configure(text=message))

            success, release_info, error = release_service.publish_release(
                installer_path=self._installer_path,
                version=version,
                release_notes=release_notes,
                channel=canal,
                published_by=auth_service.usuario_atual,
                progress_callback=progress_callback
            )

            if self.winfo_exists():
                self.after(0, lambda: self._publicacao_concluida(success, release_info, error))

        threading.Thread(target=_tarefa, daemon=True).start()

    def _publicacao_concluida(self, success: bool, release_info: Optional[ReleaseInfo], error: str):
        """Callback quando a publicação é concluída."""
        self._publicando = False
        self._btn_publicar.configure(state="normal", text="Publicar Versão")
        self._btn_cancelar.configure(state="normal")
        self._btn_selecionar.configure(state="normal")

        if success and release_info:
            # Registrar na auditoria
            try:
                auditoria_service.registrar_acao(
                    ACAO_PUBLICAR_VERSAO,
                    f"Versão {release_info.version} publicada no canal {release_info.channel}"
                )
            except Exception as e:
                logger.error(f"Erro ao registrar na auditoria: {e}")

            # Exibir resumo
            resumo = f"""Publicação concluída com sucesso!

Versão: {release_info.version}
Canal: {release_info.channel}
Arquivo: {release_info.installer_filename}
Tamanho: {release_info.installer_size / (1024*1024):.2f} MB
SHA-256: {release_info.sha256}
Servidor: {release_info.server_type}
Caminho: {release_info.server_path}

A versão já está disponível para todos os computadores."""

            messagebox.showinfo("Publicação Concluída", resumo)

            if self._on_publicacao_concluida:
                self._on_publicacao_concluida()

            self.destroy()
        else:
            messagebox.showerror("Erro na Publicação", error)
            self._progress_bar.set(0)
            self._label_status.configure(text="Publicação falhou")


def abrir_publicar_versao(master, on_concluida=None):
    """Abre a tela de publicação de versão."""
    # Verificar permissão Mestre
    if not auth_service.tem_permissao("mestre"):
        messagebox.showerror(
            "Acesso Negado",
            "Apenas usuários com nível Mestre podem publicar versões."
        )
        return

    TelaPublicarVersao(master, on_concluida)

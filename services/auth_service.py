"""
Servico de autenticacao do sistema CW Transportadora.

Responsavel por:
- Hash e verificacao de senhas (PBKDF2-HMAC-SHA256)
- Login / logout
- Gerenciamento de sessao ("Lembrar de mim")
- Bloqueio temporario apos tentativas invalidas
- Criacao do usuario mestre no primeiro boot
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import settings
from utils.database import conectar
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Constantes de seguranca ──────────────────────────────────────────────────
_ITERACOES_HASH = 600_000
_TAMANHO_SALT = 32
_TAMANHO_HASH = 64
_MAX_TENTATIVAS = 5
_MINUTOS_BLOQUEIO = 15
_SESSION_FILE_NAME = ".cw_session"

# Modulos do sistema para permissoes
MODULOS_PERMISSOES: Dict[str, str] = {
    "dashboard": "Painel Principal",
    "operacoes": "Nova Operacao",
    "notas": "Notas Importadas",
    "criar_viagem": "Criar Viagem",
    "historico": "Viagens",
    "ranking_clientes": "Ranking de Clientes",
    "combustivel": "Combustivel",
    "contas": "Contas",
    "relatorios": "Relatorios",
    "manutencao": "Manutencao",
    "funcionarios": "Funcionarios",
    "configuracoes": "Configuracoes",
    "usuarios": "Gerenciar Usuarios",
    "auditoria": "Auditoria",
    "sincronizacao": "Sincronizacao",
}

# Modulos que usuarios operacionais NAO acessam
_MODULOS_EXCLUSIVOS_MESTRE = frozenset({"usuarios", "auditoria"})


class AuthError(Exception):
    """Excecao base para erros de autenticacao."""


class CredenciaisInvalidasError(AuthError):
    pass


class ContaBloqueadaError(AuthError):
    def __init__(self, minutos_restantes: int = 0):
        self.minutos_restantes = minutos_restantes
        super().__init__(
            f"Conta bloqueada. Tente novamente em {minutos_restantes} minuto(s)."
        )


class ContaInativaError(AuthError):
    pass


class SenhaFracaError(AuthError):
    pass


def validar_forca_senha(senha: str) -> Optional[str]:
    """Retorna mensagem de erro se a senha nao atender aos requisitos, ou None."""
    if len(senha) < 8:
        return "A senha deve ter no minimo 8 caracteres."
    if not any(c.isupper() for c in senha):
        return "A senha deve conter pelo menos uma letra maiuscula."
    if not any(c.isdigit() for c in senha):
        return "A senha deve conter pelo menos um numero."
    if not any(not c.isalnum() for c in senha):
        return "A senha deve conter pelo menos um caractere especial."
    return None


class AuthService:
    """Servico singleton de autenticacao e sessao."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._usuario_atual: Optional[Dict[str, Any]] = None

    # ── Propriedades ──────────────────────────────────────────────────────────

    @property
    def usuario_atual(self) -> Optional[Dict[str, Any]]:
        return self._usuario_atual

    @property
    def esta_autenticado(self) -> bool:
        return self._usuario_atual is not None

    @property
    def eh_mestre(self) -> bool:
        u = self._usuario_atual
        return u is not None and u.get("nivel_acesso") == "mestre"

    @property
    def session_file(self) -> Path:
        return settings.dados_dir / _SESSION_FILE_NAME

    # ── Hash de senha ─────────────────────────────────────────────────────────

    @staticmethod
    def gerar_salt() -> bytes:
        return os.urandom(_TAMANHO_SALT)

    @staticmethod
    def hash_senha(senha: str, salt: bytes) -> str:
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt,
            _ITERACOES_HASH,
            dklen=_TAMANHO_HASH,
        )
        return dk.hex()

    @staticmethod
    def verificar_senha(senha: str, senha_hash: str, salt_hex: str) -> bool:
        salt = bytes.fromhex(salt_hex)
        computed = AuthService.hash_senha(senha, salt)
        return hmac.compare_digest(computed, senha_hash)

    # ── Usuario mestre ────────────────────────────────────────────────────────

    def garantir_usuario_mestre(self) -> Optional[str]:
        """
        Cria o usuario mestre (Bruno Gabriel) se nao existir, com uma senha
        aleatoria gerada no primeiro boot (nunca fica hardcoded no codigo).

        A senha gerada e' gravada uma unica vez em um arquivo de primeiro
        acesso (ver `arquivo_primeiro_acesso`) para o administrador consultar,
        e o usuario e' obrigado a troca-la no primeiro login
        (`deve_alterar_senha=1`).

        Returns:
            A senha gerada, se um usuario mestre novo foi criado agora.
            None se o usuario mestre ja existia (nada foi alterado).
        """
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", ("bruno",))
            if cursor.fetchone():
                return None  # Ja existe

            senha_gerada = secrets.token_urlsafe(12)
            salt = self.gerar_salt()
            senha_hash = self.hash_senha(senha_gerada, salt)

            cursor.execute(
                """
                INSERT INTO usuarios (
                    nome_completo, usuario, senha_hash, senha_salt,
                    nivel_acesso, ativo, deve_alterar_senha,
                    tentativas_falhas, criado_em, atualizado_em
                )
                VALUES (?, ?, ?, ?, 'mestre', 1, 1, 0, ?, ?)
                """,
                (
                    "Bruno Gabriel",
                    "bruno",
                    senha_hash,
                    salt.hex(),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()
            logger.info("Usuario mestre criado com sucesso (senha gerada aleatoriamente).")

            self._gravar_senha_primeiro_acesso(senha_gerada)
            return senha_gerada
        finally:
            conn.close()

    @property
    def arquivo_primeiro_acesso(self) -> Path:
        """Arquivo local (fora do repositorio) com a senha inicial do usuario mestre."""
        return settings.dados_dir / "PRIMEIRO_ACESSO_LEIA_E_APAGUE.txt"

    def _gravar_senha_primeiro_acesso(self, senha: str) -> None:
        """Grava a senha inicial em um arquivo de texto para o administrador ler uma unica vez."""
        try:
            self.arquivo_primeiro_acesso.write_text(
                "CW TRANSPORTADORA - Primeiro acesso\n"
                "====================================\n\n"
                "Usuario mestre criado automaticamente:\n\n"
                "  Usuario: bruno\n"
                f"  Senha temporaria: {senha}\n\n"
                "Esta senha e' de uso unico: o sistema vai pedir para troca-la\n"
                "no primeiro login. Apague este arquivo apos anotar a senha.\n",
                encoding="utf-8",
            )
            try:
                os.chmod(self.arquivo_primeiro_acesso, 0o600)
            except OSError:
                pass  # Windows pode nao suportar chmod completo
        except Exception as erro:
            logger.error(f"Erro ao gravar arquivo de primeiro acesso: {erro}")

    # ── Login ─────────────────────────────────────────────────────────────────

    def login(self, usuario: str, senha: str) -> Dict[str, Any]:
        """
        Autentica um usuario. Retorna dict com dados do usuario.

        Raises:
            CredenciaisInvalidasError: usuario/senha incorretos
            ContaBloqueadaError: conta temporariamente bloqueada
            ContaInativaError: conta desativada
        """
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, nome_completo, usuario, senha_hash, senha_salt,
                       nivel_acesso, ativo, deve_alterar_senha,
                       tentativas_falhas, bloqueado_ate
                FROM usuarios
                WHERE usuario = ?
                """,
                (usuario.strip().lower(),),
            )
            row = cursor.fetchone()

            if row is None:
                raise CredenciaisInvalidasError("Usuario ou senha incorretos.")

            (
                uid,
                nome,
                usr,
                senha_hash,
                senha_salt,
                nivel,
                ativo,
                deve_alterar,
                tentativas,
                bloqueado_ate,
            ) = row

            # Verificar bloqueio
            if bloqueado_ate:
                try:
                    dt_bloqueio = datetime.strptime(bloqueado_ate, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() < dt_bloqueio:
                        mins = max(1, int((dt_bloqueio - datetime.now()).total_seconds() / 60))
                        raise ContaBloqueadaError(mins)
                    else:
                        # Bloqueio expirou, resetar tentativas
                        cursor.execute(
                            """
                            UPDATE usuarios
                            SET tentativas_falhas = 0, bloqueado_ate = NULL,
                                atualizado_em = ?
                            WHERE id = ?
                            """,
                            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), uid),
                        )
                        conn.commit()
                        tentativas = 0
                except ValueError:
                    pass  # Formato invalido, ignorar

            # Verificar conta ativa
            if not ativo:
                raise ContaInativaError("Conta desativada. Contate o administrador.")

            # Verificar senha
            if not self.verificar_senha(senha, senha_hash, senha_salt):
                tentativas += 1
                novo_bloqueio = None
                if tentativas >= _MAX_TENTATIVAS:
                    novo_bloqueio = (
                        datetime.now() + timedelta(minutes=_MINUTOS_BLOQUEIO)
                    ).strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET tentativas_falhas = ?, bloqueado_ate = ?, atualizado_em = ?
                    WHERE id = ?
                    """,
                    (
                        tentativas,
                        novo_bloqueio,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        uid,
                    ),
                )
                conn.commit()

                if novo_bloqueio:
                    raise ContaBloqueadaError(_MINUTOS_BLOQUEIO)
                restantes = _MAX_TENTATIVAS - tentativas
                raise CredenciaisInvalidasError(
                    f"Usuario ou senha incorretos. {restantes} tentativa(s) restante(s)."
                )

            # Login bem-sucedido
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                UPDATE usuarios
                SET tentativas_falhas = 0, bloqueado_ate = NULL,
                    ultimo_login = ?, atualizado_em = ?
                WHERE id = ?
                """,
                (agora, agora, uid),
            )
            conn.commit()

            dados_usuario = {
                "id": uid,
                "nome_completo": nome,
                "usuario": usr,
                "nivel_acesso": nivel,
                "ativo": ativo,
                "deve_alterar_senha": bool(deve_alterar),
                "ultimo_login": agora,
            }

            with self._lock:
                self._usuario_atual = dados_usuario

            return dados_usuario

        finally:
            conn.close()

    # ── Logout ────────────────────────────────────────────────────────────────

    def logout(self) -> None:
        with self._lock:
            self._usuario_atual = None
        self._remover_sessao()

    # ── Sessao (Lembrar de mim) ───────────────────────────────────────────────

    def salvar_sessao(self, usuario_dados: Dict[str, Any]) -> None:
        """Salva token de sessao seguro para 'Lembrar de mim'."""
        token = secrets.token_hex(64)
        payload = {
            "usuario_id": usuario_dados["id"],
            "usuario": usuario_dados["usuario"],
            "token": token,
            "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            self.session_file.write_text(
                json.dumps(payload, ensure_ascii=False),
                encoding="utf-8",
            )
            # Restringir permissoes do arquivo (Windows: apenas proprietario)
            try:
                os.chmod(self.session_file, 0o600)
            except OSError:
                pass  # Windows pode nao suportar chmod completo
        except Exception as erro:
            logger.error(f"Erro ao salvar sessao: {erro}")

    def verificar_sessao_salva(self) -> Optional[Dict[str, Any]]:
        """
        Verifica se existe sessao valida salva.
        Retorna dados do usuario se valida, None caso contrario.
        """
        if not self.session_file.exists():
            return None

        try:
            dados = json.loads(self.session_file.read_text(encoding="utf-8"))
            usuario_id = dados.get("usuario_id")
            if not usuario_id:
                return None

            conn = conectar()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    SELECT id, nome_completo, usuario, nivel_acesso, ativo,
                           deve_alterar_senha, ultimo_login
                    FROM usuarios
                    WHERE id = ? AND ativo = 1
                    """,
                    (usuario_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    self._remover_sessao()
                    return None

                usuario_dados = {
                    "id": row[0],
                    "nome_completo": row[1],
                    "usuario": row[2],
                    "nivel_acesso": row[3],
                    "ativo": row[4],
                    "deve_alterar_senha": bool(row[5]),
                    "ultimo_login": row[6],
                }

                with self._lock:
                    self._usuario_atual = usuario_dados

                return usuario_dados
            finally:
                conn.close()

        except Exception as erro:
            logger.warning(f"Sessao invalida, removendo: {erro}")
            self._remover_sessao()
            return None

    def _remover_sessao(self) -> None:
        try:
            if self.session_file.exists():
                self.session_file.unlink()
        except Exception as erro:
            logger.debug(f"Erro ao remover arquivo de sessao: {erro}")

    # ── Permissoes (conveniencia) ─────────────────────────────────────────────

    def tem_permissao(self, modulo: str, acao: str = "visualizar") -> bool:
        """
        Verifica se o usuario atual tem permissao para o modulo/acao.
        Mestre tem acesso total. Operacional tem tudo exceto modulos exclusivos.
        """
        u = self._usuario_atual
        if u is None:
            return False

        nivel = u.get("nivel_acesso", "comum")

        if nivel == "mestre":
            return True

        if modulo in _MODULOS_EXCLUSIVOS_MESTRE:
            return False

        if nivel == "operacional":
            return True

        # Usuario comum: verificar permissoes no banco
        conn = conectar()
        cursor = conn.cursor()
        try:
            coluna_map = {
                "visualizar": "pode_visualizar",
                "criar": "pode_criar",
                "editar": "pode_editar",
                "excluir": "pode_excluir",
                "exportar": "pode_exportar",
                "sincronizar": "pode_sincronizar",
            }
            coluna = coluna_map.get(acao, "pode_visualizar")
            cursor.execute(
                f"""
                SELECT {coluna}
                FROM permissoes_usuario
                WHERE usuario_id = ? AND modulo = ?
                """,
                (u["id"], modulo),
            )
            row = cursor.fetchone()
            return bool(row and row[0])
        finally:
            conn.close()


auth_service = AuthService()

#!/usr/bin/env python3
"""
Script de Deploy Automatizado para GitHub - CW Transportadora

Automatiza o processo completo de deploy de novas versões para o GitHub:
1. Atualiza versão no versao.json
2. Gera executável com PyInstaller (opcional)
3. Gera instalador com Inno Setup (opcional)
4. Faz commit e push para o GitHub
5. Cria release no GitHub
6. Faz upload do instalador
7. Atualiza release.json

Uso:
    python deploy_github.py [major|minor|patch] [--no-build] [--no-installer] [--skip-git]

Exemplos:
    python deploy_github.py              # Deploy completo (patch)
    python deploy_github.py minor        # Deploy com incremento minor
    python deploy_github.py major --no-build  # Apenas atualiza versão e release
    python deploy_github.py patch --skip-git  # Deploy sem commit/push
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Adicionar diretório do projeto ao path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from config.settings import settings
from services.github_release_service import github_release_service, GitHubChannel
from utils.logger import get_logger

logger = get_logger(__name__)


class DeployError(Exception):
    """Exceção base para erros de deploy."""
    pass


class GitHubDeployManager:
    """Gerenciador de deploy automatizado para GitHub."""

    def __init__(self, version_type: str = "patch", no_build: bool = False,
                 no_installer: bool = False, skip_git: bool = False):
        self.version_type = version_type
        self.no_build = no_build
        self.no_installer = no_installer
        self.skip_git = skip_git
        
        self.version_file = PROJECT_DIR / "versao.json"
        self.release_dir = PROJECT_DIR / "release"
        self.installer_dir = PROJECT_DIR / "release"
        
        self.version_info = self._load_version()
        self.new_version = self._calculate_new_version()
    
    def _load_version(self) -> dict:
        """Carrega versão atual do versao.json."""
        if not self.version_file.exists():
            raise DeployError(f"Arquivo de versão não encontrado: {self.version_file}")
        
        with open(self.version_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _calculate_new_version(self) -> str:
        """Calcula nova versão baseada no tipo."""
        current = self.version_info["versao"]
        major, minor, patch = map(int, current.split("."))
        
        if self.version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif self.version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def _update_version_file(self) -> None:
        """Atualiza o arquivo versao.json com nova versão."""
        self.version_info["versao"] = self.new_version
        self.version_info["data"] = datetime.now().strftime("%d/%m/%Y")
        
        with open(self.version_file, "w", encoding="utf-8") as f:
            json.dump(self.version_info, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Versão atualizada: {self.new_version}")
    
    def _git_commit_and_push(self) -> None:
        """Faz commit e push das mudanças para o GitHub."""
        try:
            print("\n📤 Fazendo commit e push para o GitHub...")
            
            # Verificar se há mudanças
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                print("ℹ️  Nenhuma mudança para commitar")
                return
            
            # Adicionar arquivos
            subprocess.run(
                ["git", "add", "versao.json", "release.json"],
                cwd=PROJECT_DIR,
                check=True,
                capture_output=True
            )
            
            # Commit
            commit_msg = f"Release v{self.new_version}"
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"⚠️  Nada para commitar ou erro no commit")
            
            # Push
            print("📤 Enviando para o GitHub...")
            subprocess.run(
                ["git", "push"],
                cwd=PROJECT_DIR,
                check=True,
                capture_output=True
            )
            
            print("✅ Commit e push realizados com sucesso")
            
        except subprocess.CalledProcessError as e:
            raise DeployError(f"Erro no git commit/push: {e.stderr}")
        except Exception as e:
            raise DeployError(f"Erro ao fazer commit/push: {e}")
    
    def _build_with_release_script(self) -> Path:
        """Executa o script release.py para gerar executável e instalador."""
        try:
            print("\n🔨 Gerando executável e instalador...")
            
            # Importar o módulo release
            import release
            
            # Criar ReleaseManager
            manager = release.ReleaseManager(
                version_type=self.version_type,
                no_build=self.no_build,
                no_installer=self.no_installer,
                upload=False  # Nós faremos o upload manualmente
            )
            
            # Executar build
            manager.execute()
            
            # Encontrar o instalador gerado
            installer_pattern = f"CW_Transportadora_v{self.new_version}_Setup.exe"
            installer_path = None
            
            for file_path in self.release_dir.glob("*.exe"):
                if installer_pattern in file_path.name:
                    installer_path = file_path
                    break
            
            if not installer_path:
                raise DeployError(f"Instalador não encontrado: {installer_pattern}")
            
            print(f"✅ Build concluído: {installer_path}")
            return installer_path
            
        except Exception as e:
            raise DeployError(f"Erro no build: {e}")
    
    def _generate_release_notes(self) -> str:
        """Gera notas de release básicas."""
        return f"""CW Transportadora v{self.new_version}

Data: {datetime.now().strftime("%d/%m/%Y")}

Mudanças:
- Atualização de versão {self.version_info['versao']} → {self.new_version}
- Melhorias gerais no sistema
- Correção de bugs

Para instalar:
1. Baixe o instalador
2. Execute o instalador
3. Siga as instruções
"""
    
    def _publish_to_github(self, installer_path: Path) -> None:
        """Publica o release no GitHub."""
        try:
            print("\n📤 Publicando no GitHub...")
            
            # Gerar notas de release
            release_notes = self._generate_release_notes()
            
            # Publicar release
            success, release_info, error_msg = github_release_service.publish_release(
                installer_path=installer_path,
                version=self.new_version,
                release_notes=release_notes,
                channel=GitHubChannel.STABLE,
                published_by="Deploy Automatizado"
            )
            
            if not success:
                raise DeployError(f"Erro ao publicar no GitHub: {error_msg}")
            
            print(f"✅ Release publicado com sucesso!")
            print(f"📦 Tag: {release_info.github_tag}")
            print(f"🔗 URL: {release_info.github_release_url}")
            print(f"📥 Download: {release_info.github_download_url}")
            
        except Exception as e:
            raise DeployError(f"Erro ao publicar no GitHub: {e}")
    
    def execute(self) -> None:
        """Executa o processo completo de deploy."""
        print("=" * 60)
        print("🚀 CW Transportadora - Deploy Automatizado para GitHub")
        print(f"📦 Versão: {self.version_info['versao']} → {self.new_version}")
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Validar configuração do GitHub
        if not settings.github_repo_owner or not settings.github_repo_name:
            raise DeployError(
                "❌ Configuração do GitHub incompleta.\n"
                "   Configure github_repo_owner e github_repo_name no configuracoes.json"
            )
        
        if not settings.github_token:
            print("⚠️  Token do GitHub não configurado.")
            print("   Configure github_token para repositórios privados.")
            print("   Para repositórios públicos, pode continuar sem token.")
        
        try:
            # 1. Atualizar versão
            print("\n📝 Atualizando versão...")
            self._update_version_file()
            
            # 2. Commit e push (se não skip)
            if not self.skip_git:
                self._git_commit_and_push()
            else:
                print("\n⏭️  Skip git commit/push")
            
            # 3. Build executável e instalador
            installer_path = None
            if not self.no_build:
                installer_path = self._build_with_release_script()
            else:
                print("\n⏭️  Skip build")
            
            # 4. Publicar no GitHub
            if installer_path:
                self._publish_to_github(installer_path)
            else:
                print("\n⏭️  Skip publicação no GitHub (sem instalador)")
            
            print("\n" + "=" * 60)
            print("✅ Deploy concluído com sucesso!")
            print("=" * 60)
            
            print(f"\n📝 Versão atualizada: {self.new_version}")
            print(f"📄 Arquivo de versão: {self.version_file}")
            
            if installer_path:
                print(f"\n📦 Instalador: {installer_path}")
            
        except DeployError as e:
            print(f"\n❌ Erro no deploy: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n⚠️ Deploy cancelado pelo usuário")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Script de Deploy Automatizado para GitHub - CW Transportadora",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python deploy_github.py              # Deploy completo (patch)
  python deploy_github.py minor        # Deploy com incremento minor
  python deploy_github.py major --no-build  # Apenas atualiza versão e release
  python deploy_github.py patch --skip-git  # Deploy sem commit/push
        """
    )
    
    parser.add_argument(
        "version_type",
        nargs="?",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Tipo de incremento de versão (default: patch)"
    )
    
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Não gerar executável/instalador (apenas atualizar versão)"
    )
    
    parser.add_argument(
        "--no-installer",
        action="store_true",
        help="Não gerar instalador (apenas executável)"
    )
    
    parser.add_argument(
        "--skip-git",
        action="store_true",
        help="Não fazer commit/push no git"
    )
    
    args = parser.parse_args()
    
    # Executar deploy
    manager = GitHubDeployManager(
        version_type=args.version_type,
        no_build=args.no_build,
        no_installer=args.no_installer,
        skip_git=args.skip_git
    )
    manager.execute()


if __name__ == "__main__":
    main()

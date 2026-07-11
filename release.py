#!/usr/bin/env python3
"""
Sistema de Release Automática - CW Transportadora

Executa todo o processo de release com um único comando:
1. Atualiza versão
2. Gera executável com PyInstaller
3. Gera instalador com Inno Setup
4. Calcula SHA-256
5. Atualiza arquivos de versão

Uso:
    python release.py [major|minor|patch] [--no-build] [--no-installer] [--upload]

Exemplos:
    python release.py              # Incrementa patch (default)
    python release.py minor        # Incrementa minor
    python release.py major        # Incrementa major
    python release.py patch --no-build  # Apenas atualiza versão
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple


# Configurações
PROJECT_DIR = Path(__file__).parent
VERSION_FILE = PROJECT_DIR / "versao.json"
SPEC_FILE = PROJECT_DIR / "build.spec"
ISS_FILE = PROJECT_DIR / "instalador.iss"
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
RELEASE_DIR = PROJECT_DIR / "release"
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
ICON_FILE = PROJECT_DIR / "assets" / "logo.ico"


class ReleaseError(Exception):
    """Exceção base para erros de release."""
    pass


class ReleaseManager:
    """Gerenciador de releases automático."""

    def __init__(self, version_type: str = "patch", no_build: bool = False, 
                 no_installer: bool = False, upload: bool = False):
        self.version_type = version_type
        self.no_build = no_build
        self.no_installer = no_installer
        self.upload = upload
        self.version_info = self._load_version()
        self.new_version = self._calculate_new_version()

    def _load_version(self) -> Dict[str, str]:
        """Carrega versão atual do versao.json."""
        if not VERSION_FILE.exists():
            raise ReleaseError(f"Arquivo de versão não encontrado: {VERSION_FILE}")
        
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
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
        
        with open(VERSION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.version_info, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Versão atualizada: {self.new_version}")

    def _generate_spec_file(self) -> None:
        """Gera arquivo .spec para PyInstaller com ícone."""
        project_dir_str = str(PROJECT_DIR).replace('\\', '/')
        icon_path_str = str(ICON_FILE).replace('\\', '/')
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[r'{project_dir_str}'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('config', 'config'),
        ('telas', 'telas'),
        ('services', 'services'),
        ('utils', 'utils'),
        ('models', 'models'),
        ('migrations', 'migrations'),
        ('versao.json', '.'),
        ('configuracoes.json', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'sqlite3',
        'requests',
        'matplotlib',
        'numpy',
        'reportlab',
        'loguru',
        'psycopg2',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CW_Transportadora',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{icon_path_str}',
)
'''
        
        with open(SPEC_FILE, "w", encoding="utf-8") as f:
            f.write(spec_content)
        
        print(f"✅ Arquivo .spec gerado com ícone: {SPEC_FILE}")

    def _generate_iss_file(self, exe_path: Path) -> None:
        """Gera arquivo .iss para Inno Setup com ícone."""
        exe_size = exe_path.stat().st_size if exe_path.exists() else 0
        exe_size_mb = exe_size / (1024 * 1024)
        
        project_dir_str = str(PROJECT_DIR).replace('\\', '/')
        icon_path_str = str(ICON_FILE).replace('\\', '/')
        
        iss_content = f'''[Setup]
AppName=CW Transportadora
AppVersion={self.new_version}
AppPublisher=CW Transportadora
AppPublisherURL=
AppSupportURL=
AppUpdatesURL=
DefaultDirName={{commonpf}}\\CW Transportadora
DefaultGroupName=CW Transportadora
OutputDir={RELEASE_DIR}
OutputBaseFilename=CW_Transportadora_v{self.new_version}_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={{app}}\\CW_Transportadora.exe
InternalCompressLevel=max
SetupIconFile={icon_path_str}
UninstallIconFile={icon_path_str}

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\\BrazilianPortuguese.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar ícone na área de trabalho"; GroupDescription: "Ícones adicionais:"

[Files]
Source: "{exe_path}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{project_dir_str}\\assets\\*"; DestDir: "{{app}}\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{project_dir_str}\\config\\*"; DestDir: "{{app}}\\config"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{project_dir_str}\\telas\\*"; DestDir: "{{app}}\\telas"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{project_dir_str}\\services\\*"; DestDir: "{{app}}\\services"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{project_dir_str}\\utils\\*"; DestDir: "{{app}}\\utils"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{project_dir_str}\\models\\*"; DestDir: "{{app}}\\models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{project_dir_str}\\migrations\\*"; DestDir: "{{app}}\\migrations"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{project_dir_str}\\versao.json"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\CW Transportadora"; Filename: "{{app}}\\CW_Transportadora.exe"; IconFilename: "{icon_path_str}"
Name: "{{commondesktop}}\\CW Transportadora"; Filename: "{{app}}\\CW_Transportadora.exe"; IconFilename: "{icon_path_str}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\CW_Transportadora.exe"; Description: "Iniciar CW Transportadora"; Flags: nowait postinstall skipifsilent
'''
        
        with open(ISS_FILE, "w", encoding="utf-8") as f:
            f.write(iss_content)
        
        print(f"✅ Arquivo .iss gerado com ícone: {ISS_FILE}")

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calcula hash SHA-256 de um arquivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _clean_build_dirs(self) -> None:
        """Limpa diretórios de build anteriores com tratamento de erros."""
        import stat
        import time
        
        def remove_readonly(func, path, excinfo):
            """Trata arquivos com atributo readonly."""
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass
        
        dirs_to_clean = [BUILD_DIR, DIST_DIR]
        for dir_path in dirs_to_clean:
            if not dir_path.exists():
                continue
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    shutil.rmtree(dir_path, onerror=remove_readonly)
                    print(f"🧹 Limpo: {dir_path}")
                    break
                except PermissionError as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Arquivo em uso, tentando novamente ({attempt + 1}/{max_retries})...")
                        time.sleep(2)
                    else:
                        print(f"⚠️ Não foi possível limpar {dir_path}: {e}")
                        print(f"   Feche qualquer instância do aplicativo e tente novamente")
                except Exception as e:
                    print(f"⚠️ Erro ao limpar {dir_path}: {e}")
                    break

    def _build_executable(self) -> Path:
        """Gera executável com PyInstaller."""
        print("\n🔨 Gerando executável com PyInstaller...")
        
        if not SPEC_FILE.exists():
            self._generate_spec_file()
        
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(SPEC_FILE)]
        result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise ReleaseError(f"Erro no PyInstaller:\n{result.stderr}")
        
        exe_path = DIST_DIR / "CW_Transportadora.exe"
        if not exe_path.exists():
            raise ReleaseError(f"Executável não encontrado: {exe_path}")
        
        exe_size = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executável gerado: {exe_path} ({exe_size:.2f} MB)")
        return exe_path

    def _build_installer(self, exe_path: Path) -> Path:
        """Gera instalador com Inno Setup."""
        print("\n🔨 Gerando instalador com Inno Setup...")
        
        if not ISS_FILE.exists():
            self._generate_iss_file(exe_path)
        
        # Criar diretório de release
        RELEASE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Procurar compilador do Inno Setup
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe",
        ]
        
        iscc_path = None
        for path in inno_paths:
            if Path(path).exists():
                iscc_path = path
                break
        
        if not iscc_path:
            raise ReleaseError(
                "Inno Setup não encontrado. Instale em: https://jrsoftware.org/isdl.php"
            )
        
        cmd = [iscc_path, str(ISS_FILE)]
        result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise ReleaseError(f"Erro no Inno Setup:\n{result.stderr}")
        
        # Procurar o instalador gerado
        installer_pattern = f"CW_Transportadora_v{self.new_version}_Setup.exe"
        installer_path = None
        
        # Verificar no diretório de release
        for file_path in RELEASE_DIR.glob("*.exe"):
            if installer_pattern in file_path.name:
                installer_path = file_path
                break
        
        if not installer_path:
            raise ReleaseError(f"Instalador não encontrado: {installer_pattern}")
        
        installer_size = installer_path.stat().st_size / (1024 * 1024)
        print(f"✅ Instalador gerado: {installer_path} ({installer_size:.2f} MB)")
        return installer_path

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

SHA-256: [será preenchido após build]
"""

    def _create_release_info(self, installer_path: Path) -> Dict[str, str]:
        """Cria informações do release para upload."""
        sha256 = self._calculate_sha256(installer_path)
        size_mb = installer_path.stat().st_size / (1024 * 1024)
        
        release_info = {
            "versao": self.new_version,
            "data": datetime.now().strftime("%d/%m/%Y"),
            "nome": "CW Transportadora",
            "installer_path": str(installer_path),
            "installer_size_mb": f"{size_mb:.2f}",
            "sha256": sha256,
            "release_notes": self._generate_release_notes().replace("[será preenchido após build]", sha256),
        }
        
        # Salvar release info
        release_info_file = RELEASE_DIR / f"release_v{self.new_version}.json"
        with open(release_info_file, "w", encoding="utf-8") as f:
            json.dump(release_info, f, ensure_ascii=False, indent=4)
        
        print(f"✅ Release info salvo: {release_info_file}")
        print(f"📋 SHA-256: {sha256}")
        
        return release_info

    def _upload_to_github(self, installer_path: Path, release_info: Dict[str, str]) -> None:
        """Faz upload do release para GitHub (requer gh CLI)."""
        print("\n📤 Fazendo upload para GitHub...")
        
        # Verificar se gh CLI está instalado
        result = subprocess.run(["gh", "--version"], capture_output=True)
        if result.returncode != 0:
            print("⚠️ GitHub CLI não encontrado. Instale em: https://cli.github.com/")
            print("📝 Manualmente: Crie release no GitHub e faça upload do instalador")
            return
        
        # Criar release no GitHub
        tag = f"v{self.new_version}"
        title = f"CW Transportadora v{self.new_version}"
        notes_file = RELEASE_DIR / f"release_notes_v{self.new_version}.txt"
        
        with open(notes_file, "w", encoding="utf-8") as f:
            f.write(release_info["release_notes"])
        
        cmd = [
            "gh", "release", "create",
            tag,
            "--title", title,
            "--notes-file", str(notes_file),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Erro ao criar release: {result.stderr}")
            print("📝 Crie o release manualmente no GitHub")
            return
        
        # Fazer upload do instalador
        cmd = [
            "gh", "release", "upload",
            tag,
            str(installer_path),
            "--clobber"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Erro ao fazer upload: {result.stderr}")
            print("📝 Faça upload manualmente do instalador")
            return
        
        print(f"✅ Release criado no GitHub: {tag}")

    def execute(self) -> None:
        """Executa o processo completo de release."""
        print("=" * 60)
        print(f"🚀 CW Transportadora - Release Automático")
        print(f"📦 Versão: {self.version_info['versao']} → {self.new_version}")
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("=" * 60)
        
        # Validar existência do ícone
        if not ICON_FILE.exists():
            raise ReleaseError(
                f"❌ Arquivo de ícone não encontrado: {ICON_FILE}\n"
                f"   O ícone é obrigatório para o build do executável e instalador.\n"
                f"   Certifique-se de que o arquivo 'logo.ico' existe na pasta 'assets/'."
            )
        
        print(f"✅ Ícone encontrado: {ICON_FILE}")
        
        try:
            # 1. Atualizar versão
            print("\n📝 Atualizando versão...")
            self._update_version_file()
            
            # 2. Limpar diretórios de build
            if not self.no_build:
                print("\n🧹 Limpando diretórios de build...")
                self._clean_build_dirs()
            
            # 3. Gerar executável
            exe_path = None
            if not self.no_build:
                exe_path = self._build_executable()
            
            # 4. Gerar instalador
            installer_path = None
            if not self.no_build and not self.no_installer:
                try:
                    installer_path = self._build_installer(exe_path)
                except ReleaseError as e:
                    print(f"⚠️ Erro ao gerar instalador: {e}")
                    print("   Continuando sem instalador...")
            
            # 5. Calcular SHA-256 e criar release info
            if installer_path:
                release_info = self._create_release_info(installer_path)
                
                # 6. Upload para GitHub (opcional)
                if self.upload:
                    self._upload_to_github(installer_path, release_info)
            
            print("\n" + "=" * 60)
            print("✅ Release concluído com sucesso!")
            print("=" * 60)
            
            if installer_path:
                print(f"\n📦 Instalador: {installer_path}")
                print(f"📋 SHA-256: {release_info['sha256']}")
                print(f"📊 Tamanho: {release_info['installer_size_mb']} MB")
            
            print(f"\n📝 Versão atualizada: {self.new_version}")
            print(f"📄 Arquivo de versão: {VERSION_FILE}")
            
        except ReleaseError as e:
            print(f"\n❌ Erro no release: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n⚠️ Release cancelado pelo usuário")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Sistema de Release Automática - CW Transportadora",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python release.py              # Incrementa patch (default)
  python release.py minor        # Incrementa minor
  python release.py major        # Incrementa major
  python release.py patch --no-build  # Apenas atualiza versão
  python release.py minor --upload    # Build e upload para GitHub
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
        "--upload",
        action="store_true",
        help="Fazer upload para GitHub (requer gh CLI)"
    )
    
    args = parser.parse_args()
    
    # Verificar dependências
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller não instalado. Execute: pip install pyinstaller")
        sys.exit(1)
    
    # Executar release
    manager = ReleaseManager(
        version_type=args.version_type,
        no_build=args.no_build,
        no_installer=args.no_installer,
        upload=args.upload
    )
    manager.execute()


if __name__ == "__main__":
    main()

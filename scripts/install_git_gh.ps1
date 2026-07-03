Param()

function Write-Info {
    Write-Host "[INFO]" $args -ForegroundColor Cyan
}

function Write-Warn {
    Write-Host "[WARN]" $args -ForegroundColor Yellow
}

function Write-ErrorAndExit {
    Write-Host "[ERROR]" $args -ForegroundColor Red
    exit 1
}

function Get-CommonExecutablePaths {
    param([string]$command)
    switch ($command) {
        'git' {
            return @(
                'C:\Program Files\Git\cmd\git.exe',
                'C:\Program Files (x86)\Git\cmd\git.exe'
            )
        }
        'gh' {
            return @(
                'C:\Program Files\GitHub CLI\bin\gh.exe',
                'C:\Program Files (x86)\GitHub CLI\bin\gh.exe'
            )
        }
        default {
            return @()
        }
    }
}

function Test-CommandAccessible {
    param([string]$command)
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Get-CommandExecutablePath {
    param([string]$command)
    try {
        $cmd = Get-Command $command -ErrorAction Stop
        return $cmd.Path
    } catch {
        foreach ($path in Get-CommonExecutablePaths -command $command) {
            if (Test-Path $path) { return $path }
        }
        return $null
    }
}

function Test-CommandExists {
    param([string]$command)
    return [bool](Get-CommandExecutablePath -command $command)
}

function Find-ExecutablePaths {
    param([string]$command)
    $paths = @()
    foreach ($path in Get-CommonExecutablePaths -command $command) {
        if (Test-Path $path) { $paths += $path }
    }
    if ($command -eq 'gh') {
        $paths += Get-ChildItem -Path 'C:\Program Files','C:\Program Files (x86)' -Filter gh.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
    }
    if ($command -eq 'git') {
        $paths += Get-ChildItem -Path 'C:\Program Files','C:\Program Files (x86)' -Filter git.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
    }
    return $paths | Sort-Object -Unique
}

function Print-InstallStatus {
    param(
        [string]$command,
        [bool]$found
    )
    if ($found) {
        if (Test-CommandAccessible -command $command) {
            Write-Info "$command já está disponível no shell."
            try {
                & $command --version
            } catch {
                Write-Warn "Não foi possível executar '$command --version'."
            }
        } else {
            $exePath = Get-CommandExecutablePath -command $command
            Write-Warn "$command está instalado, mas não está no PATH. Abra um novo terminal ou adicione '$exePath' ao PATH."
            if ($exePath) {
                Write-Host "Localização encontrada: $exePath" -ForegroundColor Yellow
                try {
                    & "$exePath" --version
                } catch {
                    Write-Warn "Não foi possível executar '$exePath --version'."
                }
            }
        }
        return
    }

    Write-Warn "$command ainda não foi encontrado no shell atual. Reinicie o terminal ou abra um novo prompt para atualizar o PATH."
    $paths = Find-ExecutablePaths -command $command
    if ($paths.Count -gt 0) {
        Write-Host ("Possíveis localizações encontradas para " + $command + ":") -ForegroundColor Yellow
        $paths | ForEach-Object { Write-Host "  $_" }
    } else {
        Write-Warn "Nenhuma instalação de $command foi encontrada nos caminhos comuns."
    }
}

function Install-Git-WithWinget {
    Write-Info "Tentando instalar Git via winget..."
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
}

function Install-GH-WithWinget {
    Write-Info "Tentando instalar GitHub CLI via winget..."
    winget install --id GitHub.cli -e --source winget --accept-package-agreements --accept-source-agreements
}

function Download-File {
    param(
        [string]$url,
        [string]$dest
    )
    Write-Info "Baixando $url ..."
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -ErrorAction Stop
}

function Install-Git-FromInstaller {
    param([string]$dest)
    Write-Info "Instalando Git silenciosamente..."
    Start-Process -FilePath $dest -ArgumentList "/VERYSILENT", "/NORESTART" -Wait -NoNewWindow
}

function Install-GH-FromInstaller {
    param([string]$dest)
    Write-Info "Instalando GitHub CLI silenciosamente..."
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i", "`"$dest`"", "/qn", "/norestart" -Wait -NoNewWindow
}

function Install-Git-Direct {
    $tmp = Join-Path $env:TEMP "git_gh_installs"
    if (-not (Test-Path $tmp)) { New-Item -ItemType Directory -Path $tmp | Out-Null }

    $arch = if ($env:PROCESSOR_ARCHITECTURE -eq 'AMD64') { '64' } else { '32' }
    $gitUrl = if ($arch -eq '64') { 'https://github.com/git-for-windows/git/releases/latest/download/Git-64-bit.exe' } else { 'https://github.com/git-for-windows/git/releases/latest/download/Git-32-bit.exe' }
    $gitDest = Join-Path $tmp "Git-setup.exe"

    Download-File -url $gitUrl -dest $gitDest
    Install-Git-FromInstaller -dest $gitDest
}

function Install-GH-Direct {
    $tmp = Join-Path $env:TEMP "git_gh_installs"
    if (-not (Test-Path $tmp)) { New-Item -ItemType Directory -Path $tmp | Out-Null }

    $ghUrl = 'https://github.com/cli/cli/releases/latest/download/gh-windows-amd64.msi'
    $ghDest = Join-Path $tmp "gh.msi"

    Download-File -url $ghUrl -dest $ghDest
    Install-GH-FromInstaller -dest $ghDest
}

Write-Info "Iniciando instalação de Git e GitHub CLI..."

if (Test-CommandAccessible -command "git") {
    Write-Info "Git já está disponível no PATH: $(& git --version)"
} elseif (Test-CommandExists -command "git") {
    $gitPath = Get-CommandExecutablePath -command "git"
    Write-Warn "Git está instalado em '$gitPath', mas não está no PATH. Abra um novo terminal ou adicione esse caminho ao PATH."
} else {
    if (Test-CommandAccessible -command "winget") {
        try {
            Install-Git-WithWinget
        } catch {
            Write-Warn "winget falhou ao instalar Git. Tentando download direto..."
            Install-Git-Direct
        }
    } else {
        Write-Warn "winget não encontrado. Tentando download direto..."
        Install-Git-Direct
    }
}

if (Test-CommandAccessible -command "gh") {
    Write-Info "GitHub CLI já está disponível no PATH: $(& gh --version | Select-Object -First 1)"
} elseif (Test-CommandExists -command "gh") {
    $ghPath = Get-CommandExecutablePath -command "gh"
    Write-Warn "GitHub CLI está instalado em '$ghPath', mas não está no PATH. Abra um novo terminal ou adicione esse caminho ao PATH."
} else {
    if (Test-CommandAccessible -command "winget") {
        try {
            Install-GH-WithWinget
        } catch {
            Write-Warn "winget falhou ao instalar GitHub CLI. Tentando download direto..."
            Install-GH-Direct
        }
    } else {
        Write-Warn "winget não encontrado. Tentando download direto..."
        Install-GH-Direct
    }
}

Write-Info "Instalação concluída. Verificando disponibilidade..."
Print-InstallStatus -command "git" -found (Test-CommandExists -command "git")
Print-InstallStatus -command "gh" -found (Test-CommandExists -command "gh")

Write-Host "`nSe ambos aparecerem, execute:"
Write-Host "  .\scripts\install_dev_tools.ps1"
Write-Host "  .\scripts\commit_and_push.ps1 -createPR"

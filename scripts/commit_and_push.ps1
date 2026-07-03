Param(
    [string]$branch = "feature/security-ui-improvements",
    [string]$remote = "origin",
    [string]$commitMessage = "chore: security, dev tooling, CI, UI theme and dashboard polish",
    [switch]$createPR
)

function Resolve-ExecutablePath {
    param(
        [string]$exe,
        [string[]]$fallbackPaths
    )

    $command = Get-Command $exe -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Path
    }

    foreach ($path in $fallbackPaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    return $null
}

function Ensure-ExecutableOnPath {
    param(
        [string]$exe,
        [string[]]$fallbackPaths
    )

    $path = Resolve-ExecutablePath -exe $exe -fallbackPaths $fallbackPaths
    if (-not $path) {
        return $false
    }

    $directory = Split-Path $path
    if ($env:PATH -notmatch [regex]::Escape($directory)) {
        $env:PATH = "$directory;$env:PATH"
        Write-Host "Added $directory to PATH for this session."
    }
    return $true
}

function Get-CommonGitPaths {
    return @(
        'C:\Program Files\Git\cmd\git.exe',
        'C:\Program Files (x86)\Git\cmd\git.exe'
    )
}

function Get-CommonGhPaths {
    return @(
        'C:\Program Files\GitHub CLI\gh.exe',
        'C:\Program Files\GitHub CLI\bin\gh.exe',
        'C:\Program Files (x86)\GitHub CLI\gh.exe',
        'C:\Program Files (x86)\GitHub CLI\bin\gh.exe'
    )
}

Write-Host "Preparing to create branch and push changes..."

if (-not (Test-Path ".git")) {
    Write-Error ".git not found. Initialize a git repository first or install Git with .\scripts\install_git_gh.ps1."
    exit 1
}

if (-not (Ensure-ExecutableOnPath -exe "git" -fallbackPaths (Get-CommonGitPaths))) {
    Write-Error "git is not available in this terminal and was not found in the common install paths."
    exit 1
}

git status --porcelain | Out-Null

Write-Host "Creating and switching to branch $branch"
$branchExists = (git branch --list $branch) -ne $null -and (git branch --list $branch).Trim() -ne ''
if ($branchExists) {
    git checkout $branch
} else {
    git checkout -b $branch
}

Write-Host "Staging changes..."
git add -A

Write-Host "Committing..."
git commit -m $commitMessage

Write-Host "Installing pre-commit hooks (if missing) and running checks"
try {
    pre-commit install
} catch {
    Write-Host "pre-commit not available; ensure it's installed from requirements-dev.txt"
}

try {
    pre-commit run --all-files
} catch {
    Write-Host "pre-commit reported issues; please fix or review the output"
}

Write-Host "Staging any auto-fixed changes and committing style fixes"
git add -A
try {
    git commit -m "style: apply pre-commit fixes"
} catch {
    Write-Host "No style changes to commit"
}

Write-Host "Pushing branch to remote $remote"
git push -u $remote $branch

if ($createPR) {
    if (-not (Ensure-ExecutableOnPath -exe "gh" -fallbackPaths (Get-CommonGhPaths))) {
        Write-Host "GitHub CLI (gh) not found in PATH. Checking common install paths..."
        if (-not (Resolve-ExecutablePath -exe "gh" -fallbackPaths (Get-CommonGhPaths))) {
            Write-Host "GitHub CLI (gh) not found. Install it or add it to PATH before creating a PR."
        } else {
            Write-Host "GitHub CLI found and added to PATH."
        }
    }

    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $bodyFile = [System.IO.Path]::GetTempFileName()
        try {
            Get-Content -Path "COMMIT_CHANGES.txt" -Raw | Set-Content -Path $bodyFile -NoNewline
            & gh pr create --head $branch --base main --title $commitMessage --body-file $bodyFile
        } finally {
            if (Test-Path $bodyFile) { Remove-Item $bodyFile -Force }
        }
    } else {
        Write-Host "GitHub CLI (gh) not found. Install it to create PR automatically, or create a PR manually."
    }
}

Write-Host "Done. Review the remote branch and open a PR if desired."

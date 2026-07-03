@echo off
echo ========================================
echo Configurando Sincronizacao CW Transportadora
echo ========================================
echo.

if exist .env (
    echo Arquivo .env ja existe. Deseja sobrescrever? (S/N)
    set /p resposta=
    if /i not "%resposta%"=="S" (
        echo Configuracao cancelada.
        pause
        exit /b
    )
)

echo Criando arquivo .env...
copy .env.example .env >nul

echo Configurando URL do Supabase...
powershell -Command "(Get-Content .env) -replace 'SUPABASE_URL=', 'SUPABASE_URL=postgresql://postgres:gasperewinter2026@db.pcbvfqlqbrcozlxeeyzd.supabase.co:5432/postgres?sslmode=require' | Set-Content .env"

echo.
echo ========================================
echo Configuracao concluida com sucesso!
echo ========================================
echo.
echo O sistema agora ira sincronizar automaticamente
echo entre os PCs a cada 60 segundos.
echo.
pause

@echo off
echo ==========================================
echo   Sistema de Aprovacao - Ponto Interno
echo ==========================================
echo.

REM Define o diretorio base como a pasta onde o .bat esta
set BASE_DIR=%~dp0

REM Verifica se o Python esta instalado
where py >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Python nao encontrado. Instale o Python 3 primeiro.
    pause
    exit /b 1
)

REM Cria o ambiente virtual se nao existir
if not exist "%BASE_DIR%venv" (
    echo Criando ambiente virtual...
    py -3 -m venv "%BASE_DIR%venv"
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)

REM Ativa o ambiente virtual
echo Ativando ambiente virtual...
call "%BASE_DIR%venv\Scripts\activate.bat"

REM Instala as dependencias
echo Instalando dependencias...
pip install -r "%BASE_DIR%requirements.txt" --quiet

REM Verifica se o .env existe
if not exist "%BASE_DIR%.env" (
    echo.
    echo AVISO: Arquivo .env nao encontrado!
    echo Copie o arquivo .env.exemplo para .env e preencha as credenciais.
    echo.
    pause
    exit /b 1
)

REM Inicia a aplicacao
echo.
echo Iniciando a aplicacao...
echo Acesse: http://localhost:5001
echo.
python "%BASE_DIR%run.py"

pause

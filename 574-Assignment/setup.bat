@echo off
REM Setup script for 574 Assignment with uv (Windows)

echo ================================================================
echo 574 Assignment Setup Script (Windows with uv)
echo ================================================================

REM Check if we're in the right directory
if not exist pyproject.toml (
    echo Error: Please run this script from the 574-Assignment directory
    exit /b 1
)

REM Check if uv is installed
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: uv not found. Please install uv:
    echo    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    exit /b 1
)

echo Using uv:
uv --version
echo.

echo.
echo Step 1: Installing Python 3.12 and dependencies with uv...
echo    This will create a venv and install pymilvus, sentence-transformers, torch, etc.
echo.

uv sync

if %ERRORLEVEL% neq 0 (
    echo Failed to install dependencies
    echo.
    echo Troubleshooting:
    echo   - Ensure Python 3.12 is installed
    echo   - Or try: uv venv --python 3.12 ^&^& uv sync
    exit /b 1
)

echo.
echo Dependencies installed successfully
echo.
echo Step 2: Building OpenAI embeddings storage...
echo.

uv run python scripts\1_build_openai_embeddings.py

if %ERRORLEVEL% neq 0 (
    echo Failed to build OpenAI embeddings
    echo    Make sure rulebook storage exists in main project
    exit /b 1
)

echo.
echo Step 3: Building Qwen + Milvus storage...
echo    This will download Qwen model (~600MB) on first run
echo.

uv run python scripts\2_build_qwen_milvus.py

if %ERRORLEVEL% neq 0 (
    echo Failed to build Qwen + Milvus storage
    exit /b 1
)

echo.
echo ================================================================
echo Setup Complete!
echo ================================================================
echo.
echo Next steps:
echo   1. Review test questions: type ground_truth\test_questions.json
echo   2. Run evaluation: uv run python scripts\3_run_evaluation.py
echo   3. Check results: dir results
echo.

pause

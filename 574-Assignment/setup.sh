#!/bin/bash
# Setup script for 574 Assignment with uv
# Works on macOS and Linux. For Windows, use setup.bat or run commands manually.

set -e

echo "================================================================"
echo "574 Assignment Setup Script (with uv)"
echo "================================================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the 574-Assignment directory"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv not found. Please install uv:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Using uv: $(uv --version)"
echo ""

echo ""
echo "Step 1: Installing Python 3.12 and dependencies with uv..."
echo "   This will create a venv and install pymilvus, sentence-transformers, torch, etc."
echo ""

uv sync

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo ""
    echo "Troubleshooting:"
    echo "  - Ensure Python 3.12 is installed: pyenv install 3.12"
    echo "  - Or try: uv venv --python 3.12 && uv sync"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully"
echo ""
echo "Step 2: Building OpenAI embeddings storage..."
echo ""

uv run python scripts/1_build_openai_embeddings.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to build OpenAI embeddings"
    echo "   Make sure rulebook storage exists in main project"
    exit 1
fi

echo ""
echo "Step 3: Building Qwen + Milvus storage..."
echo "   This will download Qwen model (~600MB) on first run"
echo ""

uv run python scripts/2_build_qwen_milvus.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Qwen + Milvus storage"
    exit 1
fi

echo ""
echo "================================================================"
echo "✅ Setup Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. Review test questions: cat ground_truth/test_questions.json"
echo "  2. Run evaluation: uv run python scripts/3_run_evaluation.py"
echo "  3. Check results: ls -lh results/"
echo ""

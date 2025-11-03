#!/bin/bash
# Startup script for ShadowScribe 2.0

set -e

echo "🎲 Starting ShadowScribe 2.0..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with your API keys:"
    echo "  OPENAI_API_KEY=sk-..."
    echo "  ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Start Docker Compose services
echo "🚀 Starting Docker Compose services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."

# Wait for MySQL to be healthy
until docker-compose exec -T mysql mysqladmin ping -h localhost --silent 2>/dev/null; do
    echo "   Waiting for MySQL..."
    sleep 2
done

echo "✅ MySQL is ready"

# Wait for API to be healthy
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    echo "   Waiting for API..."
    sleep 2
done

echo "✅ API is ready"

# Wait for frontend to be ready
until curl -s http://localhost:3000 > /dev/null 2>&1; do
    echo "   Waiting for frontend..."
    sleep 2
done

echo "✅ Frontend is ready"
echo ""

# Check if characters need to be migrated
echo "🔄 Checking for character migration..."
if docker-compose exec -T api python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from api.database.connection import AsyncSessionLocal
from api.database.repositories.character_repo import CharacterRepository
import asyncio

async def check():
    async with AsyncSessionLocal() as session:
        repo = CharacterRepository(session)
        chars = await repo.get_all()
        return len(chars)

result = asyncio.run(check())
print(result)
" 2>/dev/null; then
    CHAR_COUNT=$(docker-compose exec -T api python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from api.database.connection import AsyncSessionLocal
from api.database.repositories.character_repo import CharacterRepository
import asyncio

async def check():
    async with AsyncSessionLocal() as session:
        repo = CharacterRepository(session)
        chars = await repo.get_all()
        return len(chars)

result = asyncio.run(check())
print(result)
" 2>/dev/null | tail -1)
    
    if [ "$CHAR_COUNT" = "0" ]; then
        echo "   No characters in database. Running migration..."
        docker-compose exec -T api python scripts/migrate_characters_to_db.py
    else
        echo "   Found $CHAR_COUNT character(s) in database"
    fi
fi

echo ""
echo "✨ ShadowScribe 2.0 is ready!"
echo ""
echo "📍 Access points:"
echo "   Frontend:  http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   MySQL:     localhost:3306"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f [mysql|api|frontend]"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""

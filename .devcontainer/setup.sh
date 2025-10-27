#!/bin/bash

set -e

echo "🚀 Setting up LLM Session Manager in Codespaces..."

# Install Poetry
echo "📦 Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/home/vscode/.local/bin:$PATH"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
poetry install

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Initialize database
echo "💾 Initializing database..."
poetry run python -m llm_session_manager.cli init --demo

# Generate JWT secret and create .env
echo "🔐 Generating secure configuration..."
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
cat > backend/.env << EOF
JWT_SECRET_KEY=${JWT_SECRET}
DATABASE_URL=sqlite:///./collaboration.db
BACKEND_PORT=8000
FRONTEND_PORT=3000
EOF

# Generate test tokens
echo "🎫 Generating test tokens..."
cd backend
python3 generate_tokens.py > /dev/null 2>&1 || true
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Quick Start:"
echo "  • List sessions:  poetry run python -m llm_session_manager.cli list"
echo "  • Monitor:        poetry run python -m llm_session_manager.cli monitor"
echo "  • Start backend:  cd backend && uvicorn app.main:app --reload --host 0.0.0.0"
echo "  • Start frontend: cd frontend && npm run dev"
echo ""
echo "📚 Documentation: See README.md"
echo ""

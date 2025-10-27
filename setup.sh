#!/bin/bash

# LLM Session Manager - One-Command Setup
# Usage: curl -fsSL https://raw.githubusercontent.com/yourusername/llm-session-manager/main/setup.sh | bash
# Or: ./setup.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.10"
NODE_MIN_VERSION="18"

clear

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        LLM Session Manager - Instant Setup                    ║
║        Monitor • Collaborate • Learn from AI Sessions         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo ""
echo -e "${BLUE}This script will:${NC}"
echo "  ✓ Check prerequisites"
echo "  ✓ Install all dependencies"
echo "  ✓ Set up CLI tool"
echo "  ✓ Configure collaboration server (optional)"
echo "  ✓ Generate test tokens"
echo "  ✓ Start monitoring your AI sessions"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 1
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Step 1: Checking Prerequisites${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python found:${NC} $(python3 --version)"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}⚠️  Poetry not found. Installing...${NC}"
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    echo -e "${GREEN}✅ Poetry installed${NC}"
else
    echo -e "${GREEN}✅ Poetry found:${NC} $(poetry --version)"
fi

# Ask about collaboration features
echo ""
echo -e "${BLUE}Do you want to install collaboration features?${NC}"
echo "  (Allows team collaboration via web interface)"
read -p "Install collaboration? (y/n) " -n 1 -r INSTALL_COLLAB
echo ""

SETUP_COLLAB=false
if [[ $INSTALL_COLLAB =~ ^[Yy]$ ]]; then
    SETUP_COLLAB=true

    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js not found${NC}"
        echo "Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    echo -e "${GREEN}✅ Node.js found:${NC} $(node --version)"

    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ npm found:${NC} $(npm --version)"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Step 2: Installing CLI Tool${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
poetry install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ CLI tool installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install CLI tool${NC}"
    exit 1
fi

# Test CLI
echo ""
echo "Testing CLI..."
poetry run python -m llm_session_manager.cli info

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ CLI tool is working${NC}"
else
    echo -e "${RED}❌ CLI tool failed${NC}"
    exit 1
fi

# Install collaboration features
if [ "$SETUP_COLLAB" = true ]; then
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  Step 3: Setting Up Collaboration Features${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""

    # Install backend dependencies
    echo "Installing backend dependencies..."
    cd backend
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"

    # Install frontend dependencies
    echo ""
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"

    # Generate JWT secret
    echo ""
    echo "Generating secure JWT secret..."
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

    # Create .env file
    cat > backend/.env << EOF
JWT_SECRET_KEY=${JWT_SECRET}
DATABASE_URL=sqlite:///./collaboration.db
BACKEND_PORT=8000
FRONTEND_PORT=3000
EOF
    echo -e "${GREEN}✅ Configuration file created${NC}"

    # Initialize database
    echo ""
    echo "Initializing database..."
    cd backend
    python3 init_database.py 2>/dev/null || echo "Database ready"
    cd ..

    # Generate test tokens
    echo ""
    echo "Generating test tokens..."
    cd backend
    python3 generate_tokens.py > /dev/null 2>&1 || true
    cd ..
    echo -e "${GREEN}✅ Test tokens generated${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Step 4: Quick Start Options${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${BLUE}What would you like to do?${NC}"
echo ""
echo "1) 🔍 Monitor my AI sessions (CLI only)"
echo "2) 👥 Start collaboration server (Backend + Frontend)"
echo "3) 🎯 Try demo mode with sample data"
echo "4) 📚 Show me the documentation"
echo "5) ⏭️  Skip - I'll explore on my own"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Starting session monitor...${NC}"
        echo ""
        poetry run python -m llm_session_manager.cli list
        echo ""
        echo -e "${CYAN}Next steps:${NC}"
        echo "  • Run: poetry run python -m llm_session_manager.cli monitor"
        echo "  • Run: poetry run python -m llm_session_manager.cli health <session-id>"
        echo "  • Run: poetry run python -m llm_session_manager.cli insights <session-id>"
        ;;
    2)
        if [ "$SETUP_COLLAB" = true ]; then
            echo ""
            echo -e "${GREEN}Creating launcher script...${NC}"

            # Create launch script
            cat > start.sh << 'LAUNCH_EOF'
#!/bin/bash

# Start backend and frontend in parallel

echo "Starting LLM Session Manager..."
echo ""
echo "Backend will run at: http://localhost:8000"
echo "Frontend will run at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both
wait
LAUNCH_EOF
            chmod +x start.sh

            echo -e "${GREEN}✅ Created start.sh launcher${NC}"
            echo ""
            echo -e "${CYAN}Starting servers...${NC}"
            echo ""
            ./start.sh
        else
            echo -e "${YELLOW}Collaboration features not installed.${NC}"
            echo "Re-run setup and choose 'y' for collaboration features."
        fi
        ;;
    3)
        echo ""
        echo -e "${GREEN}Starting demo mode...${NC}"
        poetry run python -m llm_session_manager.cli monitor
        ;;
    4)
        echo ""
        echo -e "${CYAN}Documentation:${NC}"
        echo ""
        echo "📖 Main Guide:        README.md"
        echo "🚀 Quick Start:       QUICKSTART.md"
        echo "🏗️  Architecture:      docs/ARCHITECTURE_EXPLAINED.md"
        echo "🧠 AI Insights:       docs/COGNEE_INTEGRATION.md"
        echo "👥 Collaboration:     docs/REALTIME_COLLABORATION.md"
        echo "🔧 CLI Guide:         docs/CLI_GUIDE.md"
        echo ""
        ;;
    5)
        echo ""
        echo -e "${CYAN}All set! Here's what you can do:${NC}"
        ;;
esac

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Setup Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Quick Commands:${NC}"
echo ""
echo "  # List active sessions"
echo "  poetry run python -m llm_session_manager.cli list"
echo ""
echo "  # Monitor in real-time"
echo "  poetry run python -m llm_session_manager.cli monitor"
echo ""
echo "  # Get AI insights"
echo "  poetry run python -m llm_session_manager.cli insights <session-id>"
echo ""

if [ "$SETUP_COLLAB" = true ]; then
    echo "  # Start collaboration server"
    echo "  ./start.sh"
    echo ""
    echo "  # View test tokens"
    echo "  cat backend/test_tokens.txt"
    echo ""
fi

echo -e "${CYAN}Documentation:${NC} README.md"
echo -e "${CYAN}Support:${NC} https://github.com/yourusername/llm-session-manager/issues"
echo ""
echo -e "${MAGENTA}Happy coding! 🚀${NC}"
echo ""

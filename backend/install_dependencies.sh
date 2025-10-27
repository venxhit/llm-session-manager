#!/bin/bash
# Install all backend dependencies

echo "========================================"
echo "Installing Backend Dependencies"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    echo "Please run this from the backend/ directory"
    exit 1
fi

echo "📦 Installing Python packages..."
echo ""

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Installation Complete!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Create .env file: cp .env.example .env"
    echo "2. Generate tokens: python3 generate_tokens.py"
    echo "3. Start server: uvicorn app.main:app --reload"
else
    echo ""
    echo "========================================"
    echo "❌ Installation Failed"
    echo "========================================"
    echo ""
    echo "Try installing packages individually:"
    echo "  pip install fastapi uvicorn[standard]"
    echo "  pip install python-jose[cryptography] passlib[bcrypt]"
    echo "  pip install sqlalchemy python-dotenv"
    exit 1
fi

#!/bin/bash

echo "🚀 LLM Session Manager - GitHub Push Script"
echo "=========================================="
echo ""

# Step 1: Create the repository on GitHub
echo "Step 1: Creating GitHub repository..."
gh repo create llm-session-manager \
  --public \
  --description "The first CLI tool to manage multiple AI coding sessions with real-time health monitoring and token tracking" \
  --source=. \
  --remote=origin \
  --push

if [ $? -eq 0 ]; then
  echo "✅ Repository created and code pushed successfully!"
  echo ""
  echo "🎉 Your repository is live at:"
  echo "   https://github.com/iamgagan/llm-session-manager"
  echo ""
  echo "📝 Next steps:"
  echo "   1. Add repository topics (ai, claude-code, cursor, cli, tui, python)"
  echo "   2. Create a demo video and add it to the README"
  echo "   3. Start reaching out to pilot companies"
else
  echo "❌ Failed to create repository"
  echo ""
  echo "Please try one of these alternatives:"
  echo ""
  echo "Option 1: Manual creation"
  echo "  1. Go to: https://github.com/new"
  echo "  2. Repository name: llm-session-manager"
  echo "  3. Description: The first CLI tool to manage multiple AI coding sessions with real-time health monitoring and token tracking"
  echo "  4. Visibility: Public"
  echo "  5. DO NOT initialize with README, .gitignore, or license"
  echo "  6. Click 'Create repository'"
  echo "  7. Run: git push -u origin main"
  echo ""
  echo "Option 2: Authenticate gh CLI first"
  echo "  1. Run: gh auth login"
  echo "  2. Follow the prompts to authenticate"
  echo "  3. Run this script again"
fi

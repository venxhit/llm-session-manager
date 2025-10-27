# 🚀 Instant Start Guide

**Get started in under 60 seconds!**

Choose the method that works best for you:

---

## ⚡ Method 1: One Command Install (Recommended)

**Time: 30 seconds**

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/llm-session-manager/main/setup.sh | bash
```

That's it! The script will:
- ✅ Check prerequisites
- ✅ Install all dependencies
- ✅ Set up CLI tool
- ✅ Generate test tokens
- ✅ Start your first session

---

## 🐳 Method 2: Docker Compose (Zero Config)

**Time: 1 minute**

```bash
# Clone and start
git clone https://github.com/yourusername/llm-session-manager.git
cd llm-session-manager
docker-compose up -d

# Open in browser
open http://localhost:3000
```

Done! Everything runs in containers.

---

## ☁️ Method 3: GitHub Codespaces (No Install)

**Time: 30 seconds**

1. Click: [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/yourusername/llm-session-manager/codespaces)
2. Wait 30 seconds for environment to build
3. Run: `poetry run python -m llm_session_manager.cli list`

Everything pre-installed and configured!

---

## 🌐 Method 4: Try Web Demo (Instant)

**Time: 0 seconds**

[**Open Live Demo →**](https://demo.llmsessionmanager.com)

No installation required. Try all features with sample data.

---

## 📦 Method 5: pip Install (Coming Soon)

**Time: 10 seconds**

```bash
pip install llm-session-manager
llm-session init
llm-session list
```

---

## 🎯 First Steps After Install

### See Your Active Sessions
```bash
poetry run python -m llm_session_manager.cli list
```

### Start Real-Time Monitoring
```bash
poetry run python -m llm_session_manager.cli monitor
```

### Get AI Insights
```bash
poetry run python -m llm_session_manager.cli insights <session-id>
```

### Share with Team
```bash
poetry run python -m llm_session_manager.cli share <session-id>
```

---

## 🎓 Quick Tutorial (2 minutes)

### Step 1: List Sessions
```bash
$ poetry run python -m llm_session_manager.cli list

📊 Active Sessions:
┌─────────────────────┬───────────────┬──────────┬─────────┐
│ Session ID          │ Type          │ Tokens   │ Health  │
├─────────────────────┼───────────────┼──────────┼─────────┤
│ claude_code_60389   │ Claude Code   │ 164k/200k│ 82%     │
│ cursor_cli_12345    │ Cursor        │ 50k/200k │ 95%     │
└─────────────────────┴───────────────┴──────────┴─────────┘
```

### Step 2: Get Insights
```bash
$ poetry run python -m llm_session_manager.cli insights 60389

🧠 AI Insights for Session 60389:

📊 Health: 82% (Good)
🎯 Tokens: 164k / 200k (82% used)

💡 Recommendations:
  • Consider starting fresh at 80% based on 50 past sessions
  • Similar session patterns suggest 30 mins remaining
  • Error rate is normal (2 errors/hour)

⚠️  Warnings:
  • Approaching token limit
  • 3 similar failures in past 2 weeks at 85%+

🔍 Similar Sessions:
  • session_abc123 - solved authentication bug
  • session_xyz789 - teammate Alice's approach
```

### Step 3: Start Collaboration
```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Get tokens
cat backend/test_tokens.txt

# Browser: http://localhost:3000
# Login with tokens and collaborate!
```

---

## 💡 Common Use Cases

### For Solo Developers

**"When should I start a fresh session?"**
```bash
llm-session insights <session-id>
# AI tells you based on past patterns
```

**"What did I work on yesterday?"**
```bash
llm-session search "authentication"
llm-session memory-search "how to setup JWT"
```

**"How are my sessions doing?"**
```bash
llm-session monitor
# Real-time dashboard
```

### For Teams

**"Share my session for code review"**
```bash
llm-session share <session-id>
# Generates shareable link
# Team sees live updates
```

**"Collaborate on debugging"**
```bash
# All team members join same session
# Live chat + cursor tracking
# Add code comments at specific lines
```

**"Learn from team's past work"**
```bash
llm-session memory-search "solved CORS issue"
# Finds solutions from all team sessions
```

---

## 🔧 Troubleshooting

### Setup script fails
```bash
# Check prerequisites
python3 --version  # Should be 3.10+
poetry --version   # Should be installed

# Install Poetry if missing
curl -sSL https://install.python-poetry.org | python3 -
```

### Can't find sessions
```bash
# Make sure you have an active AI coding session
# Open Claude Code, Cursor, or Copilot
# Then run:
poetry run python -m llm_session_manager.cli list
```

### Docker issues
```bash
# Check Docker is running
docker ps

# Restart containers
docker-compose down
docker-compose up -d
```

### Frontend won't start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📚 Next Steps

### Learn More
- **[README.md](README.md)** - Full documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Detailed quick start
- **[ARCHITECTURE_EXPLAINED.md](docs/ARCHITECTURE_EXPLAINED.md)** - How it works

### Advanced Features
- **[COGNEE_INTEGRATION.md](docs/COGNEE_INTEGRATION.md)** - AI insights setup
- **[MCP_IMPLEMENTATION_SUMMARY.md](docs/MCP_IMPLEMENTATION_SUMMARY.md)** - Claude Desktop integration
- **[VSCODE_EXTENSION_GUIDE.md](docs/VSCODE_EXTENSION_GUIDE.md)** - VS Code extension

### Contributing
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[GitHub Issues](https://github.com/yourusername/llm-session-manager/issues)** - Report bugs

---

## 🎉 You're Ready!

You now have:
- ✅ Session monitoring working
- ✅ AI insights configured
- ✅ Team collaboration ready (optional)
- ✅ All features at your fingertips

**Start monitoring your AI sessions now:**
```bash
poetry run python -m llm_session_manager.cli monitor
```

**Questions?** Open an issue or check the docs!

---

**Built with ❤️ for AI-powered development teams**

*Monitor smarter • Collaborate better • Learn continuously*

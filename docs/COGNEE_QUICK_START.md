# Cognee Quick Start - Get AI Insights Now! 🚀

## ✅ Already Installed!

Cognee is installed and ready to use. You just need to set one environment variable.

---

## 🔑 Setup (30 seconds)

### Step 1: Set Your API Key

Cognee needs `LLM_API_KEY` environment variable:

```bash
# For OpenAI (recommended - what you have):
export LLM_API_KEY="sk-proj-your-openai-key-here"

# OR for Anthropic Claude:
export LLM_API_KEY="sk-ant-your-anthropic-key-here"
```

**Important:** Use `LLM_API_KEY` (not `OPENAI_API_KEY`)

### Step 2: Test It!

```bash
poetry run python -m llm_session_manager.cli insights 65260
```

When prompted, choose `Y` to capture learnings.

---

## 🎯 What You'll See

### First Session (Building Knowledge)
```bash
$ poetry run python -m llm_session_manager.cli insights 65260

🧠 Analyzing Session with AI...
✅ Found session: claude_code_65260
   Health: 100%

🔍 Searching past sessions for patterns...
✅ No issues found. This is the first session or everything looks good!

💾 Capture learnings? [Y/n]: Y
Capturing session learnings...
✅ Session learnings captured!
```

### Future Sessions (Getting Smarter!)
```bash
$ poetry run python -m llm_session_manager.cli insights 65260

🧠 Analyzing Session with AI...
✅ Found session: claude_code_65260
   Health: 85%

🔍 Searching past sessions for patterns...

⚠️  Warnings:
  • Found 3 similar error patterns in past sessions

💡 Recommendations:
  • Token usage at 85%. Past sessions suggest starting fresh around 80%
  • Found 5 past sessions in this project

🔗 Similar Sessions:
  • Session had similar token usage pattern
  • Healthy session in /path/to/project
  • Error solution from 2 days ago
```

---

## 💡 Use Cases

### Check Before Starting Work
```bash
# "Should I start a new session?"
poetry run python -m llm_session_manager.cli insights 65260
```

### Learn From Failures
```bash
# "Why did that fail?"
poetry run python -m llm_session_manager.cli insights 12345
```

### Build Team Knowledge
```bash
# Every session you analyze adds to team knowledge
# Over time, get smarter recommendations!
```

---

## 🐛 Troubleshooting

### "LLM API key is not set"

**Solution:** Export the environment variable:
```bash
export LLM_API_KEY="your-api-key-here"
```

Then run the command again.

### "Empty graph"

This is normal for the first run! Cognee needs to build its knowledge base. Just capture one session:

```bash
poetry run python -m llm_session_manager.cli insights 65260
# Choose Y to capture
```

### Make It Permanent

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
echo 'export LLM_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📊 How It Works

1. **Capture** - Run `insights` command, capture session data
2. **Process** - Cognee builds knowledge graph using LLM
3. **Search** - Future sessions search the graph for patterns
4. **Recommend** - Get AI-powered insights based on history

---

## 🎉 That's It!

You're ready to use AI-powered session intelligence!

**Next:** Run the insights command after each coding session to build your knowledge base over time.

```bash
export LLM_API_KEY="your-openai-key"
poetry run python -m llm_session_manager.cli insights 65260
```

The more sessions you capture, the smarter it gets! 🧠✨

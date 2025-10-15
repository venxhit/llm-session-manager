# Hybrid Detection System

LLM Session Manager uses a sophisticated **hybrid detection system** to identify AI coding assistants running on your system.

## Overview

Instead of hardcoded patterns, we use a 3-tier detection strategy:

```
┌─────────────────────────────────────────┐
│         Process Discovered              │
└──────────────┬──────────────────────────┘
               │
               ▼
       ┌──────────────┐
       │  Registry    │ ◄─── Fast, accurate (99% cases)
       │  Detector    │
       └──────┬───────┘
              │ Match? ✅
              │
              ▼ No match
       ┌──────────────┐
       │  Heuristic   │ ◄─── Smart patterns (edge cases)
       │  Detector    │
       └──────┬───────┘
              │ Match? ✅
              │
              ▼ No match
       ┌──────────────┐
       │  LLM         │ ◄─── AI-powered (opt-in)
       │  Detector    │
       └──────┬───────┘
              │
              ▼
        ┌─────────┐
        │ Result  │
        └─────────┘
```

---

## Tier 1: Registry Detector ⚡ (Primary)

**Speed**: Fastest
**Accuracy**: Highest for known tools
**Coverage**: Claude Code, Cursor, GitHub Copilot, Windsurf, Aider, Codeium, Tabnine, Continue

### How it works:

Uses a community-maintained YAML registry ([`ai_tools_registry.yaml`](../llm_session_manager/config/ai_tools_registry.yaml)) with patterns for each tool:

```yaml
claude_code:
  patterns:
    process_names: ['claude', 'Claude', 'node']
    cmdline_keywords: ['claude-code', '@anthropic/claude']
    paths:
      macos: ['/Applications/Claude.app']
      windows: ['C:\\Program Files\\Claude']
  exclude_patterns: ['helper', 'crashpad', 'gpu']
```

### Advantages:
- ✅ **Fast** - Simple pattern matching
- ✅ **Accurate** - Tested patterns for known tools
- ✅ **Maintainable** - Community can add new tools
- ✅ **Platform-aware** - Different paths for macOS/Windows/Linux
- ✅ **No API calls** - Works offline

### Example:
```python
detector = RegistryDetector()
session_type = detector.identify_session_type(process)
# Returns: SessionType.CLAUDE_CODE
```

---

## Tier 2: Heuristic Detector 🧠 (Fallback)

**Speed**: Fast
**Accuracy**: Good for unknown tools
**Coverage**: Any AI tool with recognizable patterns

### How it works:

Analyzes process characteristics using intelligent heuristics:

**Indicators checked:**
- AI-related keywords (ai, llm, gpt, claude, copilot, assistant)
- Tech stack (electron, node, language-server)
- Memory usage (>50MB typical for AI tools)
- Network activity (API calls)
- File patterns

**Scoring system:**
```python
score = (
    keyword_match * 0.3 +
    tech_stack * 0.2 +
    memory_usage * 0.15 +
    network_activity * 0.15 +
    file_patterns * 0.2
)

if score >= 0.6:  # 60% confidence threshold
    return inferred_type
```

### Advantages:
- ✅ **Flexible** - Can detect unknown tools
- ✅ **No manual config** - Self-adapting
- ✅ **Fast** - Local analysis only
- ✅ **Privacy-preserving** - No external calls

### Example:
```python
detector = HeuristicDetector()
session_type = detector.identify_session_type(process)
# Returns: SessionType.CURSOR_CLI (60% confidence)
```

---

## Tier 3: LLM Detector 🤖 (Optional)

**Speed**: Slowest
**Accuracy**: Highest for complete unknowns
**Coverage**: ANY AI tool

### How it works:

Uses a local or cloud LLM to intelligently analyze processes:

```python
prompt = f"""
Analyze this process:
Process Name: {proc_name}
Command Line: {cmdline}

Is this an AI coding assistant?
Which one: Claude Code, Cursor, Copilot, Windsurf, Other?
Is this a helper process to ignore?

Respond with JSON:
{{
    "is_ai_assistant": true/false,
    "tool_name": "claude_code",
    "is_helper_process": false,
    "confidence": 0.95
}}
"""
```

### Providers supported:
- **Ollama** (default) - Local, privacy-preserving, free
- **Anthropic Claude** - Cloud API, requires key
- **OpenAI GPT** - Cloud API, requires key

### Advantages:
- ✅ **Smartest** - Can reason about unknown tools
- ✅ **Adaptable** - Learns from context
- ✅ **Future-proof** - No manual updates needed

### Disadvantages:
- ⚠️ **Slow** - API call per process (~1-2 seconds)
- ⚠️ **Opt-in required** - Disabled by default
- ⚠️ **API costs** - If using cloud providers
- ⚠️ **Privacy** - Sends process info (use Ollama for privacy)

### Example:
```python
detector = LLMDetector(provider="ollama", model="llama3.2", enabled=True)
session_type = detector.identify_session_type(process)
# Returns: SessionType.CLAUDE_CODE (95% confidence)
```

---

## Usage

### Default (Registry + Heuristics):
```python
from llm_session_manager.core.detectors import HybridDetector

detector = HybridDetector()
session_type = detector.identify_session_type(process)
```

### With LLM Fallback (Opt-in):
```python
detector = HybridDetector(
    enable_llm=True,
    llm_provider="ollama",  # Local, privacy-preserving
    llm_model="llama3.2"
)
```

### In CLI:
```bash
# Default (fast, no LLM)
python -m llm_session_manager.cli list

# With LLM fallback (slower, more accurate)
python -m llm_session_manager.cli list --enable-llm

# With specific provider
python -m llm_session_manager.cli list --enable-llm --llm-provider anthropic
```

---

## Performance Comparison

| Strategy   | Speed | Accuracy | Privacy | API Cost |
|------------|-------|----------|---------|----------|
| Registry   | ⚡⚡⚡  | ⭐⭐⭐    | ✅      | Free     |
| Heuristic  | ⚡⚡   | ⭐⭐     | ✅      | Free     |
| LLM (Ollama)| ⚡    | ⭐⭐⭐    | ✅      | Free     |
| LLM (Cloud) | ⚡    | ⭐⭐⭐    | ⚠️      | $$$      |

---

## Detection Statistics

The hybrid detector tracks which strategy was used:

```python
stats = detector.get_detection_stats()
print(stats)
# Output:
# {
#   'registry_matches': 45,      # 90% via registry
#   'heuristic_matches': 5,       # 10% via heuristics
#   'llm_matches': 0,             # 0% via LLM (disabled)
#   'total_processes': 50,
#   'registry_percentage': 90.0,
#   'heuristic_percentage': 10.0
# }
```

---

## Adding New Tools to Registry

The registry is community-maintained! Add support for new AI coding tools:

1. **Fork the repo**
2. **Edit** [`ai_tools_registry.yaml`](../llm_session_manager/config/ai_tools_registry.yaml)
3. **Add your tool**:

```yaml
my_new_tool:
  display_name: "My New AI Tool"
  description: "Description of the tool"
  patterns:
    process_names:
      - "mytool"
    cmdline_keywords:
      - "mytool-ide"
    paths:
      macos:
        - "/Applications/MyTool.app"
  exclude_patterns:
    - "helper"
  token_limits:
    default: 100000
```

4. **Submit PR**
5. **Everyone benefits!**

---

## Configuration

Configure detection in [`config.yaml`](~/.config/llm-session-manager/config.yaml):

```yaml
# Detection strategy
detection_strategy: "hybrid"  # registry, heuristic, llm, hybrid

# LLM fallback settings
llm_fallback:
  enabled: false  # Opt-in for privacy
  provider: "ollama"  # ollama, anthropic, openai
  model: "llama3.2"  # Local model by default
  confidence_threshold: 0.7
  max_retries: 2
```

---

## Why Hybrid?

**Problem with hardcoding:**
- ❌ Breaks when tools update
- ❌ Platform-specific (macOS only)
- ❌ Can't detect new tools (WindSurf, Aider, etc.)
- ❌ False positives (macOS TextInputUI)
- ❌ Requires code changes for every new tool

**Solution with hybrid:**
- ✅ Community-maintainable registry
- ✅ Cross-platform support
- ✅ Automatically detects new tools (heuristics)
- ✅ AI-powered fallback (optional)
- ✅ No code changes needed - just update YAML

---

## Future Enhancements

1. **Auto-update registry** from GitHub
2. **ML-based classification** (trained model)
3. **Crowdsourced patterns** (users submit patterns)
4. **Telemetry** (anonymized detection stats)
5. **Plugin system** (custom detectors)

---

## Technical Details

### Architecture:

```
llm_session_manager/
├── core/
│   ├── detectors/
│   │   ├── __init__.py
│   │   ├── registry_detector.py    # Tier 1
│   │   ├── heuristic_detector.py   # Tier 2
│   │   ├── llm_detector.py         # Tier 3
│   │   └── hybrid_detector.py      # Orchestrator
│   └── session_discovery.py        # Uses HybridDetector
├── config/
│   └── ai_tools_registry.yaml      # Community patterns
```

### Flow:

1. **SessionDiscovery** scans processes
2. For each process, calls **HybridDetector.identify_session_type()**
3. HybridDetector tries: Registry → Heuristic → LLM (if enabled)
4. First match wins
5. Returns **SessionType** or **None**

---

## FAQ

**Q: Which strategy is used most often?**
A: Registry detector handles ~95% of cases. Heuristics catch the remaining ~5%.

**Q: Do I need to enable LLM detection?**
A: No! Registry + Heuristics work great for all known tools. LLM is only for detecting brand-new tools.

**Q: Is my data sent to external APIs?**
A: Only if you explicitly enable LLM detection with a cloud provider. By default (Ollama), everything is local.

**Q: How do I add a new tool?**
A: Edit `ai_tools_registry.yaml` and submit a PR. No code changes needed!

**Q: Can I disable heuristics?**
A: Not currently, but you can set `detection_strategy: "registry"` in config (future feature).

---

## Learn More

- [Registry File](../llm_session_manager/config/ai_tools_registry.yaml) - See all supported tools
- [Contributing](../CONTRIBUTING.md) - Add new tools to registry
- [API Documentation](../docs/API.md) - Use detectors in your code

---

**Built with ❤️ by the LLM Session Manager team**

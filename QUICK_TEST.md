# ⚡ Quick Testing Guide

**Date:** Monday, October 27, 2025

The fastest way to test all features individually.

---

## Step 1: Get Your Session IDs

```bash
poetry run python -m llm_session_manager.cli list
```

**Output:**
```
                              Active Sessions (3)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━┓
┃ ID                                  ┃ Ty… ┃ PID ┃ St… ┃ Du… ┃ To… ┃ He… ┃ T… ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━┩
│ claude_code_15825_1761613095        │ cl… │ 15… │ ac… │ 11… │ 35… │  ⚠️  │ -  │
│ cursor_cli_40041_1761613095         │ cu… │ 40… │ ac… │ 12… │ 9,… │  ⚠️  │ -  │
│ claude_code_60420_1761613095        │ cl… │ 60… │ ac… │ 12h │ 9,… │  ⚠️  │ -  │
└─────────────────────────────────────┴─────┴─────┴─────┴─────┴─────┴─────┴────┘
```

**Copy one of the session IDs** from the first column. They look like:
- `claude_code_15825_1761613095`
- `cursor_cli_40041_1761613095`
- `claude_code_60420_1761613095`

---

## Step 2: Test Core Features (5 minutes)

Replace `SESSION_ID` with your actual session ID:

```bash
# Set your session ID (copy from list above)
export SESSION_ID="claude_code_15825_1761613095"

# Test 1: View detailed session info
poetry run python -m llm_session_manager.cli info $SESSION_ID

# Test 2: Check health score
poetry run python -m llm_session_manager.cli health $SESSION_ID

# Test 3: Export to JSON
poetry run python -m llm_session_manager.cli export $SESSION_ID --format json --output /tmp/session.json
cat /tmp/session.json

# Test 4: Add tags
poetry run python -m llm_session_manager.cli tag $SESSION_ID testing feature-demo

# Test 5: List tags
poetry run python -m llm_session_manager.cli list-tags

# Test 6: Filter by tag
poetry run python -m llm_session_manager.cli list --tag testing

# Test 7: Set description
poetry run python -m llm_session_manager.cli describe $SESSION_ID "Testing session features"

# Test 8: View description
poetry run python -m llm_session_manager.cli describe $SESSION_ID --show

# Test 9: Memory stats
poetry run python -m llm_session_manager.cli memory-stats

# Test 10: Search sessions
poetry run python -m llm_session_manager.cli search "testing"
```

---

## Step 3: Test Advanced Features (3 minutes)

```bash
# Test 11: Export to YAML
poetry run python -m llm_session_manager.cli export $SESSION_ID --format yaml --output /tmp/session.yaml
cat /tmp/session.yaml

# Test 12: Export to Markdown
poetry run python -m llm_session_manager.cli export $SESSION_ID --format markdown --output /tmp/session.md
cat /tmp/session.md

# Test 13: Set project name
poetry run python -m llm_session_manager.cli project $SESSION_ID llm-session-manager

# Test 14: List projects
poetry run python -m llm_session_manager.cli list-projects

# Test 15: Filter by project
poetry run python -m llm_session_manager.cli list --project llm-session-manager

# Test 16: Auto-suggest tags (requires OpenAI API key)
poetry run python -m llm_session_manager.cli auto-tag $SESSION_ID

# Test 17: Get recommendations
poetry run python -m llm_session_manager.cli recommend $SESSION_ID

# Test 18: MCP configuration
poetry run python -m llm_session_manager.cli mcp-config
```

---

## Step 4: Test Real-Time Monitoring (1 minute)

```bash
# Launch live dashboard
poetry run python -m llm_session_manager.cli monitor

# Exit: Press Ctrl+C
```

---

## All 29 Commands Quick Reference

| Command | Example |
|---------|---------|
| `list` | `poetry run python -m llm_session_manager.cli list` |
| `list --active` | `poetry run python -m llm_session_manager.cli list --active` |
| `list --tag <tag>` | `poetry run python -m llm_session_manager.cli list --tag bugfix` |
| `list --project <name>` | `poetry run python -m llm_session_manager.cli list --project my-app` |
| `info <id>` | `poetry run python -m llm_session_manager.cli info $SESSION_ID` |
| `discover` | `poetry run python -m llm_session_manager.cli discover` |
| `init` | `poetry run python -m llm_session_manager.cli init --tool claude_code` |
| `monitor` | `poetry run python -m llm_session_manager.cli monitor` |
| `health <id>` | `poetry run python -m llm_session_manager.cli health $SESSION_ID` |
| `health-stats` | `poetry run python -m llm_session_manager.cli health-stats` |
| `export <id> --format json` | `poetry run python -m llm_session_manager.cli export $SESSION_ID --format json` |
| `export <id> --format yaml` | `poetry run python -m llm_session_manager.cli export $SESSION_ID --format yaml` |
| `export <id> --format markdown` | `poetry run python -m llm_session_manager.cli export $SESSION_ID --format markdown` |
| `tag <id> <tags>` | `poetry run python -m llm_session_manager.cli tag $SESSION_ID bugfix urgent` |
| `untag <id> <tag>` | `poetry run python -m llm_session_manager.cli untag $SESSION_ID urgent` |
| `list-tags` | `poetry run python -m llm_session_manager.cli list-tags` |
| `auto-tag <id>` | `poetry run python -m llm_session_manager.cli auto-tag $SESSION_ID` |
| `auto-tag <id> --apply` | `poetry run python -m llm_session_manager.cli auto-tag $SESSION_ID --apply` |
| `memory-stats` | `poetry run python -m llm_session_manager.cli memory-stats` |
| `memory-list` | `poetry run python -m llm_session_manager.cli memory-list` |
| `search <query>` | `poetry run python -m llm_session_manager.cli search "bug fix"` |
| `recommend <id>` | `poetry run python -m llm_session_manager.cli recommend $SESSION_ID` |
| `project <id> <name>` | `poetry run python -m llm_session_manager.cli project $SESSION_ID my-app` |
| `list-projects` | `poetry run python -m llm_session_manager.cli list-projects` |
| `describe <id> <text>` | `poetry run python -m llm_session_manager.cli describe $SESSION_ID "Fixed bug"` |
| `describe <id> --show` | `poetry run python -m llm_session_manager.cli describe $SESSION_ID --show` |
| `mcp-config` | `poetry run python -m llm_session_manager.cli mcp-config` |
| `--help` | `poetry run python -m llm_session_manager.cli --help` |
| `<command> --help` | `poetry run python -m llm_session_manager.cli export --help` |

---

## ✅ Success Criteria

All features pass if:
- ✅ No errors during command execution
- ✅ Session IDs are fully visible (not truncated)
- ✅ Export files are created and valid
- ✅ Tags persist across commands
- ✅ Search returns relevant results
- ✅ Monitor dashboard updates in real-time

---

## 🔧 Troubleshooting

**Can't see full session IDs?**
- This has been fixed! Session IDs are now fully visible in the list

**No sessions found?**
- Make sure you have Claude Code, Cursor, or GitHub Copilot running
- Check: `poetry run python -m llm_session_manager.cli discover`

**Database errors?**
- Run migration: `poetry run python migrate_database.py`

**Import errors?**
- Reinstall: `poetry install`

---

**For complete testing documentation, see:** [MANUAL_TESTING_GUIDE.md](MANUAL_TESTING_GUIDE.md)

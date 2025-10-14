# Quick Testing Guide - 5 Minutes

## 🚀 Fastest Way to Test Everything

### **Option 1: Automated Test Suite (Recommended)**

Run the automated test suite:

```bash
cd /Users/gagan/llm-session-manager
./run_all_tests.sh
```

This will:
- ✅ Test all components
- ✅ Test all CLI commands
- ✅ Test export/import
- ✅ Test error handling
- ✅ Give you a pass/fail summary

**Expected runtime:** 2-3 minutes

---

### **Option 2: Manual Quick Test (5 commands)**

If you want to test manually:

```bash
# 1️⃣ List sessions (should show your Claude session)
python -m llm_session_manager.cli list

# 2️⃣ Export a session (copy session ID from above)
python -m llm_session_manager.cli export <SESSION_ID> -o quick.json

# 3️⃣ Import it back (verify data intact)
python -m llm_session_manager.cli import-context quick.json

# 4️⃣ Check health (see detailed breakdown)
python -m llm_session_manager.cli health <SESSION_ID>

# 5️⃣ Run dashboard (press 'q' to quit)
python -m llm_session_manager.cli monitor
```

If all 5 work, you're done! ✅

---

### **Option 3: Component-by-Component**

Test each component individually:

```bash
# Test 1: Session Discovery
python test_discovery.py

# Test 2: Token Estimation
python test_token_estimator.py

# Test 3: Health Monitoring
python test_health_monitor.py

# Test 4: Dashboard
python test_dashboard.py
```

---

## ✅ Success Checklist

After testing, verify:

- [ ] **Discovery works** - Finds your Claude Code session
- [ ] **Tokens counted** - Shows realistic token numbers
- [ ] **Health calculated** - Shows percentage and status
- [ ] **Dashboard displays** - Table with colors and emojis
- [ ] **Export works** - Creates JSON file
- [ ] **Import works** - Reads JSON back
- [ ] **CLI responds** - All commands run without errors

---

## 🐛 Common Issues & Fixes

### Issue: "No sessions found"
**Fix:** Make sure Claude Code is running!

### Issue: "Module not found"
**Fix:** Run from project root directory
```bash
cd /Users/gagan/llm-session-manager
```

### Issue: "Permission denied" errors
**Fix:** This is normal! Token estimator can't read some system files. It's handled gracefully.

### Issue: Dashboard not updating
**Fix:** Press 'r' to force refresh, or restart dashboard

---

## 📊 What Each Test Does

| Test | What It Checks | Time |
|------|----------------|------|
| `test_discovery.py` | Finds running sessions via psutil | 5s |
| `test_token_estimator.py` | Counts tokens in files | 10s |
| `test_health_monitor.py` | Calculates health scores | 5s |
| `test_dashboard.py` | Renders TUI dashboard | 10s |
| `cli list` | End-to-end CLI workflow | 5s |
| `cli export` | JSON serialization | 5s |
| `cli import` | JSON deserialization | 2s |
| `cli health` | Health reporting | 5s |
| `cli monitor` | Interactive dashboard | Manual |

**Total:** ~50 seconds (automated)

---

## 🎯 One-Liner Test

The absolute fastest test:

```bash
python -m llm_session_manager.cli list && echo "✅ WORKING!"
```

If you see your sessions listed, everything is working!

---

## 📝 Expected Output Examples

### **Good Output (Success):**
```
Active Sessions (2)
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━┓
┃ ID             ┃ Type        ┃  PID ┃ Status ┃ Durat ┃ Tokens ┃ Health┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━┩
│ claude_code... │ claude_code │28373 │ active │ 11h   │ 32,068 │ ✅ 86%│
└────────────────┴─────────────┴──────┴────────┴───────┴────────┴───────┘
```

### **Bad Output (Problem):**
```
Traceback (most recent call last):
  File "...", line X, in <module>
    ...
ModuleNotFoundError: No module named 'llm_session_manager'
```

**Fix:** Run from correct directory!

---

## 🚦 Test Status Indicators

- ✅ **Green** - Test passed, everything working
- ⚠️ **Yellow** - Warning, but not critical
- ❌ **Red** - Test failed, needs attention
- ⏭️ **Skipped** - Test skipped (e.g., no sessions found)

---

## 📞 Need More Help?

For detailed testing instructions, see:
- **TESTING_GUIDE.md** - Complete step-by-step guide (20 tests)
- **CLI_GUIDE.md** - All CLI commands with examples
- **DASHBOARD_FEATURES.md** - Dashboard features and usage

---

## ✨ Quick Win!

Want to see something cool immediately?

```bash
python -m llm_session_manager.cli monitor
```

Press 'q' to quit when done!

This shows the live dashboard with:
- 🖥️ Real-time session monitoring
- 📊 Token usage bars
- ❤️ Health indicators
- ⏱️ Duration tracking
- 🔄 Auto-refresh every 5 seconds

**Try it now!** 🎉

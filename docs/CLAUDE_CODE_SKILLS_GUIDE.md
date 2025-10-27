# Claude Code Skills Guide

This guide explains how to use the custom Claude Code skills and slash commands created for LLM Session Manager.

## Table of Contents
- [What are Skills?](#what-are-skills)
- [What are Slash Commands?](#what-are-slash-commands)
- [Available Skills](#available-skills)
- [Available Slash Commands](#available-slash-commands)
- [Creating Custom Skills](#creating-custom-skills)

## What are Skills?

Skills are reusable, specialized mini-agents that perform specific tasks. They're stored in `.claude/skills/` and provide detailed instructions for complex operations.

**Key Features:**
- **Specialized**: Each skill focuses on one domain
- **Reusable**: Invoke anytime you need that capability
- **Configurable**: Customize behavior via prompts
- **Powerful**: Access to all Claude Code tools

## What are Slash Commands?

Slash commands are quick shortcuts that expand into detailed prompts. They're stored in `.claude/commands/` and provide instant access to common workflows.

**Key Features:**
- **Quick**: Type `/command-name` to invoke
- **Consistent**: Same workflow every time
- **Shareable**: Team members use same commands
- **Simple**: Just markdown files

## Available Skills

### 1. Session Analysis Skill

**File:** `.claude/skills/session-analysis.md`

**Purpose:** Analyze LLM coding sessions with AI-powered insights

**When to Use:**
- Need detailed session analysis
- Want AI recommendations
- Comparing sessions
- Troubleshooting issues

**Example Usage:**
```
You: Analyze session 65260

Claude: I'll use the session-analysis skill to provide a comprehensive analysis.

[Uses skill to:]
1. Get session health
2. Run AI insights
3. Compare with similar sessions
4. Provide recommendations

📊 Session Analysis: 65260
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 OVERVIEW
  • Type: Claude Code
  • Duration: 2h 15m
  • Health Score: 85%

📈 METRICS
  • Tokens: 78,432/100,000 (78%)
  • Errors: 3
  • Activity: High

🧠 AI INSIGHTS
  • Similar to 12 past sessions
  • Average lifespan: 2.5 hours

💡 RECOMMENDATIONS
  1. Start fresh at 80% tokens
  2. Review authentication errors
  3. Export context now
```

**Capabilities:**
- Health score breakdown
- Token usage trends
- Error pattern analysis
- AI-powered recommendations
- Historical comparison
- Team insights

### 2. Monitoring Skill

**File:** `.claude/skills/monitoring.md`

**Purpose:** Real-time session monitoring with alerts

**When to Use:**
- Need continuous monitoring
- Want automated alerts
- Tracking multiple sessions
- Preventing issues before they occur

**Example Usage:**
```
You: Monitor my active sessions

Claude: I'll use the monitoring skill to watch your sessions.

🎯 Active Session Monitor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SESSION: claude_code_65260
├─ Status: 🟡 WARNING
├─ Tokens: 78,432 / 100,000 (78%)
├─ Health: 72%
├─ Duration: 2h 15m
└─ ⚠️ Consider starting fresh at 80%

[Updates every 5 minutes]

⚠️ TOKEN ALERT: Session 65260
Token usage: 80,000 / 100,000 (80%)
Recommended: Plan to start fresh soon
```

**Alert Levels:**
- 🟢 Healthy (80-100%)
- 🟡 Warning (60-79%)
- 🔴 Critical (<60%)
- ⚫ Inactive

**Thresholds:**
- Token: 75%, 85%, 95%
- Health: <70%
- Errors: >5 in 10 min
- Duration: >3 hours

### 3. Documentation Generator Skill

**File:** `.claude/skills/doc-generator.md`

**Purpose:** Auto-generate and maintain documentation

**When to Use:**
- Added new features
- Need API docs updated
- Want user guides created
- Maintaining changelog

**Example Usage:**
```
You: Update the documentation for the new export feature

Claude: I'll use the doc-generator skill to update docs.

[Analyzes code:]
- Found new export formats in cli.py
- Detected new API endpoint: /api/export
- Identified user-facing changes

[Updates:]
✅ Updated CLI.md with new export command
✅ Updated API.md with /api/export endpoint
✅ Added example usage to README.md
✅ Updated CHANGELOG.md with new feature

📝 Documentation Updated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Files modified:
- docs/CLI.md (added export formats)
- docs/API.md (new endpoint documented)
- README.md (updated examples)
- CHANGELOG.md (version 0.3.1 entry)
```

**Documentation Types:**
- API Reference
- CLI Commands
- User Guides
- Architecture Docs
- Changelog Entries

## Available Slash Commands

### 1. /start-dev

**File:** `.claude/commands/start-dev.md`

**Purpose:** Start complete development environment

**Usage:**
```
/start-dev
```

**What it does:**
1. Kills running backend processes
2. Checks environment variables
3. Starts backend (port 8000)
4. Starts frontend (port 3000)
5. Verifies both are running
6. Displays access URLs

**Example Output:**
```
🚀 Starting Development Environment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Backend started
   URL: http://localhost:8000
   Health: http://localhost:8000/health

✅ Frontend started
   URL: http://localhost:3000

🎉 Ready to develop!
```

### 2. /test-all

**File:** `.claude/commands/test-all.md`

**Purpose:** Run complete test suite

**Usage:**
```
/test-all
```

**What it does:**
1. Runs backend pytest tests
2. Runs CLI tests
3. Runs integration tests
4. Shows coverage report
5. Summarizes results

**Example Output:**
```
🧪 Running Test Suite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend Tests:
  ✅ 42/42 passed
  📊 Coverage: 87%
  ⏱️  Time: 12.3s

CLI Tests:
  ✅ 18/18 passed
  📊 Coverage: 92%
  ⏱️  Time: 5.1s

Integration Tests:
  ✅ 8/8 passed
  ⏱️  Time: 8.7s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 68/68 passed (100%)
Overall Coverage: 89%
Total Time: 26.1s

🎉 All tests passed!
```

### 3. /deploy-check

**File:** `.claude/commands/deploy-check.md`

**Purpose:** Comprehensive deployment readiness check

**Usage:**
```
/deploy-check
```

**What it does:**
1. Checks environment variables
2. Verifies dependencies
3. Runs linting
4. Runs type checking
5. Runs tests
6. Checks database migrations
7. Validates frontend build
8. Scans for security issues

**Example Output:**
```
🚀 DEPLOYMENT READINESS CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Environment Variables
✅ Dependencies
✅ Tests (68/68 passed)
✅ Type Checking
✅ Frontend Build
⚠️  Security (1 warning)
❌ Database Migrations (1 pending)

OVERALL: ⚠️  NEEDS ATTENTION

BLOCKERS:
1. Run migration: alembic upgrade head

WARNINGS:
1. Update 'requests' package (CVE-2023-xxxxx)

READY TO DEPLOY: No
```

### 4. /analyze-session

**File:** `.claude/commands/analyze-session.md`

**Purpose:** Shortcut to analyze a session

**Usage:**
```
/analyze-session
```

**What it does:**
1. Lists available sessions (if no ID provided)
2. Invokes session-analysis skill
3. Provides comprehensive analysis

### 5. /monitor-sessions

**File:** `.claude/commands/monitor-sessions.md`

**Purpose:** Start real-time monitoring

**Usage:**
```
/monitor-sessions
```

**What it does:**
1. Lists active sessions
2. Starts continuous monitoring
3. Alerts on thresholds
4. Provides periodic updates

**Options:**
```
/monitor-sessions --interval 60    # Update every 60s
/monitor-sessions --session-id 65260  # Monitor specific session
```

### 6. /update-docs

**File:** `.claude/commands/update-docs.md`

**Purpose:** Update project documentation

**Usage:**
```
/update-docs
/update-docs --api          # Update API docs only
/update-docs --cli          # Update CLI docs only
/update-docs --changelog    # Update changelog only
```

**What it does:**
1. Detects changes (via git diff)
2. Updates relevant documentation
3. Validates links and examples
4. Provides summary of changes

## Creating Custom Skills

### Skill Template

Create a new file in `.claude/skills/your-skill.md`:

```markdown
# Your Skill Name

You are a [domain] expert for the LLM Session Manager project.

## Purpose
[What this skill does]

## When to Use
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

## Available Tools
- **Bash**: [What you'll use it for]
- **Read**: [What you'll use it for]
- **Write**: [What you'll use it for]

## Workflow

### 1. Step One
[Detailed instructions]
```bash
# Example commands
poetry run python -m llm_session_manager.cli command
```

### 2. Step Two
[More instructions]

## Output Format
[Expected output structure]

## Error Handling
- [Error scenario 1]: [How to handle]
- [Error scenario 2]: [How to handle]

## Examples

**Example 1: [Name]**
```
User: [Request]
→ [What you do]
→ [Result]
```
```

### Slash Command Template

Create a new file in `.claude/commands/your-command.md`:

```markdown
Brief description of what this command does.

Steps:
1. First step
2. Second step
3. Third step

Provide clear output with:
- Status of each step
- Any errors or warnings
- Final summary

Use emojis for visual feedback.
```

## Best Practices

### For Skills:
1. **Be Specific**: Clear, detailed instructions
2. **Include Examples**: Show expected usage
3. **Handle Errors**: Account for failure cases
4. **Format Output**: Consistent, readable results
5. **Use Tools Wisely**: Choose right tool for job

### For Slash Commands:
1. **Keep Simple**: Short, focused tasks
2. **Clear Steps**: Numbered, sequential
3. **Expected Output**: Define what user sees
4. **Error Handling**: What to do if fails
5. **Quick to Execute**: < 2 minutes

## Tips

**Invoking Skills:**
- Skills activate when you describe their use case
- Be specific: "Use the session-analysis skill"
- Skills can call other skills

**Using Slash Commands:**
- Type `/` to see available commands
- Commands expand into full prompts
- Can be chained in conversation

**Combining Skills & Commands:**
- Use commands for quick operations
- Use skills for complex analysis
- Chain them: `/test-all` then analyze results with skill

## Examples

### Complex Workflow
```
You: /start-dev

Claude: [Starts dev environment]

You: Now run the tests and analyze the results

Claude: [Uses /test-all command]
       [Uses session-analysis skill for detailed breakdown]
```

### Team Collaboration
```
You: Monitor sessions and alert me if health drops below 70%

Claude: [Uses monitoring skill]
        [Sets custom threshold]
        [Provides real-time updates]
```

### Documentation Workflow
```
You: I added a new feature. Update the docs and create a changelog entry.

Claude: [Uses doc-generator skill]
        [Analyzes new code]
        [Updates multiple doc files]
        [Adds changelog entry]
        [Validates all changes]
```

## Next Steps

1. **Try the skills**: Experiment with each one
2. **Create custom skills**: For your specific needs
3. **Share with team**: Standardize workflows
4. **Iterate**: Improve based on usage

---

**Skills make Claude Code more powerful!** 🚀

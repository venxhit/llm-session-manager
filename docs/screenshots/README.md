# Screenshots for README

This directory contains screenshots used in the main README.md.

## Required Screenshots

To complete the README, take the following screenshots:

### 1. monitoring-dashboard.png
**What to capture:**
- Run: `poetry run python -m llm_session_manager.cli monitor`
- Show the real-time TUI dashboard with:
  - Multiple active sessions
  - Token counts and percentages
  - Health scores with color coding
  - Session durations

**Recommended tool:** [terminalizer](https://github.com/faressoft/terminalizer) or screenshot tool

### 2. collaboration-ui.png
**What to capture:**
- Start backend and frontend
- Open: http://localhost:3000
- Show collaborative session with:
  - Live chat messages
  - User presence indicators
  - Session metrics panel
  - Real-time cursor tracking (if possible)

**Recommended tool:** Browser screenshot or [OBS Studio](https://obsproject.com/)

### 3. ai-insights.png
**What to capture:**
- Run: `poetry run python -m llm_session_manager.cli insights <session-id>`
- Show AI-powered recommendations:
  - Pattern analysis
  - Smart suggestions
  - Historical comparisons
  - Health warnings

**Recommended tool:** Terminal screenshot

## Optional Screenshots

### 4. session-list.png
- Run: `poetry run python -m llm_session_manager.cli list`
- Shows all active sessions in a table

### 5. health-breakdown.png
- Run: `poetry run python -m llm_session_manager.cli health <session-id>`
- Shows detailed health metrics breakdown

### 6. export-example.png
- Run: `poetry run python -m llm_session_manager.cli export <session-id> --format json`
- Show exported JSON output

## Screenshot Guidelines

- **Resolution:** At least 1200px wide for clarity
- **Format:** PNG with transparency where applicable
- **Theme:** Dark theme preferred (matches developer audience)
- **Text:** Ensure text is readable at normal zoom levels
- **File size:** Optimize with tools like [TinyPNG](https://tinypng.com/)

## Adding Screenshots to README

Once you have the screenshots:

1. Save them in this directory (`docs/screenshots/`)
2. Verify the filenames match those referenced in README.md:
   - `monitoring-dashboard.png`
   - `collaboration-ui.png`
   - `ai-insights.png`
3. Test that images display correctly in GitHub markdown preview
4. Commit and push

## Tools Recommendations

### For Terminal Screenshots
- **macOS:** Built-in Screenshot (Cmd+Shift+4)
- **Linux:** [Flameshot](https://flameshot.org/)
- **Windows:** [ShareX](https://getsharex.com/)
- **Cross-platform:** [Terminalizer](https://github.com/faressoft/terminalizer) (for animated GIFs)

### For Web UI Screenshots
- **Browser DevTools:** Firefox/Chrome screenshot feature
- **Full-page:** [GoFullPage extension](https://gofullpage.com/)
- **Annotated:** [Annotely](https://annotely.com/)

### For GIFs (Optional)
- **macOS:** [Kap](https://getkap.co/)
- **Windows/Linux:** [ScreenToGif](https://www.screentogif.com/)
- **Cross-platform:** [LICEcap](https://www.cockos.com/licecap/)

## Quick Capture Script

```bash
#!/bin/bash
# Save as: capture_screenshots.sh

echo "Starting screenshot capture process..."

# 1. Start the CLI monitor in background
echo "1. Take screenshot of CLI monitor"
poetry run python -m llm_session_manager.cli monitor &
MONITOR_PID=$!
sleep 3
echo "   → Screenshot terminal now and save as monitoring-dashboard.png"
read -p "   → Press Enter when done..."
kill $MONITOR_PID

# 2. Start backend and frontend
echo "2. Take screenshot of web UI"
echo "   → Start backend: cd backend && uvicorn app.main:app"
echo "   → Start frontend: cd frontend && npm run dev"
echo "   → Open http://localhost:3000"
read -p "   → Press Enter when screenshot is saved as collaboration-ui.png..."

# 3. Show AI insights
echo "3. Take screenshot of AI insights"
poetry run python -m llm_session_manager.cli insights cursor_cli
echo "   → Screenshot terminal now and save as ai-insights.png"
read -p "   → Press Enter when done..."

echo "Screenshots complete! Check docs/screenshots/"
```

## Notes

- Remove the placeholder text from README.md once real screenshots are added
- Update this README if you add more screenshots
- Consider adding animated GIFs for dynamic features like real-time updates

Start real-time monitoring of all active sessions.

This command invokes the monitoring skill to watch sessions continuously.

Steps:
1. List all active sessions
2. Start monitoring mode with real-time updates
3. Alert on threshold breaches (tokens, health, errors)
4. Provide periodic status updates
5. Continue until user stops (Ctrl+C)

The monitoring should include:
- Real-time token usage tracking
- Health score monitoring
- Error rate detection
- Duration tracking
- Predictive alerts

Use the monitoring skill for detailed implementation.

Options to support:
- --interval: Update frequency (default 5 minutes)
- --session-id: Monitor specific session only
- --threshold: Custom alert thresholds

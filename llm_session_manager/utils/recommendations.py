"""Smart recommendations engine for session management."""

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
import structlog

from ..models import Session, SessionStatus

logger = structlog.get_logger()


class RecommendationEngine:
    """Provides intelligent recommendations for session management.

    Analyzes sessions and suggests actions like:
    - Merging similar sessions
    - Restarting unhealthy sessions
    - Closing idle sessions
    - Switching to different sessions
    """

    # Thresholds for recommendations
    HIGH_TOKEN_USAGE = 0.85  # 85% token usage
    CRITICAL_TOKEN_USAGE = 0.95  # 95% token usage
    LOW_HEALTH = 0.50  # 50% health score
    CRITICAL_HEALTH = 0.30  # 30% health score
    IDLE_THRESHOLD_MINUTES = 30  # Consider idle after 30 minutes

    def __init__(self):
        """Initialize recommendation engine."""
        self.logger = structlog.get_logger()

    def analyze_sessions(self, sessions: List[Session]) -> List[Dict[str, Any]]:
        """Analyze all sessions and generate recommendations.

        Args:
            sessions: List of Session objects to analyze.

        Returns:
            List of recommendation dictionaries with:
                - type: str (restart, close, merge, switch, warning)
                - priority: str (high, medium, low)
                - session_ids: List[str]
                - message: str
                - reason: str
        """
        recommendations = []

        # Analyze each session individually
        for session in sessions:
            recommendations.extend(self._analyze_single_session(session))

        # Analyze relationships between sessions
        recommendations.extend(self._analyze_session_relationships(sessions))

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r["priority"], 3))

        return recommendations

    def _analyze_single_session(self, session: Session) -> List[Dict[str, Any]]:
        """Analyze a single session for issues.

        Args:
            session: Session to analyze.

        Returns:
            List of recommendations for this session.
        """
        recommendations = []

        # Token usage warnings
        token_pct = session.calculate_token_usage_percent() / 100
        if token_pct >= self.CRITICAL_TOKEN_USAGE:
            recommendations.append({
                "type": "restart",
                "priority": "high",
                "session_ids": [session.id],
                "message": f"Session approaching token limit ({token_pct:.0%})",
                "reason": "Critical token usage - restart recommended to avoid context loss",
                "action": f"Start a new session and export context from {session.id[:20]}"
            })
        elif token_pct >= self.HIGH_TOKEN_USAGE:
            recommendations.append({
                "type": "warning",
                "priority": "medium",
                "session_ids": [session.id],
                "message": f"High token usage ({token_pct:.0%})",
                "reason": "Consider wrapping up or exporting context soon",
                "action": "Plan to start a new session within next hour"
            })

        # Health score warnings
        health_score = session.health_score / 100
        if health_score <= self.CRITICAL_HEALTH:
            recommendations.append({
                "type": "restart",
                "priority": "high",
                "session_ids": [session.id],
                "message": f"Critical health score ({health_score:.0%})",
                "reason": f"Session has {session.error_count} errors and poor health metrics",
                "action": "Restart session immediately"
            })
        elif health_score <= self.LOW_HEALTH:
            recommendations.append({
                "type": "warning",
                "priority": "medium",
                "session_ids": [session.id],
                "message": f"Low health score ({health_score:.0%})",
                "reason": "Session may be experiencing issues",
                "action": "Monitor closely or consider restarting"
            })

        # Idle session detection
        idle_time = datetime.now() - session.last_activity
        if idle_time > timedelta(minutes=self.IDLE_THRESHOLD_MINUTES):
            idle_hours = idle_time.total_seconds() / 3600
            if idle_hours >= 2:
                recommendations.append({
                    "type": "close",
                    "priority": "low",
                    "session_ids": [session.id],
                    "message": f"Session idle for {idle_hours:.1f} hours",
                    "reason": "Long idle time - consider closing to free resources",
                    "action": "Export context and close session if no longer needed"
                })

        # Error accumulation
        if session.error_count >= 10:
            recommendations.append({
                "type": "restart",
                "priority": "medium",
                "session_ids": [session.id],
                "message": f"High error count ({session.error_count} errors)",
                "reason": "Too many errors - session may be unstable",
                "action": "Restart session with fresh context"
            })

        return recommendations

    def _analyze_session_relationships(self, sessions: List[Session]) -> List[Dict[str, Any]]:
        """Analyze relationships between sessions.

        Args:
            sessions: List of all sessions.

        Returns:
            List of recommendations for session relationships.
        """
        recommendations = []

        if len(sessions) <= 1:
            return recommendations

        # Check for sessions in same project
        project_groups: Dict[str, List[Session]] = {}
        for session in sessions:
            if session.project_name:
                if session.project_name not in project_groups:
                    project_groups[session.project_name] = []
                project_groups[session.project_name].append(session)

        # Recommend merging sessions in same project
        for project, project_sessions in project_groups.items():
            if len(project_sessions) >= 2:
                # Find the healthiest session
                best_session = max(project_sessions, key=lambda s: s.health_score)
                other_sessions = [s for s in project_sessions if s.id != best_session.id]

                recommendations.append({
                    "type": "merge",
                    "priority": "medium",
                    "session_ids": [s.id for s in project_sessions],
                    "message": f"Multiple sessions for project '{project}'",
                    "reason": f"Found {len(project_sessions)} sessions working on same project",
                    "action": f"Consider consolidating into session {best_session.id[:20]} (healthiest)"
                })

        # Check for too many concurrent sessions
        active_sessions = [s for s in sessions if s.status == SessionStatus.ACTIVE]
        if len(active_sessions) >= 5:
            recommendations.append({
                "type": "warning",
                "priority": "medium",
                "session_ids": [s.id for s in active_sessions],
                "message": f"{len(active_sessions)} concurrent active sessions",
                "reason": "Managing many sessions can be overwhelming",
                "action": "Consider closing or consolidating some sessions"
            })

        # Check for sessions with similar tags
        tag_groups: Dict[str, List[Session]] = {}
        for session in sessions:
            for tag in session.tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(session)

        for tag, tag_sessions in tag_groups.items():
            if len(tag_sessions) >= 3:
                recommendations.append({
                    "type": "merge",
                    "priority": "low",
                    "session_ids": [s.id for s in tag_sessions],
                    "message": f"Multiple sessions with tag '#{tag}'",
                    "reason": f"Found {len(tag_sessions)} sessions with similar context",
                    "action": "Consider merging if working on related tasks"
                })

        return recommendations

    def get_best_session_for_task(
        self,
        sessions: List[Session],
        task_tags: List[str] = None,
        project_name: str = None
    ) -> Tuple[Session, str]:
        """Recommend the best session for a new task.

        Args:
            sessions: Available sessions.
            task_tags: Tags related to the task.
            project_name: Project name for the task.

        Returns:
            Tuple of (best_session, reason) or (None, reason) if should start new.
        """
        if not sessions:
            return None, "No active sessions - start a new one"

        candidates = []

        for session in sessions:
            score = 0.0
            reasons = []

            # Health score contributes 40%
            health_factor = session.health_score / 100
            score += health_factor * 0.4
            if health_factor > 0.7:
                reasons.append("healthy")

            # Token availability contributes 30%
            token_available = 1 - (session.calculate_token_usage_percent() / 100)
            score += token_available * 0.3
            if token_available > 0.5:
                reasons.append("low token usage")

            # Project match contributes 20%
            if project_name and session.project_name == project_name:
                score += 0.2
                reasons.append("same project")

            # Tag overlap contributes 10%
            if task_tags and session.tags:
                tag_overlap = len(set(task_tags) & set(session.tags)) / len(task_tags)
                score += tag_overlap * 0.1
                if tag_overlap > 0:
                    reasons.append("matching tags")

            candidates.append((session, score, reasons))

        # Sort by score
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_session, best_score, reasons = candidates[0]

        # Only recommend if score is decent
        if best_score >= 0.5:
            reason_str = ", ".join(reasons) if reasons else "best available"
            return best_session, f"Recommended: {reason_str} (score: {best_score:.1%})"
        else:
            return None, f"Best session score too low ({best_score:.1%}) - start a new session"

    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations as a readable string.

        Args:
            recommendations: List of recommendation dicts.

        Returns:
            Formatted string for display.
        """
        if not recommendations:
            return "✅ No recommendations - all sessions healthy!"

        output = []
        priority_emojis = {"high": "🔴", "medium": "🟡", "low": "🟢"}

        for rec in recommendations:
            emoji = priority_emojis.get(rec["priority"], "ℹ️")
            output.append(f"{emoji} {rec['message'].upper() if rec['priority'] == 'high' else rec['message']}")
            output.append(f"   Reason: {rec['reason']}")
            output.append(f"   Action: {rec['action']}")
            output.append("")

        return "\n".join(output)

"""Health monitoring and scoring system for LLM sessions."""

from datetime import datetime, timedelta
from typing import List, Tuple
import structlog

from ..models import Session

logger = structlog.get_logger()


class HealthMonitor:
    """Monitors and scores the health of LLM sessions.

    Calculates health scores based on token usage, session duration,
    activity level, and error counts. Uses weighted scoring to determine
    overall session health.
    """

    # Health score weights (must sum to 1.0)
    WEIGHT_TOKEN_USAGE = 0.40  # 40% - Token usage impact
    WEIGHT_DURATION = 0.20     # 20% - Session duration impact
    WEIGHT_ACTIVITY = 0.20     # 20% - Recent activity impact
    WEIGHT_ERRORS = 0.20       # 20% - Error count impact

    # Health thresholds
    THRESHOLD_HEALTHY = 0.70   # >= 70% is healthy
    THRESHOLD_WARNING = 0.40   # >= 40% is warning, < 40% is critical

    # Time-based thresholds
    MAX_IDEAL_DURATION = 4 * 60 * 60  # 4 hours in seconds
    MAX_IDLE_TIME = 30 * 60           # 30 minutes in seconds
    WARNING_IDLE_TIME = 15 * 60       # 15 minutes in seconds

    # Token usage thresholds (percentages)
    TOKEN_WARNING_THRESHOLD = 70.0    # Warning at 70% usage
    TOKEN_CRITICAL_THRESHOLD = 90.0   # Critical at 90% usage

    # Error thresholds
    MAX_ACCEPTABLE_ERRORS = 5
    CRITICAL_ERROR_COUNT = 10

    def calculate_health(self, session: Session) -> float:
        """Calculate overall health score for a session.

        Uses weighted formula:
        health = (token_score * 0.4) +
                 (duration_score * 0.2) +
                 (activity_score * 0.2) +
                 (error_score * 0.2)

        Args:
            session: Session to calculate health for.

        Returns:
            Health score between 0.0 (critical) and 1.0 (perfect).
        """
        # Calculate individual component scores
        token_score = self._calculate_token_score(session)
        duration_score = self._calculate_duration_score(session)
        activity_score = self._calculate_activity_score(session)
        error_score = self._calculate_error_score(session)

        # Apply weights and calculate total
        health_score = (
            (token_score * self.WEIGHT_TOKEN_USAGE) +
            (duration_score * self.WEIGHT_DURATION) +
            (activity_score * self.WEIGHT_ACTIVITY) +
            (error_score * self.WEIGHT_ERRORS)
        )

        # Clamp to [0.0, 1.0] range
        health_score = max(0.0, min(1.0, health_score))

        logger.debug(
            "health_calculated",
            session_id=session.id,
            token_score=f"{token_score:.2f}",
            duration_score=f"{duration_score:.2f}",
            activity_score=f"{activity_score:.2f}",
            error_score=f"{error_score:.2f}",
            final_score=f"{health_score:.2f}"
        )

        return health_score

    def _calculate_token_score(self, session: Session) -> float:
        """Calculate health score based on token usage.

        Score decreases as token usage approaches limit:
        - 0-70%: Full score (1.0)
        - 70-90%: Linear decrease (1.0 -> 0.3)
        - 90-100%: Rapid decrease (0.3 -> 0.0)

        Args:
            session: Session to score.

        Returns:
            Score between 0.0 and 1.0.
        """
        if session.token_limit == 0:
            return 1.0

        usage_percent = (session.token_count / session.token_limit) * 100

        if usage_percent < self.TOKEN_WARNING_THRESHOLD:
            # Healthy range: full score
            return 1.0
        elif usage_percent < self.TOKEN_CRITICAL_THRESHOLD:
            # Warning range: linear decrease from 1.0 to 0.3
            range_size = self.TOKEN_CRITICAL_THRESHOLD - self.TOKEN_WARNING_THRESHOLD
            position = usage_percent - self.TOKEN_WARNING_THRESHOLD
            return 1.0 - (position / range_size * 0.7)
        else:
            # Critical range: rapid decrease from 0.3 to 0.0
            range_size = 100 - self.TOKEN_CRITICAL_THRESHOLD
            position = min(usage_percent - self.TOKEN_CRITICAL_THRESHOLD, range_size)
            return 0.3 - (position / range_size * 0.3)

    def _calculate_duration_score(self, session: Session) -> float:
        """Calculate health score based on session duration.

        Longer sessions may have context degradation:
        - 0-4 hours: Full score (1.0)
        - 4-8 hours: Gradual decrease (1.0 -> 0.4)
        - 8+ hours: Low score (0.4 -> 0.1)

        Args:
            session: Session to score.

        Returns:
            Score between 0.0 and 1.0.
        """
        duration = (datetime.now() - session.start_time).total_seconds()

        if duration < self.MAX_IDEAL_DURATION:
            # Ideal duration: full score
            return 1.0
        elif duration < self.MAX_IDEAL_DURATION * 2:
            # Warning range: 4-8 hours
            range_size = self.MAX_IDEAL_DURATION
            position = duration - self.MAX_IDEAL_DURATION
            return 1.0 - (position / range_size * 0.6)
        else:
            # Extended duration: 8+ hours
            range_size = self.MAX_IDEAL_DURATION * 2
            position = min(duration - (self.MAX_IDEAL_DURATION * 2), range_size)
            return 0.4 - (position / range_size * 0.3)

    def _calculate_activity_score(self, session: Session) -> float:
        """Calculate health score based on recent activity.

        Idle sessions get lower scores:
        - Active (< 15 min idle): Full score (1.0)
        - Warning (15-30 min idle): Decreased (1.0 -> 0.5)
        - Idle (> 30 min): Low score (0.5 -> 0.2)

        Args:
            session: Session to score.

        Returns:
            Score between 0.0 and 1.0.
        """
        idle_time = (datetime.now() - session.last_activity).total_seconds()

        if idle_time < self.WARNING_IDLE_TIME:
            # Recently active: full score
            return 1.0
        elif idle_time < self.MAX_IDLE_TIME:
            # Warning range: 15-30 minutes
            range_size = self.MAX_IDLE_TIME - self.WARNING_IDLE_TIME
            position = idle_time - self.WARNING_IDLE_TIME
            return 1.0 - (position / range_size * 0.5)
        else:
            # Idle: > 30 minutes
            range_size = self.MAX_IDLE_TIME
            position = min(idle_time - self.MAX_IDLE_TIME, range_size * 2)
            return 0.5 - (position / (range_size * 2) * 0.3)

    def _calculate_error_score(self, session: Session) -> float:
        """Calculate health score based on error count.

        More errors indicate problems:
        - 0-5 errors: Good score (1.0 -> 0.7)
        - 5-10 errors: Warning (0.7 -> 0.3)
        - 10+ errors: Critical (0.3 -> 0.0)

        Args:
            session: Session to score.

        Returns:
            Score between 0.0 and 1.0.
        """
        error_count = session.error_count

        if error_count == 0:
            return 1.0
        elif error_count <= self.MAX_ACCEPTABLE_ERRORS:
            # Acceptable range: 1-5 errors
            return 1.0 - (error_count / self.MAX_ACCEPTABLE_ERRORS * 0.3)
        elif error_count < self.CRITICAL_ERROR_COUNT:
            # Warning range: 6-9 errors
            range_size = self.CRITICAL_ERROR_COUNT - self.MAX_ACCEPTABLE_ERRORS
            position = error_count - self.MAX_ACCEPTABLE_ERRORS
            return 0.7 - (position / range_size * 0.4)
        else:
            # Critical range: 10+ errors
            position = min(error_count - self.CRITICAL_ERROR_COUNT, 10)
            return 0.3 - (position / 10 * 0.3)

    def get_health_status(self, health_score: float) -> str:
        """Get health status label from score.

        Args:
            health_score: Score between 0.0 and 1.0.

        Returns:
            Status string: "healthy", "warning", or "critical".
        """
        if health_score >= self.THRESHOLD_HEALTHY:
            return "healthy"
        elif health_score >= self.THRESHOLD_WARNING:
            return "warning"
        else:
            return "critical"

    def get_health_color(self, health_score: float) -> str:
        """Get color code for health visualization.

        Args:
            health_score: Score between 0.0 and 1.0.

        Returns:
            Color string: "green", "yellow", or "red".
        """
        if health_score >= self.THRESHOLD_HEALTHY:
            return "green"
        elif health_score >= self.THRESHOLD_WARNING:
            return "yellow"
        else:
            return "red"

    def get_health_emoji(self, health_score: float) -> str:
        """Get emoji indicator for health score.

        Args:
            health_score: Score between 0.0 and 1.0.

        Returns:
            Emoji string.
        """
        if health_score >= self.THRESHOLD_HEALTHY:
            return "✅"
        elif health_score >= self.THRESHOLD_WARNING:
            return "⚠️"
        else:
            return "🔴"

    def update_health_scores(self, sessions: List[Session]) -> None:
        """Calculate and update health scores for all sessions.

        Args:
            sessions: List of Session objects to update.
        """
        logger.info("updating_health_scores", session_count=len(sessions))

        for session in sessions:
            old_score = session.health_score
            new_score = self.calculate_health(session)

            # Convert to 0-100 scale for storage
            session.health_score = new_score * 100

            # Log significant changes
            if abs(new_score * 100 - old_score) > 10:
                logger.info(
                    "health_score_changed",
                    session_id=session.id,
                    old_score=f"{old_score:.1f}",
                    new_score=f"{session.health_score:.1f}",
                    status=self.get_health_status(new_score)
                )

    def get_health_summary(self, session: Session) -> dict:
        """Get detailed health summary for a session.

        Args:
            session: Session to analyze.

        Returns:
            Dictionary with health breakdown and recommendations.
        """
        # Calculate individual scores
        token_score = self._calculate_token_score(session)
        duration_score = self._calculate_duration_score(session)
        activity_score = self._calculate_activity_score(session)
        error_score = self._calculate_error_score(session)
        overall_score = self.calculate_health(session)

        # Calculate metrics
        duration = (datetime.now() - session.start_time).total_seconds()
        idle_time = (datetime.now() - session.last_activity).total_seconds()
        token_usage = (session.token_count / session.token_limit * 100) if session.token_limit > 0 else 0

        # Generate recommendations
        recommendations = []

        if token_score < 0.5:
            recommendations.append("Token usage is high. Consider starting a new session.")
        if duration_score < 0.5:
            recommendations.append("Session has been running for a long time. Context may be degraded.")
        if activity_score < 0.5:
            recommendations.append("Session has been idle. Consider closing if no longer needed.")
        if error_score < 0.5:
            recommendations.append("High error count detected. Check for recurring issues.")

        return {
            "overall_score": overall_score,
            "overall_percentage": overall_score * 100,
            "status": self.get_health_status(overall_score),
            "color": self.get_health_color(overall_score),
            "emoji": self.get_health_emoji(overall_score),
            "component_scores": {
                "token": token_score,
                "duration": duration_score,
                "activity": activity_score,
                "errors": error_score,
            },
            "metrics": {
                "duration_hours": duration / 3600,
                "idle_minutes": idle_time / 60,
                "token_usage_percent": token_usage,
                "error_count": session.error_count,
            },
            "recommendations": recommendations,
        }

    def is_session_stale(self, session: Session) -> bool:
        """Check if session appears to be stale/abandoned.

        Args:
            session: Session to check.

        Returns:
            True if session has been idle for extended period.
        """
        idle_time = (datetime.now() - session.last_activity).total_seconds()
        return idle_time > (self.MAX_IDLE_TIME * 2)  # 1 hour

    def should_restart_session(self, session: Session) -> Tuple[bool, str]:
        """Determine if session should be restarted.

        Args:
            session: Session to evaluate.

        Returns:
            Tuple of (should_restart: bool, reason: str).
        """
        health_score = self.calculate_health(session)

        # Critical health
        if health_score < 0.3:
            return True, "Critical health score"

        # Token limit approaching
        token_usage = (session.token_count / session.token_limit * 100) if session.token_limit > 0 else 0
        if token_usage > 95:
            return True, "Token limit nearly exhausted"

        # Too many errors
        if session.error_count >= self.CRITICAL_ERROR_COUNT:
            return True, "Excessive errors encountered"

        # Extended duration with degraded health
        duration = (datetime.now() - session.start_time).total_seconds()
        if duration > (self.MAX_IDEAL_DURATION * 3) and health_score < 0.5:
            return True, "Long-running session with poor health"

        return False, ""

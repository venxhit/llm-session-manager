"""Session Intelligence - AI-powered insights using Cognee."""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import structlog
from datetime import datetime

# Configure Cognee to use local storage
os.environ["COGNEE_DATA_ROOT"] = str(Path.home() / ".llm-session-manager" / "cognee_data")

try:
    import cognee
except ImportError:
    cognee = None
    print("Warning: Cognee not installed. Session intelligence features will be disabled.")

logger = structlog.get_logger()


class SessionIntelligence:
    """AI-powered session insights using Cognee memory."""

    def __init__(self):
        """Initialize session intelligence."""
        self.enabled = cognee is not None
        if self.enabled:
            # Initialize Cognee
            try:
                # Configure Cognee with API key from environment
                api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    # Set Cognee configuration
                    os.environ["LLM_API_KEY"] = api_key

                    # Determine provider
                    if os.getenv("OPENAI_API_KEY"):
                        os.environ["LLM_PROVIDER"] = "openai"
                    elif os.getenv("ANTHROPIC_API_KEY"):
                        os.environ["LLM_PROVIDER"] = "anthropic"

                # Use async wrapper since cognee is async
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                logger.info(
                    "cognee_initialized",
                    data_root=os.environ["COGNEE_DATA_ROOT"],
                    api_key_set=bool(api_key)
                )
            except Exception as e:
                logger.error("cognee_init_failed", error=str(e))
                self.enabled = False

    async def capture_session_learning(self, session) -> bool:
        """
        Capture learnings from a session for future reference.

        Args:
            session: Session object with metrics and data

        Returns:
            bool: True if successful
        """
        if not self.enabled:
            return False

        try:
            # Create context about the session
            context_items = []

            # Basic session info
            context_items.append(
                f"Session {session.id} ({session.type.value}) in project {session.working_directory}"
            )

            # Token usage patterns
            token_percentage = (session.token_count / session.token_limit * 100) if session.token_limit > 0 else 0
            context_items.append(
                f"Token usage: {session.token_count:,} / {session.token_limit:,} ({token_percentage:.1f}%)"
            )

            # Health patterns
            health_status = "healthy" if session.health_score >= 80 else "warning" if session.health_score >= 60 else "critical"
            context_items.append(
                f"Session health: {session.health_score:.0f}% ({health_status})"
            )

            # Activity metrics
            context_items.append(
                f"Activity: {session.message_count} messages, {session.file_count} files, {session.error_count} errors"
            )

            # Duration
            if session.start_time:
                duration = datetime.now() - session.start_time
                hours = duration.total_seconds() / 3600
                context_items.append(f"Session duration: {hours:.1f} hours")

            # Tags and context
            if session.tags:
                context_items.append(f"Tags: {', '.join(session.tags)}")

            # Add all context to Cognee
            for item in context_items:
                await cognee.add(item)

            # Process the data to build knowledge graph
            await cognee.cognify()

            logger.info(
                "session_learning_captured",
                session_id=session.id,
                items_count=len(context_items)
            )
            return True

        except Exception as e:
            logger.error("capture_learning_failed", session_id=session.id, error=str(e))
            return False

    async def get_session_insights(self, current_session) -> Dict[str, any]:
        """
        Get AI-powered insights for a session based on past sessions.

        Args:
            current_session: Current session object

        Returns:
            dict: Insights and recommendations
        """
        if not self.enabled:
            return {
                "enabled": False,
                "warnings": [],
                "recommendations": [],
                "similar_sessions": []
            }

        try:
            insights = {
                "enabled": True,
                "warnings": [],
                "recommendations": [],
                "similar_sessions": []
            }

            # Search for similar error patterns
            if current_session.error_count > 0:
                error_results = await cognee.search(
                    f"errors in {current_session.working_directory}"
                )
                if error_results:
                    insights["warnings"].append({
                        "type": "similar_errors",
                        "message": f"Found {len(error_results)} similar error patterns in past sessions",
                        "details": error_results
                    })

            # Check token usage patterns
            token_percentage = (current_session.token_count / current_session.token_limit * 100) if current_session.token_limit > 0 else 0
            if token_percentage > 70:
                usage_results = await cognee.search(
                    f"token usage {current_session.type.value}",
                    
                )
                if usage_results:
                    insights["recommendations"].append({
                        "type": "token_management",
                        "message": f"Token usage at {token_percentage:.0f}%. Past sessions suggest taking a break around 75%",
                        "details": usage_results
                    })

            # Find similar successful sessions
            if current_session.working_directory:
                similar_results = await cognee.search(
                    f"healthy session {current_session.working_directory}",
                    
                )
                if similar_results:
                    insights["similar_sessions"] = similar_results

            # Project-specific recommendations
            project_results = await cognee.search(
                f"session in {current_session.working_directory}",
                
            )
            if project_results:
                insights["recommendations"].append({
                    "type": "project_insights",
                    "message": f"Found {len(project_results)} past sessions in this project",
                    "details": project_results
                })

            logger.info(
                "session_insights_generated",
                session_id=current_session.id,
                warnings_count=len(insights["warnings"]),
                recommendations_count=len(insights["recommendations"])
            )

            return insights

        except Exception as e:
            logger.error("get_insights_failed", session_id=current_session.id, error=str(e))
            return {
                "enabled": True,
                "error": str(e),
                "warnings": [],
                "recommendations": [],
                "similar_sessions": []
            }

    async def search_team_knowledge(self, query: str, limit: int = 5) -> List[str]:
        """
        Search across all team sessions for specific knowledge.

        Args:
            query: Search query
            limit: Maximum results to return (applied after search)

        Returns:
            list: Search results
        """
        if not self.enabled:
            return []

        try:
            results = await cognee.search(query)
            # Apply limit manually since API doesn't support it
            limited_results = results[:limit] if results else []
            logger.info("team_knowledge_search", query=query, results_count=len(limited_results))
            return limited_results
        except Exception as e:
            logger.error("team_search_failed", query=query, error=str(e))
            return []

    async def get_session_autopsy(self, failed_session) -> Dict[str, any]:
        """
        Analyze a failed or problematic session.

        Args:
            failed_session: Session that failed or had issues

        Returns:
            dict: Analysis and recommendations
        """
        if not self.enabled:
            return {"enabled": False}

        try:
            autopsy = {
                "enabled": True,
                "issues_found": [],
                "possible_causes": [],
                "recommendations": []
            }

            # Analyze errors
            if failed_session.error_count > 0:
                error_patterns = await cognee.search(
                    f"errors and solutions {failed_session.type.value}",
                    
                )
                if error_patterns:
                    autopsy["possible_causes"].extend(error_patterns)

            # Compare to successful sessions
            if failed_session.health_score < 60:
                autopsy["issues_found"].append(f"Low health score: {failed_session.health_score:.0f}%")

                successful_patterns = await cognee.search(
                    f"healthy session {failed_session.type.value}",
                    
                )
                if successful_patterns:
                    autopsy["recommendations"].append({
                        "type": "compare_success",
                        "message": "Compare with successful sessions",
                        "details": successful_patterns
                    })

            # Token exhaustion check
            token_percentage = (failed_session.token_count / failed_session.token_limit * 100) if failed_session.token_limit > 0 else 0
            if token_percentage > 90:
                autopsy["issues_found"].append(f"Token exhaustion: {token_percentage:.0f}%")
                autopsy["recommendations"].append({
                    "type": "token_management",
                    "message": "Session likely failed due to token limit. Consider starting fresh sessions more frequently."
                })

            logger.info(
                "session_autopsy_complete",
                session_id=failed_session.id,
                issues_count=len(autopsy["issues_found"]),
                recommendations_count=len(autopsy["recommendations"])
            )

            return autopsy

        except Exception as e:
            logger.error("autopsy_failed", session_id=failed_session.id, error=str(e))
            return {
                "enabled": True,
                "error": str(e),
                "issues_found": [],
                "possible_causes": [],
                "recommendations": []
            }

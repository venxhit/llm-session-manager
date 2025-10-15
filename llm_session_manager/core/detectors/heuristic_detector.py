"""Heuristic-based AI coding assistant detection.

Uses intelligent patterns and behavior analysis to detect unknown AI tools.
Serves as fallback when registry doesn't match.
"""

import psutil
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import structlog

from ...models import SessionType

logger = structlog.get_logger()


class HeuristicDetector:
    """Detect AI coding assistants using heuristic patterns."""

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize heuristic detector.

        Args:
            registry_path: Path to registry YAML (for heuristic patterns).
        """
        self.logger = logger

        # Load heuristic patterns from registry
        if registry_path is None:
            registry_path = Path(__file__).parent.parent.parent / "config" / "ai_tools_registry.yaml"

        self.heuristics = self._load_heuristics(registry_path)

    def _load_heuristics(self, path: Path) -> Dict[str, Any]:
        """Load heuristic patterns from registry.

        Args:
            path: Path to registry file.

        Returns:
            Heuristics configuration dictionary.
        """
        try:
            with open(path, 'r') as f:
                registry = yaml.safe_load(f)
                return registry.get('heuristics', {})
        except Exception as e:
            self.logger.error("heuristics_load_failed", error=str(e))
            return {}

    def identify_session_type(self, process: psutil.Process) -> Optional[SessionType]:
        """Identify AI assistant using heuristic analysis.

        Args:
            process: psutil.Process object to analyze.

        Returns:
            SessionType if identified, None otherwise.
        """
        try:
            # Get process information
            proc_info = process.info
            proc_name = (proc_info.get('name') or '').lower()
            cmdline = proc_info.get('cmdline') or []
            cmdline_str = ' '.join(cmdline).lower()

            # Check if this looks like an AI coding tool
            if not self._looks_like_ai_tool(proc_name, cmdline_str):
                return None

            # Exclude obvious system processes
            if self._is_system_process(proc_name, cmdline_str):
                return None

            # Score the process
            confidence, tool_type = self._score_process(process, proc_name, cmdline_str)

            if confidence >= 0.6:  # 60% confidence threshold
                self.logger.debug(
                    "heuristic_match",
                    process=proc_name,
                    confidence=confidence,
                    tool_type=tool_type
                )
                return tool_type

            return None

        except Exception as e:
            self.logger.debug("heuristic_detection_failed", error=str(e))
            return None

    def _looks_like_ai_tool(self, proc_name: str, cmdline_str: str) -> bool:
        """Check if process has AI tool indicators.

        Args:
            proc_name: Process name (lowercased).
            cmdline_str: Command line string (lowercased).

        Returns:
            True if process has AI tool characteristics.
        """
        ai_keywords = self.heuristics.get('ai_keywords', [])

        # Check for AI-related keywords
        text = f"{proc_name} {cmdline_str}"
        return any(keyword.lower() in text for keyword in ai_keywords)

    def _is_system_process(self, proc_name: str, cmdline_str: str) -> bool:
        """Check if process is a system process (false positive).

        Args:
            proc_name: Process name (lowercased).
            cmdline_str: Command line string (lowercased).

        Returns:
            True if process is a system process.
        """
        exclude_patterns = self.heuristics.get('exclude_system_processes', [])

        text = f"{proc_name} {cmdline_str}"
        return any(pattern.lower() in text for pattern in exclude_patterns)

    def _score_process(
        self,
        process: psutil.Process,
        proc_name: str,
        cmdline_str: str
    ) -> Tuple[float, SessionType]:
        """Score process likelihood of being an AI tool.

        Args:
            process: psutil.Process object.
            proc_name: Process name (lowercased).
            cmdline_str: Command line string (lowercased).

        Returns:
            Tuple of (confidence_score, likely_session_type).
        """
        score = 0.0
        weights = {
            'ai_keywords': 0.3,
            'tech_stack': 0.2,
            'memory_usage': 0.15,
            'network_activity': 0.15,
            'file_patterns': 0.2,
        }

        # Check AI keywords (weighted)
        ai_keywords = self.heuristics.get('ai_keywords', [])
        keyword_matches = sum(1 for kw in ai_keywords if kw.lower() in f"{proc_name} {cmdline_str}")
        if keyword_matches > 0:
            score += weights['ai_keywords'] * min(keyword_matches / len(ai_keywords), 1.0)

        # Check tech stack indicators
        tech_indicators = self.heuristics.get('tech_indicators', [])
        tech_matches = sum(1 for tech in tech_indicators if tech.lower() in cmdline_str)
        if tech_matches > 0:
            score += weights['tech_stack'] * min(tech_matches / len(tech_indicators), 1.0)

        # Check memory usage (AI tools typically use significant memory)
        try:
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            min_memory = self.heuristics.get('behavior_patterns', {}).get('min_memory_mb', 50)

            if memory_mb >= min_memory:
                score += weights['memory_usage']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        # Check network activity (AI tools make API calls)
        try:
            connections = process.connections()
            if len(connections) > 0:
                score += weights['network_activity']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        # Determine likely tool type based on keywords
        tool_type = self._infer_tool_type(proc_name, cmdline_str)

        return (score, tool_type)

    def _infer_tool_type(self, proc_name: str, cmdline_str: str) -> SessionType:
        """Infer likely tool type from process characteristics.

        Args:
            proc_name: Process name (lowercased).
            cmdline_str: Command line string (lowercased).

        Returns:
            Most likely SessionType.
        """
        text = f"{proc_name} {cmdline_str}"

        # Simple keyword-based inference
        if 'claude' in text:
            return SessionType.CLAUDE_CODE
        elif 'cursor' in text:
            return SessionType.CURSOR_CLI
        elif 'copilot' in text:
            return SessionType.GITHUB_COPILOT
        else:
            return SessionType.UNKNOWN

    def get_confidence_explanation(
        self,
        process: psutil.Process
    ) -> Dict[str, Any]:
        """Get detailed explanation of confidence score.

        Args:
            process: psutil.Process to analyze.

        Returns:
            Dictionary with scoring breakdown.
        """
        try:
            proc_info = process.info
            proc_name = (proc_info.get('name') or '').lower()
            cmdline = proc_info.get('cmdline') or []
            cmdline_str = ' '.join(cmdline).lower()

            confidence, tool_type = self._score_process(process, proc_name, cmdline_str)

            return {
                'confidence': confidence,
                'likely_type': tool_type.value if tool_type else 'unknown',
                'process_name': proc_name,
                'indicators': {
                    'has_ai_keywords': self._looks_like_ai_tool(proc_name, cmdline_str),
                    'is_system_process': self._is_system_process(proc_name, cmdline_str),
                }
            }

        except Exception as e:
            return {'error': str(e)}

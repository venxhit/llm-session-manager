"""Hybrid detection orchestrator.

Combines registry, heuristic, and optional LLM detection for maximum accuracy.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import structlog
import psutil

from ...models import SessionType
from .registry_detector import RegistryDetector
from .heuristic_detector import HeuristicDetector
from .llm_detector import LLMDetector

logger = structlog.get_logger()


class HybridDetector:
    """Orchestrates multiple detection strategies for optimal results."""

    def __init__(
        self,
        registry_path: Optional[Path] = None,
        enable_llm: bool = False,
        llm_provider: str = "ollama",
        llm_model: str = "llama3.2"
    ):
        """Initialize hybrid detector.

        Args:
            registry_path: Path to registry YAML.
            enable_llm: Whether to enable LLM fallback (opt-in).
            llm_provider: LLM provider for fallback detection.
            llm_model: LLM model name.
        """
        self.logger = logger

        # Initialize detectors
        self.registry = RegistryDetector(registry_path)
        self.heuristic = HeuristicDetector(registry_path)
        self.llm = LLMDetector(llm_provider, llm_model, enable_llm) if enable_llm else None

        self.stats = {
            'registry_matches': 0,
            'heuristic_matches': 0,
            'llm_matches': 0,
            'total_processes': 0,
        }

        self.logger.info(
            "hybrid_detector_initialized",
            registry_tools=len(self.registry.tools),
            llm_enabled=enable_llm
        )

    def identify_session_type(self, process: psutil.Process) -> Optional[SessionType]:
        """Identify AI assistant using hybrid strategy.

        Strategy:
        1. Try registry first (fast, accurate for known tools)
        2. Fall back to heuristics (for unknown but likely AI tools)
        3. Fall back to LLM if enabled (for complete unknowns)

        Args:
            process: psutil.Process object to analyze.

        Returns:
            SessionType if identified, None otherwise.
        """
        self.stats['total_processes'] += 1

        try:
            # Strategy 1: Registry-based detection (fastest)
            result = self.registry.identify_session_type(process)
            if result is not None:
                self.stats['registry_matches'] += 1
                self.logger.debug(
                    "detection_via_registry",
                    session_type=result.value,
                    pid=process.info.get('pid')
                )
                return result

            # Strategy 2: Heuristic detection (medium speed)
            result = self.heuristic.identify_session_type(process)
            if result is not None:
                self.stats['heuristic_matches'] += 1
                self.logger.debug(
                    "detection_via_heuristic",
                    session_type=result.value,
                    pid=process.info.get('pid')
                )
                return result

            # Strategy 3: LLM fallback (slowest, opt-in only)
            if self.llm and self.llm.enabled:
                # Only use LLM for promising candidates
                if self._should_use_llm(process):
                    result = self.llm.identify_session_type(process)
                    if result is not None:
                        self.stats['llm_matches'] += 1
                        self.logger.info(
                            "detection_via_llm",
                            session_type=result.value,
                            pid=process.info.get('pid')
                        )
                        return result

            return None

        except Exception as e:
            self.logger.debug("hybrid_detection_failed", error=str(e))
            return None

    def _should_use_llm(self, process: psutil.Process) -> bool:
        """Determine if LLM should be used for this process.

        Only use LLM for processes that look promising (has AI keywords).
        Avoid wasting API calls on obvious non-AI processes.

        Args:
            process: psutil.Process to evaluate.

        Returns:
            True if LLM analysis is warranted.
        """
        try:
            proc_info = process.info
            proc_name = (proc_info.get('name') or '').lower()
            cmdline = proc_info.get('cmdline') or []
            cmdline_str = ' '.join(cmdline).lower()

            # Check for AI-related keywords
            ai_keywords = [
                'ai', 'llm', 'gpt', 'claude', 'copilot', 'cursor',
                'assistant', 'chat', 'code', 'completion', 'windsurf',
                'aider', 'codeium', 'tabnine', 'continue'
            ]

            text = f"{proc_name} {cmdline_str}"
            return any(keyword in text for keyword in ai_keywords)

        except Exception:
            return False

    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics.

        Returns:
            Dictionary with detection statistics.
        """
        total = self.stats['total_processes']
        if total == 0:
            return self.stats

        return {
            **self.stats,
            'registry_percentage': (self.stats['registry_matches'] / total) * 100,
            'heuristic_percentage': (self.stats['heuristic_matches'] / total) * 100,
            'llm_percentage': (self.stats['llm_matches'] / total) * 100,
        }

    def list_supported_tools(self) -> Dict[str, Any]:
        """Get information about supported tools.

        Returns:
            Dictionary with supported tools and detection capabilities.
        """
        return {
            'registry_tools': self.registry.list_supported_tools(),
            'heuristic_enabled': True,
            'llm_enabled': self.llm.enabled if self.llm else False,
            'llm_provider': self.llm.provider if self.llm else None,
        }

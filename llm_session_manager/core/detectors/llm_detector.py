"""LLM-powered AI coding assistant detection.

Optional fallback that uses a local or cloud LLM to identify unknown tools.
Disabled by default for privacy and performance.
"""

import json
from typing import Optional, Dict, Any
import structlog
import psutil

from ...models import SessionType

logger = structlog.get_logger()


class LLMDetector:
    """Detect AI assistants using LLM analysis (optional, opt-in)."""

    def __init__(self, provider: str = "ollama", model: str = "llama3.2", enabled: bool = False):
        """Initialize LLM detector.

        Args:
            provider: LLM provider ('ollama', 'anthropic', 'openai').
            model: Model name to use.
            enabled: Whether LLM detection is enabled (opt-in).
        """
        self.logger = logger
        self.provider = provider
        self.model = model
        self.enabled = enabled
        self.client = None

        if self.enabled:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize LLM client based on provider."""
        try:
            if self.provider == "ollama":
                # Local Ollama - privacy-preserving
                try:
                    import requests
                    # Check if Ollama is running
                    response = requests.get("http://localhost:11434/api/tags")
                    if response.status_code == 200:
                        self.client = "ollama"
                        self.logger.info("llm_detector_initialized", provider="ollama")
                    else:
                        self.logger.warning("ollama_not_running")
                        self.enabled = False
                except Exception as e:
                    self.logger.warning("ollama_connection_failed", error=str(e))
                    self.enabled = False

            elif self.provider == "anthropic":
                # Cloud API - requires opt-in
                try:
                    import anthropic
                    # User must set ANTHROPIC_API_KEY
                    self.client = anthropic.Anthropic()
                    self.logger.info("llm_detector_initialized", provider="anthropic")
                except Exception as e:
                    self.logger.error("anthropic_init_failed", error=str(e))
                    self.enabled = False

            # Add more providers as needed

        except Exception as e:
            self.logger.error("llm_client_init_failed", error=str(e))
            self.enabled = False

    def identify_session_type(self, process: psutil.Process) -> Optional[SessionType]:
        """Identify AI assistant using LLM analysis.

        Args:
            process: psutil.Process object to analyze.

        Returns:
            SessionType if identified, None otherwise.
        """
        if not self.enabled or not self.client:
            return None

        try:
            # Get process information
            proc_info = process.info
            proc_name = proc_info.get('name') or ''
            cmdline = proc_info.get('cmdline') or []
            cmdline_str = ' '.join(cmdline)

            # Query LLM
            result = self._query_llm(proc_name, cmdline_str)

            if result and result.get('is_ai_assistant') and not result.get('is_helper_process'):
                tool_name = result.get('tool_name', 'unknown')
                confidence = result.get('confidence', 0.0)

                if confidence >= 0.7:  # 70% confidence threshold
                    self.logger.info(
                        "llm_detection_success",
                        process=proc_name,
                        tool=tool_name,
                        confidence=confidence
                    )
                    return self._map_tool_to_session_type(tool_name)

            return None

        except Exception as e:
            self.logger.debug("llm_detection_failed", error=str(e))
            return None

    def _query_llm(self, proc_name: str, cmdline_str: str) -> Optional[Dict[str, Any]]:
        """Query LLM to classify process.

        Args:
            proc_name: Process name.
            cmdline_str: Command line string.

        Returns:
            Classification result dictionary or None.
        """
        prompt = f"""Analyze this process and determine if it's an AI coding assistant:

Process Name: {proc_name}
Command Line: {cmdline_str}

Is this an AI coding assistant (like Claude Code, Cursor, GitHub Copilot, Windsurf, Aider, etc.)?

Respond ONLY with valid JSON in this exact format:
{{
    "is_ai_assistant": true or false,
    "tool_name": "claude_code" or "cursor" or "copilot" or "unknown",
    "is_helper_process": true or false,
    "confidence": 0.0 to 1.0
}}"""

        try:
            if self.provider == "ollama":
                return self._query_ollama(prompt)
            elif self.provider == "anthropic":
                return self._query_anthropic(prompt)
            return None

        except Exception as e:
            self.logger.error("llm_query_failed", error=str(e))
            return None

    def _query_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query local Ollama instance.

        Args:
            prompt: Prompt text.

        Returns:
            Parsed JSON response or None.
        """
        try:
            import requests

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False}
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')

                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))

            return None

        except Exception as e:
            self.logger.error("ollama_query_failed", error=str(e))
            return None

    def _query_anthropic(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query Anthropic Claude API.

        Args:
            prompt: Prompt text.

        Returns:
            Parsed JSON response or None.
        """
        # Placeholder - implement if needed
        self.logger.warning("anthropic_not_implemented")
        return None

    def _map_tool_to_session_type(self, tool_name: str) -> SessionType:
        """Map tool name to SessionType.

        Args:
            tool_name: Tool identifier from LLM.

        Returns:
            Corresponding SessionType.
        """
        mapping = {
            'claude_code': SessionType.CLAUDE_CODE,
            'cursor': SessionType.CURSOR_CLI,
            'copilot': SessionType.GITHUB_COPILOT,
            'github_copilot': SessionType.GITHUB_COPILOT,
        }

        return mapping.get(tool_name, SessionType.UNKNOWN)

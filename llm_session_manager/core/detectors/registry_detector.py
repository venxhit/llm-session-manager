"""Registry-based AI coding assistant detection.

Uses a community-maintained YAML registry to identify known AI tools.
Fast, accurate, and easily maintainable.
"""

import platform
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
import structlog
import psutil

from ...models import SessionType

logger = structlog.get_logger()


class RegistryDetector:
    """Detect AI coding assistants using pattern registry."""

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize registry detector.

        Args:
            registry_path: Path to registry YAML file. If None, uses default.
        """
        self.logger = logger
        self.platform = platform.system().lower()

        # Load registry
        if registry_path is None:
            registry_path = Path(__file__).parent.parent.parent / "config" / "ai_tools_registry.yaml"

        self.registry = self._load_registry(registry_path)
        self.tools = self.registry.get('ai_coding_assistants', {})

        self.logger.debug(
            "registry_detector_initialized",
            tools_count=len(self.tools),
            platform=self.platform
        )

    def _load_registry(self, path: Path) -> Dict[str, Any]:
        """Load registry from YAML file.

        Args:
            path: Path to registry file.

        Returns:
            Parsed registry dictionary.
        """
        try:
            with open(path, 'r') as f:
                registry = yaml.safe_load(f)
                self.logger.info("registry_loaded", path=str(path))
                return registry
        except Exception as e:
            self.logger.error("registry_load_failed", error=str(e), path=str(path))
            return {'ai_coding_assistants': {}}

    def identify_session_type(self, process: psutil.Process) -> Optional[SessionType]:
        """Identify AI assistant type from process using registry.

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

            # Try to match against each registered tool
            for tool_id, tool_config in self.tools.items():
                if self._matches_tool(proc_name, cmdline_str, cmdline, tool_config):
                    # Check if this is an excluded helper process
                    if self._is_excluded(proc_name, cmdline_str, tool_config):
                        continue

                    self.logger.debug(
                        "tool_matched",
                        tool=tool_id,
                        process=proc_name,
                        pid=proc_info.get('pid')
                    )

                    # Map tool_id to SessionType
                    return self._map_to_session_type(tool_id)

            return None

        except Exception as e:
            self.logger.debug("registry_detection_failed", error=str(e))
            return None

    def _matches_tool(
        self,
        proc_name: str,
        cmdline_str: str,
        cmdline: List[str],
        tool_config: Dict[str, Any]
    ) -> bool:
        """Check if process matches tool patterns.

        Args:
            proc_name: Process name (lowercased).
            cmdline_str: Full command line string (lowercased).
            cmdline: Command line arguments list.
            tool_config: Tool configuration from registry.

        Returns:
            True if process matches tool patterns.
        """
        patterns = tool_config.get('patterns', {})

        # Check process name patterns
        process_names = patterns.get('process_names', [])
        for name in process_names:
            if name.lower() in proc_name:
                # Additional validation: check cmdline or paths
                if self._validate_match(cmdline_str, cmdline, patterns):
                    return True

        # Check cmdline keyword patterns
        cmdline_keywords = patterns.get('cmdline_keywords', [])
        for keyword in cmdline_keywords:
            if keyword.lower() in cmdline_str:
                return True

        # Check path patterns for current platform
        paths = patterns.get('paths', {})
        platform_paths = paths.get(self._normalize_platform(), [])
        for path_pattern in platform_paths:
            # Expand ~ and environment variables
            expanded_path = str(Path(path_pattern).expanduser()).lower()
            if expanded_path in cmdline_str:
                return True

        return False

    def _validate_match(
        self,
        cmdline_str: str,
        cmdline: List[str],
        patterns: Dict[str, Any]
    ) -> bool:
        """Validate that a process name match is genuine.

        Args:
            cmdline_str: Command line string.
            cmdline: Command line arguments.
            patterns: Tool patterns to validate against.

        Returns:
            True if match is valid.
        """
        # Check if cmdline contains expected keywords or paths
        cmdline_keywords = patterns.get('cmdline_keywords', [])
        paths = patterns.get('paths', {})
        platform_paths = paths.get(self._normalize_platform(), [])

        # Must match at least one cmdline keyword or path
        for keyword in cmdline_keywords:
            if keyword.lower() in cmdline_str:
                return True

        for path_pattern in platform_paths:
            expanded_path = str(Path(path_pattern).expanduser()).lower()
            if expanded_path in cmdline_str:
                return True

        return False

    def _is_excluded(
        self,
        proc_name: str,
        cmdline_str: str,
        tool_config: Dict[str, Any]
    ) -> bool:
        """Check if process should be excluded (helper process, etc.).

        Args:
            proc_name: Process name (lowercased).
            cmdline_str: Command line string (lowercased).
            tool_config: Tool configuration.

        Returns:
            True if process should be excluded.
        """
        exclude_patterns = tool_config.get('exclude_patterns', [])

        for pattern in exclude_patterns:
            if pattern.lower() in proc_name or pattern.lower() in cmdline_str:
                return True

        return False

    def _normalize_platform(self) -> str:
        """Normalize platform name for registry lookup.

        Returns:
            Platform name: 'macos', 'windows', or 'linux'.
        """
        if self.platform == 'darwin':
            return 'macos'
        elif self.platform in ['win32', 'windows']:
            return 'windows'
        else:
            return 'linux'

    def _map_to_session_type(self, tool_id: str) -> SessionType:
        """Map registry tool ID to SessionType enum.

        Args:
            tool_id: Tool identifier from registry.

        Returns:
            Corresponding SessionType.
        """
        # Direct mappings
        mapping = {
            'claude_code': SessionType.CLAUDE_CODE,
            'cursor': SessionType.CURSOR_CLI,
            'github_copilot': SessionType.GITHUB_COPILOT,
            # Add more as SessionType enum expands
        }

        return mapping.get(tool_id, SessionType.UNKNOWN)

    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a tool from registry.

        Args:
            tool_id: Tool identifier.

        Returns:
            Tool configuration dictionary or None.
        """
        return self.tools.get(tool_id)

    def list_supported_tools(self) -> List[str]:
        """Get list of all supported tools in registry.

        Returns:
            List of tool display names.
        """
        return [
            tool.get('display_name', tool_id)
            for tool_id, tool in self.tools.items()
        ]

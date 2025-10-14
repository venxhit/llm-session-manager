"""Configuration management for LLM Session Manager."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class Config:
    """Manages configuration loading and defaults.

    Loads configuration from YAML file with sensible defaults.
    Configuration file location: ~/.config/llm-session-manager/config.yaml
    """

    DEFAULT_CONFIG = {
        "token_limits": {
            "claude_pro": 200000,
            "claude_max5": 350000,
            "claude_max20": 1400000,
            "cursor_default": 100000,
            "github_copilot": 8000,
        },
        "health_weights": {
            "token_usage": 0.40,
            "duration": 0.20,
            "activity": 0.20,
            "errors": 0.20,
        },
        "thresholds": {
            "token_warning": 0.80,  # Warn at 80% token usage
            "token_critical": 0.90,  # Critical at 90% token usage
            "health_warning": 0.70,  # Warn below 70% health
            "health_critical": 0.40,  # Critical below 40% health
            "idle_timeout_minutes": 30,  # Consider idle after 30 min
        },
        "dashboard": {
            "refresh_interval": 5,  # Refresh every 5 seconds
            "color_scheme": "dark",  # dark or light
            "show_tags": True,
            "show_project": True,
        },
        "database": {
            "path": "data/sessions.db",
            "auto_cleanup_days": 30,  # Auto-delete sessions older than 30 days
        },
        "monitoring": {
            "auto_discover": True,
            "discovery_interval": 10,  # Discover new sessions every 10 seconds
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".config" / "llm-session-manager" / "config.yaml"

        self.data = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default.

        Returns:
            Configuration dictionary.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)

                # Merge user config with defaults (user config takes precedence)
                config = self._merge_configs(self.DEFAULT_CONFIG.copy(), user_config or {})
                logger.info("config_loaded", path=str(self.config_path))
                return config

            except Exception as e:
                logger.warning("config_load_failed", path=str(self.config_path), error=str(e))
                logger.info("using_default_config")
                return self.DEFAULT_CONFIG.copy()
        else:
            logger.info("config_not_found", path=str(self.config_path))
            logger.info("using_default_config")
            return self.DEFAULT_CONFIG.copy()

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge override config into base config.

        Args:
            base: Base configuration dictionary.
            override: Override configuration dictionary.

        Returns:
            Merged configuration.
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base

    def save_config(self) -> None:
        """Save current configuration to file.

        Creates parent directories if needed.
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)

        logger.info("config_saved", path=str(self.config_path))

    def create_default_config(self) -> None:
        """Create a default configuration file.

        Useful for first-time setup.
        """
        self.data = self.DEFAULT_CONFIG.copy()
        self.save_config()
        logger.info("default_config_created", path=str(self.config_path))

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Supports dot notation for nested keys (e.g., "dashboard.refresh_interval").

        Args:
            key: Configuration key (supports dot notation).
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Supports dot notation for nested keys (e.g., "dashboard.refresh_interval").

        Args:
            key: Configuration key (supports dot notation).
            value: Value to set.
        """
        keys = key.split('.')
        target = self.data

        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        # Set the value
        target[keys[-1]] = value

    def get_token_limit(self, plan_type: str) -> int:
        """Get token limit for a plan type.

        Args:
            plan_type: Plan type identifier.

        Returns:
            Token limit in tokens.
        """
        return self.get(f"token_limits.{plan_type}", 200000)

    def get_health_weights(self) -> Dict[str, float]:
        """Get health scoring weights.

        Returns:
            Dictionary of component weights.
        """
        return self.get("health_weights", self.DEFAULT_CONFIG["health_weights"])

    def get_dashboard_settings(self) -> Dict[str, Any]:
        """Get dashboard settings.

        Returns:
            Dictionary of dashboard settings.
        """
        return self.get("dashboard", self.DEFAULT_CONFIG["dashboard"])

    def get_thresholds(self) -> Dict[str, float]:
        """Get warning and critical thresholds.

        Returns:
            Dictionary of threshold values.
        """
        return self.get("thresholds", self.DEFAULT_CONFIG["thresholds"])

    def __repr__(self) -> str:
        """String representation."""
        return f"Config(path={self.config_path}, loaded={self.config_path.exists()})"

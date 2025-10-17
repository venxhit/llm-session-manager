"""MCP server configuration settings."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import yaml


@dataclass
class MCPConfig:
    """Configuration for MCP servers."""

    # Server settings
    server_name: str = "llm-session-manager"
    server_version: str = "0.2.0"

    # Database paths
    db_path: str = "data/sessions.db"
    memory_path: str = "data/memories"

    # Feature flags
    enable_session_servers: bool = True
    enable_memory_search: bool = True
    enable_git_analysis: bool = True

    # Resource limits
    max_sessions_exposed: int = 100
    max_memory_results: int = 10
    max_file_size_mb: int = 10

    # Performance settings
    cache_ttl_seconds: int = 60
    enable_resource_caching: bool = True

    @classmethod
    def from_file(cls, config_path: str) -> "MCPConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file.

        Returns:
            MCPConfig instance.
        """
        path = Path(config_path)
        if not path.exists():
            return cls()  # Return defaults

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        mcp_config = data.get('mcp', {})
        return cls(**mcp_config)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of config.
        """
        return {
            'server_name': self.server_name,
            'server_version': self.server_version,
            'db_path': self.db_path,
            'memory_path': self.memory_path,
            'enable_session_servers': self.enable_session_servers,
            'enable_memory_search': self.enable_memory_search,
            'enable_git_analysis': self.enable_git_analysis,
            'max_sessions_exposed': self.max_sessions_exposed,
            'max_memory_results': self.max_memory_results,
            'max_file_size_mb': self.max_file_size_mb,
            'cache_ttl_seconds': self.cache_ttl_seconds,
            'enable_resource_caching': self.enable_resource_caching,
        }

    def save_to_file(self, config_path: str) -> None:
        """Save configuration to YAML file.

        Args:
            config_path: Path to save YAML configuration.
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new
        if path.exists():
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        # Update MCP section
        data['mcp'] = self.to_dict()

        # Save
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)


# Default configuration
DEFAULT_MCP_CONFIG = MCPConfig()


def get_mcp_config(config_path: Optional[str] = None) -> MCPConfig:
    """Get MCP configuration.

    Args:
        config_path: Optional path to config file. If not provided,
                    looks in default location.

    Returns:
        MCPConfig instance.
    """
    if config_path is None:
        # Try default locations
        default_paths = [
            Path.home() / ".config" / "llm-session-manager" / "config.yaml",
            Path("config.yaml"),
        ]

        for path in default_paths:
            if path.exists():
                return MCPConfig.from_file(str(path))

        # No config found, return defaults
        return DEFAULT_MCP_CONFIG

    return MCPConfig.from_file(config_path)

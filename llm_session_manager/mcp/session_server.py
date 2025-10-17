"""Phase 2: Enhanced MCP servers that wrap individual AI coding sessions.

These servers provide deeper integration with specific AI tools by monitoring
their file systems, git repositories, and process metrics in real-time.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, Tool, TextContent, Prompt, PromptMessage, PromptArgument
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None

from ..models.session import Session, SessionType
from ..utils.token_estimator import TokenEstimator

logger = structlog.get_logger()


class SessionMCPServer:
    """Enhanced MCP server for a specific AI coding session.

    This server wraps an individual session and provides:
    - Real-time file system monitoring
    - Git repository analysis
    - Enhanced token estimation
    - Code change tracking
    - Session activity detection
    """

    def __init__(self, session: Session):
        """Initialize session MCP server.

        Args:
            session: The session to monitor and expose.
        """
        if not MCP_AVAILABLE:
            raise RuntimeError(
                "MCP not available. Install with: pip install mcp"
            )

        self.session = session
        self.token_estimator = TokenEstimator()
        self.working_dir = Path(session.working_directory)

        # Initialize server
        server_name = f"llm-session-{session.id[:8]}"
        self.server = Server(server_name)
        self._register_handlers()

        logger.info("session_mcp_server_initialized",
                   session_id=session.id,
                   working_dir=str(self.working_dir))

    def _register_handlers(self):
        """Register MCP handlers specific to this session."""

        # ==================== RESOURCES ====================

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List resources for this session."""
            return [
                Resource(
                    uri=f"session://{self.session.id}/realtime_metrics",
                    name="Real-time Metrics",
                    description="Current token usage, file count, activity",
                    mimeType="application/json"
                ),
                Resource(
                    uri=f"session://{self.session.id}/git_status",
                    name="Git Status",
                    description="Current git repository status",
                    mimeType="application/json"
                ),
                Resource(
                    uri=f"session://{self.session.id}/recent_changes",
                    name="Recent Changes",
                    description="Recent file modifications",
                    mimeType="application/json"
                ),
                Resource(
                    uri=f"session://{self.session.id}/file_tree",
                    name="File Tree",
                    description="Current project file structure",
                    mimeType="application/json"
                ),
                Resource(
                    uri=f"session://{self.session.id}/context_estimate",
                    name="Context Estimate",
                    description="Estimated context window usage",
                    mimeType="application/json"
                ),
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read session-specific resource."""
            logger.info("session_mcp_resource_read", uri=uri, session=self.session.id)

            if uri.endswith("/realtime_metrics"):
                metrics = await self._get_realtime_metrics()
                return json.dumps(metrics, indent=2)

            elif uri.endswith("/git_status"):
                git_status = await self._get_git_status()
                return json.dumps(git_status, indent=2)

            elif uri.endswith("/recent_changes"):
                changes = await self._get_recent_changes()
                return json.dumps(changes, indent=2)

            elif uri.endswith("/file_tree"):
                tree = await self._get_file_tree()
                return json.dumps(tree, indent=2)

            elif uri.endswith("/context_estimate"):
                estimate = await self._estimate_context()
                return json.dumps(estimate, indent=2)

            return json.dumps({"error": f"Unknown resource: {uri}"})

        # ==================== TOOLS ====================

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List tools available for this session."""
            return [
                Tool(
                    name="analyze_session_health",
                    description="Deep analysis of session health metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_file_content",
                    description="Read content of a file in the session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Relative path to file"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="analyze_git_commits",
                    description="Analyze recent git commits in this session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "number",
                                "description": "Number of commits to analyze (default: 10)"
                            }
                        }
                    }
                ),
                Tool(
                    name="suggest_context_cleanup",
                    description="Suggest files/context that could be removed",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute session-specific tool."""
            logger.info("session_mcp_tool_called",
                       tool=name,
                       args=arguments,
                       session=self.session.id)

            try:
                if name == "analyze_session_health":
                    analysis = await self._analyze_health()
                    return [TextContent(
                        type="text",
                        text=json.dumps(analysis, indent=2)
                    )]

                elif name == "get_file_content":
                    file_path = arguments.get("file_path")
                    content = await self._read_file(file_path)
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "file_path": file_path,
                            "content": content,
                            "size": len(content) if content else 0
                        }, indent=2)
                    )]

                elif name == "analyze_git_commits":
                    limit = arguments.get("limit", 10)
                    commits = await self._analyze_commits(limit)
                    return [TextContent(
                        type="text",
                        text=json.dumps(commits, indent=2)
                    )]

                elif name == "suggest_context_cleanup":
                    suggestions = await self._suggest_cleanup()
                    return [TextContent(
                        type="text",
                        text=json.dumps(suggestions, indent=2)
                    )]

                else:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": f"Unknown tool: {name}"})
                    )]

            except Exception as e:
                logger.error("session_mcp_tool_error",
                           tool=name,
                           error=str(e),
                           session=self.session.id)
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)})
                )]

        # ==================== PROMPTS ====================

        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List prompts for this session."""
            return [
                Prompt(
                    name="session_status_report",
                    description="Comprehensive status report for this session",
                    arguments=[]
                ),
                Prompt(
                    name="what_am_i_working_on",
                    description="Infer what task this session is focused on",
                    arguments=[]
                ),
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> PromptMessage:
            """Get session-specific prompt."""
            if name == "session_status_report":
                metrics = await self._get_realtime_metrics()
                git_status = await self._get_git_status()

                content = f"""# Session Status Report

**Session ID**: {self.session.id}
**Type**: {self.session.type.value}
**Status**: {self.session.status.value}
**Working Directory**: {self.session.working_directory}

## Real-time Metrics

- **Token Count**: {metrics.get('token_count', 0):,}
- **Token Limit**: {metrics.get('token_limit', 0):,}
- **Usage**: {metrics.get('token_usage_percent', 0):.1f}%
- **File Count**: {metrics.get('file_count', 0)}
- **Health Score**: {metrics.get('health_score', 0):.1f}%

## Git Status

- **Branch**: {git_status.get('branch', 'N/A')}
- **Modified Files**: {len(git_status.get('modified', []))}
- **Untracked Files**: {len(git_status.get('untracked', []))}
- **Staged Changes**: {len(git_status.get('staged', []))}

## Activity

- **Start Time**: {self.session.start_time.isoformat()}
- **Last Activity**: {self.session.last_activity.isoformat()}
- **Duration**: {metrics.get('duration_hours', 0):.1f} hours
"""
                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )

            elif name == "what_am_i_working_on":
                # Infer from git commits, file names, etc.
                commits = await self._analyze_commits(5)
                changes = await self._get_recent_changes()

                content = f"""# Session Focus Analysis

Based on recent activity in this session:

## Recent Commits
"""
                for commit in commits.get('commits', [])[:3]:
                    content += f"\n- {commit.get('message', 'N/A')}"

                content += "\n\n## Recently Modified Files\n"
                for file in changes.get('recent_files', [])[:5]:
                    content += f"\n- {file['path']}"

                content += "\n\n## Project Tags\n"
                if self.session.tags:
                    for tag in self.session.tags:
                        content += f"\n- {tag}"
                else:
                    content += "\nNo tags set."

                if self.session.description:
                    content += f"\n\n## Session Description\n\n{self.session.description}"

                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )

            return PromptMessage(
                role="user",
                content=TextContent(type="text", text=f"Unknown prompt: {name}")
            )

    # ==================== HELPER METHODS ====================

    async def _get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time session metrics."""
        # Update token count
        token_count = self.token_estimator.estimate_session_tokens(self.session)
        self.session.token_count = token_count

        # Calculate duration
        duration = (datetime.now() - self.session.start_time).total_seconds() / 3600

        return {
            "session_id": self.session.id,
            "token_count": token_count,
            "token_limit": self.session.token_limit,
            "token_usage_percent": self.session.calculate_token_usage_percent(),
            "file_count": self.session.file_count,
            "health_score": self.session.health_score,
            "duration_hours": duration,
            "last_activity": self.session.last_activity.isoformat(),
            "timestamp": datetime.now().isoformat()
        }

    async def _get_git_status(self) -> Dict[str, Any]:
        """Get git repository status."""
        if not self.working_dir.exists():
            return {"error": "Working directory not found"}

        try:
            # Check if git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=str(self.working_dir),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return {"error": "Not a git repository"}

            # Get branch
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(self.working_dir),
                capture_output=True,
                text=True,
                timeout=5
            ).stdout.strip()

            # Get status
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.working_dir),
                capture_output=True,
                text=True,
                timeout=5
            ).stdout

            # Parse status
            modified = []
            untracked = []
            staged = []

            for line in status.split('\n'):
                if not line:
                    continue
                status_code = line[:2]
                file_path = line[3:]

                if status_code[0] in ['M', 'A', 'D', 'R']:
                    staged.append(file_path)
                if status_code[1] == 'M':
                    modified.append(file_path)
                if status_code == '??':
                    untracked.append(file_path)

            return {
                "branch": branch,
                "modified": modified,
                "untracked": untracked,
                "staged": staged,
                "is_clean": len(modified) == 0 and len(untracked) == 0 and len(staged) == 0
            }

        except Exception as e:
            logger.error("git_status_error", error=str(e))
            return {"error": str(e)}

    async def _get_recent_changes(self) -> Dict[str, Any]:
        """Get recently modified files."""
        if not self.working_dir.exists():
            return {"error": "Working directory not found"}

        try:
            recent_files = []

            # Walk directory and find recently modified files
            for root, dirs, files in os.walk(self.working_dir):
                # Skip common ignore patterns
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', '__pycache__', '.pytest_cache']]

                for file in files:
                    file_path = Path(root) / file
                    try:
                        stat = file_path.stat()
                        recent_files.append({
                            "path": str(file_path.relative_to(self.working_dir)),
                            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "size": stat.st_size
                        })
                    except:
                        continue

            # Sort by modification time
            recent_files.sort(key=lambda x: x['modified_time'], reverse=True)

            return {
                "recent_files": recent_files[:20],  # Top 20 most recent
                "total_files": len(recent_files)
            }

        except Exception as e:
            logger.error("recent_changes_error", error=str(e))
            return {"error": str(e)}

    async def _get_file_tree(self) -> Dict[str, Any]:
        """Get project file structure."""
        if not self.working_dir.exists():
            return {"error": "Working directory not found"}

        try:
            tree = []

            for root, dirs, files in os.walk(self.working_dir):
                # Skip common ignore patterns
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '.venv', '__pycache__', '.pytest_cache']]

                level = str(root).replace(str(self.working_dir), '').count(os.sep)
                indent = ' ' * 2 * level
                tree.append(f"{indent}{os.path.basename(root)}/")

                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    tree.append(f"{subindent}{file}")

            return {
                "tree": tree[:500],  # Limit to first 500 lines
                "working_directory": str(self.working_dir)
            }

        except Exception as e:
            logger.error("file_tree_error", error=str(e))
            return {"error": str(e)}

    async def _estimate_context(self) -> Dict[str, Any]:
        """Estimate context window usage."""
        token_count = self.token_estimator.estimate_session_tokens(self.session)

        return {
            "session_id": self.session.id,
            "estimated_tokens": token_count,
            "token_limit": self.session.token_limit,
            "usage_percent": (token_count / self.session.token_limit * 100) if self.session.token_limit > 0 else 0,
            "tokens_remaining": max(0, self.session.token_limit - token_count),
            "estimation_method": "file_based",
            "note": "This is an estimate based on file sizes. Actual token usage may vary."
        }

    async def _analyze_health(self) -> Dict[str, Any]:
        """Deep health analysis."""
        metrics = await self._get_realtime_metrics()
        git_status = await self._get_git_status()

        # Calculate health factors
        token_health = 100 - metrics.get('token_usage_percent', 0)
        activity_health = 100  # Would need real activity tracking

        issues = []
        if metrics.get('token_usage_percent', 0) > 80:
            issues.append("Token usage is high (>80%)")
        if metrics.get('duration_hours', 0) > 4:
            issues.append("Session has been running for over 4 hours")
        if not git_status.get('is_clean', True):
            issues.append("Uncommitted changes detected")

        return {
            "session_id": self.session.id,
            "overall_health": self.session.health_score,
            "factors": {
                "token_health": token_health,
                "activity_health": activity_health,
            },
            "issues": issues,
            "recommendations": self._generate_recommendations(issues)
        }

    async def _read_file(self, file_path: str) -> Optional[str]:
        """Read file content."""
        try:
            full_path = self.working_dir / file_path
            if not full_path.exists():
                return None

            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error("read_file_error", error=str(e))
            return None

    async def _analyze_commits(self, limit: int = 10) -> Dict[str, Any]:
        """Analyze recent git commits."""
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%ae|%ad|%s"],
                cwd=str(self.working_dir),
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return {"error": "Failed to get git log"}

            commits = []
            for line in result.stdout.split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })

            return {
                "commits": commits,
                "count": len(commits)
            }

        except Exception as e:
            logger.error("analyze_commits_error", error=str(e))
            return {"error": str(e)}

    async def _suggest_cleanup(self) -> Dict[str, Any]:
        """Suggest context cleanup."""
        suggestions = []

        # Check for large files
        changes = await self._get_recent_changes()
        large_files = [
            f for f in changes.get('recent_files', [])
            if f.get('size', 0) > 1_000_000  # > 1MB
        ]

        if large_files:
            suggestions.append({
                "type": "large_files",
                "message": f"Found {len(large_files)} files > 1MB that could be excluded",
                "files": [f['path'] for f in large_files[:5]]
            })

        # Check for many untracked files
        git_status = await self._get_git_status()
        if len(git_status.get('untracked', [])) > 10:
            suggestions.append({
                "type": "untracked_files",
                "message": f"{len(git_status['untracked'])} untracked files - consider .gitignore",
                "files": git_status['untracked'][:5]
            })

        return {
            "suggestions": suggestions,
            "count": len(suggestions)
        }

    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []

        for issue in issues:
            if "token usage" in issue.lower():
                recommendations.append("Consider starting a new session to reset context")
            elif "running for" in issue.lower():
                recommendations.append("Long-running session detected - consider taking a break")
            elif "uncommitted changes" in issue.lower():
                recommendations.append("Commit your changes to preserve progress")

        return recommendations

    async def run(self):
        """Run the session MCP server."""
        logger.info("session_mcp_server_starting", session_id=self.session.id)

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

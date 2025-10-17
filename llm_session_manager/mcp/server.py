"""Main MCP server implementation for LLM Session Manager.

This server exposes session management functionality via Model Context Protocol,
allowing MCP clients (like Claude Desktop) to query and interact with session data.
"""

import json
from typing import Any, Dict, List, Optional
import structlog
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        Prompt,
        PromptMessage,
        PromptArgument,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None

from ..storage.database import Database
from ..core.session_discovery import SessionDiscovery
from ..core.health_monitor import HealthMonitor
from ..core.memory_manager import MemoryManager
from ..utils.recommendations import RecommendationEngine
from ..models.session import Session, SessionType, SessionStatus

logger = structlog.get_logger()


class MCPServer:
    """MCP server for LLM Session Manager.

    Exposes session data and operations via Model Context Protocol:
    - Resources: Session data, health metrics, memory
    - Tools: Search, export, recommendations
    - Prompts: Common session management workflows
    """

    def __init__(
        self,
        db_path: str = "data/sessions.db",
        memory_path: str = "data/memories"
    ):
        """Initialize MCP server.

        Args:
            db_path: Path to session database.
            memory_path: Path to memory storage.
        """
        if not MCP_AVAILABLE:
            raise RuntimeError(
                "MCP not available. Install with: pip install mcp"
            )

        self.db = Database(db_path)
        self.db.init_db()

        self.discovery = SessionDiscovery(self.db)
        self.health_monitor = HealthMonitor()
        self.memory_manager = MemoryManager(memory_path)
        self.recommendation_engine = RecommendationEngine()

        self.server = Server("llm-session-manager")
        self._register_handlers()

        logger.info("mcp_server_initialized",
                   db_path=db_path,
                   memory_path=memory_path)

    def _register_handlers(self):
        """Register MCP handlers for resources, tools, and prompts."""

        # ==================== RESOURCES ====================

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List all available resources."""
            resources = [
                Resource(
                    uri="session://list",
                    name="All Sessions",
                    description="List of all tracked sessions",
                    mimeType="application/json"
                ),
                Resource(
                    uri="session://active",
                    name="Active Sessions",
                    description="Currently active sessions",
                    mimeType="application/json"
                ),
                Resource(
                    uri="memory://stats",
                    name="Memory Statistics",
                    description="Cross-session memory statistics",
                    mimeType="application/json"
                ),
            ]

            # Add individual session resources
            sessions = self.db.get_all_sessions()
            for session in sessions:
                resources.extend([
                    Resource(
                        uri=f"session://{session.id}/info",
                        name=f"Session {session.id[:8]} Info",
                        description=f"Detailed info for {session.type.value} session",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri=f"session://{session.id}/health",
                        name=f"Session {session.id[:8]} Health",
                        description=f"Health metrics for session",
                        mimeType="application/json"
                    ),
                    Resource(
                        uri=f"session://{session.id}/memories",
                        name=f"Session {session.id[:8]} Memories",
                        description=f"Memories from this session",
                        mimeType="application/json"
                    ),
                ])

            return resources

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource."""
            logger.info("mcp_resource_read", uri=uri)

            if uri == "session://list":
                sessions = self.db.get_all_sessions()
                return json.dumps({
                    "sessions": [s.to_dict() for s in sessions],
                    "count": len(sessions)
                }, indent=2)

            elif uri == "session://active":
                sessions = self.db.get_active_sessions()
                return json.dumps({
                    "sessions": [s.to_dict() for s in sessions],
                    "count": len(sessions)
                }, indent=2)

            elif uri == "memory://stats":
                stats = self.memory_manager.get_stats()
                return json.dumps(stats, indent=2)

            elif uri.startswith("session://"):
                # Parse session-specific URIs
                parts = uri.split("/")
                if len(parts) >= 3:
                    session_id = parts[2]
                    resource_type = parts[3] if len(parts) > 3 else "info"

                    session = self.db.get_session(session_id)
                    if not session:
                        return json.dumps({"error": f"Session {session_id} not found"})

                    if resource_type == "info":
                        return json.dumps(session.to_dict(), indent=2)

                    elif resource_type == "health":
                        health_breakdown = self.health_monitor.calculate_health_breakdown(session)
                        return json.dumps({
                            "session_id": session.id,
                            "health_score": session.health_score,
                            "breakdown": health_breakdown,
                            "is_healthy": session.is_healthy(),
                        }, indent=2)

                    elif resource_type == "memories":
                        memories = self.memory_manager.get_memories_by_session(session_id)
                        return json.dumps({
                            "session_id": session_id,
                            "memories": memories,
                            "count": len(memories)
                        }, indent=2)

            return json.dumps({"error": f"Unknown resource: {uri}"})

        # ==================== TOOLS ====================

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="search_memory",
                    description="Search cross-session memories using semantic search",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "limit": {
                                "type": "number",
                                "description": "Max results (default: 5)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="recommend_session",
                    description="Get intelligent session recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "Optional context about what you're working on"
                            }
                        }
                    }
                ),
                Tool(
                    name="export_session",
                    description="Export session context in various formats",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID to export"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["json", "yaml", "markdown"],
                                "description": "Export format (default: json)"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="find_session",
                    description="Find sessions by criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tag": {
                                "type": "string",
                                "description": "Filter by tag"
                            },
                            "project": {
                                "type": "string",
                                "description": "Filter by project name"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["active", "idle", "waiting", "error"],
                                "description": "Filter by status"
                            },
                            "description": {
                                "type": "string",
                                "description": "Search in session descriptions"
                            }
                        }
                    }
                ),
                Tool(
                    name="update_session_health",
                    description="Recalculate health score for a session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID"
                            }
                        },
                        "required": ["session_id"]
                    }
                ),
                Tool(
                    name="discover_sessions",
                    description="Discover new/updated sessions from running processes",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a tool."""
            logger.info("mcp_tool_called", tool=name, args=arguments)

            try:
                if name == "search_memory":
                    query = arguments.get("query", "")
                    limit = arguments.get("limit", 5)

                    memories = self.memory_manager.search_memories(query, limit=limit)

                    result = {
                        "query": query,
                        "results": memories,
                        "count": len(memories)
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]

                elif name == "recommend_session":
                    context = arguments.get("context", "")

                    # Get all sessions
                    sessions = self.db.get_all_sessions()

                    # Generate recommendations
                    recommendations = self.recommendation_engine.generate_recommendations(
                        sessions
                    )

                    # If context provided, search memories for relevant info
                    relevant_memories = []
                    if context:
                        relevant_memories = self.memory_manager.search_memories(
                            context, limit=3
                        )

                    result = {
                        "recommendations": recommendations,
                        "relevant_memories": relevant_memories if context else [],
                        "context": context
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]

                elif name == "export_session":
                    session_id = arguments.get("session_id")
                    format_type = arguments.get("format", "json")

                    session = self.db.get_session(session_id)
                    if not session:
                        return [TextContent(
                            type="text",
                            text=json.dumps({"error": f"Session {session_id} not found"})
                        )]

                    # Get additional data
                    health_breakdown = self.health_monitor.calculate_health_breakdown(session)
                    memories = self.memory_manager.get_memories_by_session(session_id)

                    export_data = {
                        "session": session.to_dict(),
                        "health": health_breakdown,
                        "memories": memories,
                        "exported_at": datetime.now().isoformat()
                    }

                    if format_type == "json":
                        content = json.dumps(export_data, indent=2)
                    elif format_type == "yaml":
                        try:
                            import yaml
                            content = yaml.dump(export_data, default_flow_style=False)
                        except ImportError:
                            content = json.dumps(export_data, indent=2)
                    else:  # markdown
                        content = self._format_as_markdown(export_data)

                    return [TextContent(
                        type="text",
                        text=content
                    )]

                elif name == "find_session":
                    tag = arguments.get("tag")
                    project = arguments.get("project")
                    status = arguments.get("status")
                    description = arguments.get("description")

                    sessions = self.db.get_all_sessions()

                    # Filter sessions
                    filtered = sessions
                    if tag:
                        filtered = [s for s in filtered if s.has_tag(tag)]
                    if project:
                        filtered = [s for s in filtered if s.project_name == project]
                    if status:
                        filtered = [s for s in filtered if s.status.value == status]
                    if description:
                        filtered = [
                            s for s in filtered
                            if s.description and description.lower() in s.description.lower()
                        ]

                    result = {
                        "sessions": [s.to_dict() for s in filtered],
                        "count": len(filtered),
                        "filters": {
                            "tag": tag,
                            "project": project,
                            "status": status,
                            "description": description
                        }
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]

                elif name == "update_session_health":
                    session_id = arguments.get("session_id")

                    session = self.db.get_session(session_id)
                    if not session:
                        return [TextContent(
                            type="text",
                            text=json.dumps({"error": f"Session {session_id} not found"})
                        )]

                    # Recalculate health
                    health_score = self.health_monitor.calculate_health_score(session)
                    session.health_score = health_score
                    self.db.update_session(session)

                    breakdown = self.health_monitor.calculate_health_breakdown(session)

                    result = {
                        "session_id": session_id,
                        "health_score": health_score,
                        "breakdown": breakdown,
                        "updated_at": datetime.now().isoformat()
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]

                elif name == "discover_sessions":
                    # Discover sessions
                    discovered = self.discovery.discover_sessions()

                    result = {
                        "discovered": [s.to_dict() for s in discovered],
                        "count": len(discovered),
                        "timestamp": datetime.now().isoformat()
                    }

                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]

                else:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": f"Unknown tool: {name}"})
                    )]

            except Exception as e:
                logger.error("mcp_tool_error", tool=name, error=str(e))
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)})
                )]

        # ==================== PROMPTS ====================

        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List available prompts."""
            return [
                Prompt(
                    name="session_health_check",
                    description="Check health of all sessions and get recommendations",
                    arguments=[]
                ),
                Prompt(
                    name="find_relevant_session",
                    description="Find the best session for a specific task",
                    arguments=[
                        PromptArgument(
                            name="task",
                            description="What task are you working on?",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="session_summary",
                    description="Get a summary of a specific session",
                    arguments=[
                        PromptArgument(
                            name="session_id",
                            description="Session ID to summarize",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="cross_session_search",
                    description="Search for knowledge across all sessions",
                    arguments=[
                        PromptArgument(
                            name="query",
                            description="What are you looking for?",
                            required=True
                        )
                    ]
                ),
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> PromptMessage:
            """Get a specific prompt with arguments."""
            logger.info("mcp_prompt_requested", prompt=name, args=arguments)

            if name == "session_health_check":
                sessions = self.db.get_all_sessions()
                recommendations = self.recommendation_engine.generate_recommendations(sessions)

                content = f"""# Session Health Check

Total Sessions: {len(sessions)}
Active Sessions: {len([s for s in sessions if s.status == SessionStatus.ACTIVE])}

## Health Summary
"""
                for session in sessions:
                    health_emoji = "✅" if session.health_score >= 70 else "⚠️" if session.health_score >= 40 else "🔴"
                    content += f"\n{health_emoji} {session.type.value} ({session.id[:8]}): {session.health_score:.1f}%"

                content += "\n\n## Recommendations\n"
                for rec in recommendations:
                    content += f"\n- {rec['type']}: {rec['message']}"

                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )

            elif name == "find_relevant_session":
                task = arguments.get("task", "")

                # Search memories
                relevant_memories = self.memory_manager.search_memories(task, limit=5)

                # Get sessions mentioned in memories
                session_ids = set(m['metadata'].get('session_id') for m in relevant_memories)
                sessions = [self.db.get_session(sid) for sid in session_ids if sid]
                sessions = [s for s in sessions if s]  # Filter None

                content = f"""# Find Session for: {task}

## Relevant Sessions
"""
                for session in sessions:
                    content += f"\n### {session.type.value} ({session.id[:8]})"
                    content += f"\n- Health: {session.health_score:.1f}%"
                    content += f"\n- Project: {session.project_name or 'N/A'}"
                    content += f"\n- Tags: {', '.join(session.tags) if session.tags else 'None'}"
                    if session.description:
                        content += f"\n- Description: {session.description}"
                    content += "\n"

                content += "\n## Relevant Memories\n"
                for memory in relevant_memories:
                    content += f"\n- {memory['content']} (Relevance: {memory['relevance']*100:.0f}%)"

                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )

            elif name == "session_summary":
                session_id = arguments.get("session_id", "")
                session = self.db.get_session(session_id)

                if not session:
                    content = f"Session {session_id} not found."
                else:
                    health_breakdown = self.health_monitor.calculate_health_breakdown(session)
                    memories = self.memory_manager.get_memories_by_session(session_id)

                    content = f"""# Session Summary: {session.type.value}

**ID**: {session.id}
**Status**: {session.status.value}
**Health**: {session.health_score:.1f}%
**Working Directory**: {session.working_directory}

## Health Breakdown
- Token Usage: {health_breakdown.get('token_usage_score', 0):.1f}%
- Duration: {health_breakdown.get('duration_score', 0):.1f}%
- Activity: {health_breakdown.get('activity_score', 0):.1f}%
- Errors: {health_breakdown.get('error_score', 0):.1f}%

## Metadata
- Project: {session.project_name or 'N/A'}
- Tags: {', '.join(session.tags) if session.tags else 'None'}
- Description: {session.description or 'N/A'}

## Memories ({len(memories)})
"""
                    for memory in memories[:5]:  # Show first 5
                        content += f"\n- {memory.get('content', 'N/A')}"

                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )

            elif name == "cross_session_search":
                query = arguments.get("query", "")
                memories = self.memory_manager.search_memories(query, limit=10)

                content = f"""# Cross-Session Search: {query}

Found {len(memories)} relevant memories:
"""
                for i, memory in enumerate(memories, 1):
                    session_id = memory['metadata'].get('session_id', 'unknown')[:8]
                    relevance = memory['relevance'] * 100
                    content += f"\n## Result {i} (Relevance: {relevance:.0f}%)"
                    content += f"\nSession: {session_id}"
                    content += f"\n{memory['content']}\n"

                return PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )

            # Default
            return PromptMessage(
                role="user",
                content=TextContent(type="text", text=f"Unknown prompt: {name}")
            )

    def _format_as_markdown(self, data: Dict[str, Any]) -> str:
        """Format export data as markdown."""
        session = data['session']
        health = data['health']
        memories = data['memories']

        md = f"""# Session Export: {session['type']}

**ID**: {session['id']}
**Status**: {session['status']}
**Health Score**: {session['health_score']:.1f}%
**Working Directory**: {session['working_directory']}

## Health Breakdown

- **Token Usage**: {health.get('token_usage_score', 0):.1f}%
- **Duration**: {health.get('duration_score', 0):.1f}%
- **Activity**: {health.get('activity_score', 0):.1f}%
- **Errors**: {health.get('error_score', 0):.1f}%

## Metadata

- **Project**: {session.get('project_name') or 'N/A'}
- **Tags**: {', '.join(session.get('tags', [])) if session.get('tags') else 'None'}
- **Description**: {session.get('description') or 'N/A'}

## Memories ({len(memories)})

"""
        for memory in memories:
            md += f"- {memory.get('content', 'N/A')}\n"

        md += f"\n---\n*Exported at: {data['exported_at']}*\n"

        return md

    async def run(self):
        """Run the MCP server."""
        logger.info("mcp_server_starting")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

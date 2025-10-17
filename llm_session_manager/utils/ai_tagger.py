"""AI-powered tag suggestion using LLM analysis."""

import os
from typing import List, Dict, Optional
from pathlib import Path
import structlog
from anthropic import Anthropic

from ..models import Session

logger = structlog.get_logger()


class AITagger:
    """Uses LLM to analyze session content and suggest intelligent tags.

    Analyzes:
    - File content and structure
    - Code patterns and frameworks
    - Project purpose and domain
    - Technical stack

    Falls back to heuristic analysis if LLM is unavailable.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI tagger.

        Args:
            api_key: Anthropic API key. If None, will try ANTHROPIC_API_KEY env var.
        """
        self.logger = structlog.get_logger()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("ai_tagger_initialized", provider="anthropic")
            except Exception as e:
                logger.warning("ai_tagger_init_failed", error=str(e))

    def is_available(self) -> bool:
        """Check if AI tagging is available.

        Returns:
            True if LLM client is initialized.
        """
        return self.client is not None

    def suggest_tags_ai(
        self,
        session: Session,
        max_tags: int = 10,
        context_files: int = 10
    ) -> List[str]:
        """Use AI to suggest tags based on deep content analysis.

        Args:
            session: Session to analyze.
            max_tags: Maximum number of tags to return.
            context_files: Number of files to sample for context.

        Returns:
            List of suggested tags ordered by relevance.
        """
        if not self.is_available():
            logger.warning("ai_tagger_not_available")
            return []

        if not session.working_directory or not os.path.isdir(session.working_directory):
            logger.debug("no_working_directory", session_id=session.id)
            return []

        try:
            # Gather context about the session
            context = self._gather_context(session, max_files=context_files)

            if not context["files"]:
                logger.debug("no_analyzable_files", session_id=session.id)
                return []

            # Build prompt for LLM
            prompt = self._build_tag_prompt(session, context)

            # Call LLM
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse tags from response
            tags = self._parse_tag_response(response.content[0].text)

            logger.info("ai_tags_suggested",
                       session_id=session.id,
                       count=len(tags),
                       tags=tags[:max_tags])

            return tags[:max_tags]

        except Exception as e:
            logger.error("ai_tagging_failed", error=str(e))
            return []

    def _gather_context(self, session: Session, max_files: int = 10) -> Dict:
        """Gather context about the session for analysis.

        Args:
            session: Session to analyze.
            max_files: Maximum files to sample.

        Returns:
            Dictionary with context information.
        """
        context = {
            "directory_name": Path(session.working_directory).name,
            "files": [],
            "directories": set(),
            "file_extensions": set(),
            "existing_tags": session.tags,
            "existing_description": session.description,
        }

        try:
            files_collected = 0

            for root, dirs, files in os.walk(session.working_directory):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {
                    '__pycache__', 'node_modules', '.git', 'venv', 'env',
                    'build', 'dist', '.next', 'target', 'out'
                }]

                # Collect directory names
                for d in dirs:
                    context["directories"].add(d.lower())

                # Sample interesting files
                for filename in files:
                    if files_collected >= max_files:
                        break

                    file_path = os.path.join(root, filename)
                    ext = Path(filename).suffix.lower()

                    # Track extensions
                    if ext:
                        context["file_extensions"].add(ext)

                    # Only analyze certain file types
                    if ext in {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs',
                               '.java', '.rb', '.php', '.md', '.json', '.yaml', '.yml',
                               '.toml', '.sql', '.html', '.css', '.scss', '.vue'}:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read(5000)  # First 5KB
                                relative_path = os.path.relpath(file_path, session.working_directory)
                                context["files"].append({
                                    "path": relative_path,
                                    "content": content
                                })
                                files_collected += 1
                        except (UnicodeDecodeError, IOError):
                            continue

        except Exception as e:
            logger.debug("context_gathering_error", error=str(e))

        return context

    def _build_tag_prompt(self, session: Session, context: Dict) -> str:
        """Build prompt for LLM tag suggestion.

        Args:
            session: Session to analyze.
            context: Gathered context.

        Returns:
            Formatted prompt string.
        """
        files_summary = "\n\n".join([
            f"File: {f['path']}\n```\n{f['content'][:1000]}...\n```"
            for f in context["files"][:5]
        ])

        prompt = f"""Analyze this software development session and suggest relevant tags.

Session Information:
- Working Directory: {context['directory_name']}
- File Extensions Found: {', '.join(sorted(context['file_extensions']))}
- Directories: {', '.join(sorted(list(context['directories'])[:10]))}
- Existing Tags: {', '.join(context['existing_tags']) if context['existing_tags'] else 'None'}
- Description: {context['existing_description'] or 'None'}

Sample Files:
{files_summary}

Based on this information, suggest 5-10 highly relevant tags that describe:
1. Programming languages/frameworks used
2. Project domain/purpose (e.g., web-app, api, cli-tool, data-science)
3. Key technologies (e.g., database, authentication, frontend, backend)
4. Development aspects (e.g., testing, documentation, deployment)

Return ONLY the tags as a comma-separated list, with no explanations.
Use lowercase with hyphens (e.g., "web-app", "rest-api", "machine-learning").
Avoid duplicating existing tags unless they're highly relevant.

Tags:"""

        return prompt

    def _parse_tag_response(self, response_text: str) -> List[str]:
        """Parse tags from LLM response.

        Args:
            response_text: Raw LLM response.

        Returns:
            List of parsed tags.
        """
        # Extract tags from comma-separated response
        tags = []

        # Clean up response
        text = response_text.strip()

        # Split by commas or newlines
        for line in text.split('\n'):
            for tag in line.split(','):
                tag = tag.strip().lower()
                # Remove leading # or numbers
                tag = tag.lstrip('#0123456789. ')
                # Validate tag format
                if tag and 2 <= len(tag) <= 30 and all(c.isalnum() or c in '-_' for c in tag):
                    tags.append(tag)

        return tags

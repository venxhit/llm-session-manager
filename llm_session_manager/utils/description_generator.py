"""AI-powered session description generation."""

import os
from typing import Optional, Dict
from pathlib import Path
import structlog
from anthropic import Anthropic

from ..models import Session

logger = structlog.get_logger()


class DescriptionGenerator:
    """Generates intelligent descriptions for sessions using LLM analysis.

    Analyzes:
    - Project structure and files
    - Code content and patterns
    - Existing tags and metadata
    - Development context

    Creates concise, informative summaries.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize description generator.

        Args:
            api_key: Anthropic API key. If None, will try ANTHROPIC_API_KEY env var.
        """
        self.logger = structlog.get_logger()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("description_generator_initialized", provider="anthropic")
            except Exception as e:
                logger.warning("description_generator_init_failed", error=str(e))

    def is_available(self) -> bool:
        """Check if AI description generation is available.

        Returns:
            True if LLM client is initialized.
        """
        return self.client is not None

    def generate_description(
        self,
        session: Session,
        max_length: int = 200,
        context_files: int = 8
    ) -> Optional[str]:
        """Generate a description for a session using AI.

        Args:
            session: Session to describe.
            max_length: Maximum description length in characters.
            context_files: Number of files to sample for context.

        Returns:
            Generated description or None if generation fails.
        """
        if not self.is_available():
            logger.warning("description_generator_not_available")
            return None

        if not session.working_directory or not os.path.isdir(session.working_directory):
            logger.debug("no_working_directory", session_id=session.id)
            return None

        try:
            # Gather context
            context = self._gather_context(session, max_files=context_files)

            if not context["files"] and not context["readme_content"]:
                logger.debug("insufficient_context", session_id=session.id)
                return None

            # Build prompt
            prompt = self._build_description_prompt(session, context, max_length)

            # Call LLM
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            description = response.content[0].text.strip()

            # Ensure it's not too long
            if len(description) > max_length:
                description = description[:max_length-3] + "..."

            logger.info("description_generated",
                       session_id=session.id,
                       length=len(description))

            return description

        except Exception as e:
            logger.error("description_generation_failed", error=str(e))
            return None

    def _gather_context(self, session: Session, max_files: int = 8) -> Dict:
        """Gather context for description generation.

        Args:
            session: Session to analyze.
            max_files: Maximum files to sample.

        Returns:
            Dictionary with context information.
        """
        context = {
            "directory_name": Path(session.working_directory).name,
            "files": [],
            "readme_content": None,
            "package_info": None,
            "file_types": set(),
            "key_directories": set(),
            "tags": session.tags,
            "project_name": session.project_name,
        }

        try:
            # Look for README
            for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
                readme_path = os.path.join(session.working_directory, readme_name)
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            context["readme_content"] = f.read(2000)  # First 2KB
                            break
                    except (UnicodeDecodeError, IOError):
                        pass

            # Look for package.json or pyproject.toml
            package_json = os.path.join(session.working_directory, "package.json")
            if os.path.exists(package_json):
                try:
                    import json
                    with open(package_json, 'r', encoding='utf-8') as f:
                        pkg = json.load(f)
                        context["package_info"] = {
                            "name": pkg.get("name"),
                            "description": pkg.get("description"),
                            "type": "node"
                        }
                except Exception:
                    pass

            pyproject_toml = os.path.join(session.working_directory, "pyproject.toml")
            if os.path.exists(pyproject_toml):
                try:
                    with open(pyproject_toml, 'r', encoding='utf-8') as f:
                        content = f.read(1000)
                        context["package_info"] = {
                            "type": "python",
                            "content": content
                        }
                except Exception:
                    pass

            # Sample code files
            files_collected = 0
            for root, dirs, files in os.walk(session.working_directory):
                if files_collected >= max_files:
                    break

                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {
                    '__pycache__', 'node_modules', '.git', 'venv', 'env',
                    'build', 'dist', '.next', 'target'
                }]

                # Track key directories
                for d in dirs[:5]:
                    context["key_directories"].add(d.lower())

                for filename in files:
                    if files_collected >= max_files:
                        break

                    file_path = os.path.join(root, filename)
                    ext = Path(filename).suffix.lower()

                    if ext:
                        context["file_types"].add(ext)

                    # Sample interesting files
                    if ext in {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java'}:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read(2000)
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

    def _build_description_prompt(self, session: Session, context: Dict, max_length: int) -> str:
        """Build prompt for description generation.

        Args:
            session: Session to describe.
            context: Gathered context.
            max_length: Maximum description length.

        Returns:
            Formatted prompt string.
        """
        prompt_parts = [
            "Generate a concise, informative description for this development session.",
            "",
            f"Project: {context['directory_name']}",
        ]

        if context['project_name']:
            prompt_parts.append(f"Project Name: {context['project_name']}")

        if context['tags']:
            prompt_parts.append(f"Tags: {', '.join(context['tags'])}")

        if context['readme_content']:
            prompt_parts.extend([
                "",
                "README excerpt:",
                context['readme_content'][:500]
            ])

        if context['package_info']:
            if context['package_info'].get('description'):
                prompt_parts.append(f"\nPackage description: {context['package_info']['description']}")
            if context['package_info'].get('name'):
                prompt_parts.append(f"Package name: {context['package_info']['name']}")

        if context['files']:
            prompt_parts.extend([
                "",
                "Sample files:"
            ])
            for f in context['files'][:3]:
                prompt_parts.append(f"\n{f['path']}:")
                prompt_parts.append(f["content"][:300])

        if context['file_types']:
            prompt_parts.append(f"\nFile types: {', '.join(sorted(context['file_types']))}")

        if context['key_directories']:
            prompt_parts.append(f"Key directories: {', '.join(sorted(context['key_directories']))}")

        prompt_parts.extend([
            "",
            f"Generate a description (max {max_length} chars) that:",
            "1. Identifies the project purpose and domain",
            "2. Mentions key technologies or frameworks",
            "3. Describes what's being built or worked on",
            "",
            "Return ONLY the description text, no preamble or explanation.",
            "",
            "Description:"
        ])

        return "\n".join(prompt_parts)

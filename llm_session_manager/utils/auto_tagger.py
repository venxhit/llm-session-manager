"""Automatic tag suggestion based on session content analysis."""

import os
import re
from pathlib import Path
from typing import List, Dict, Set
from collections import Counter
import structlog

from ..models import Session

logger = structlog.get_logger()


class AutoTagger:
    """Suggests tags for sessions based on file content analysis.

    Analyzes:
    - File extensions (languages/frameworks)
    - Import statements
    - Keywords in code
    - Directory structure
    - Common patterns

    Future: Could use LLM for more intelligent tagging
    """

    # Language/framework detection from file extensions
    EXTENSION_TAGS = {
        '.py': ['python', 'backend'],
        '.js': ['javascript', 'frontend'],
        '.ts': ['typescript', 'frontend'],
        '.tsx': ['typescript', 'react', 'frontend'],
        '.jsx': ['javascript', 'react', 'frontend'],
        '.vue': ['vue', 'frontend'],
        '.java': ['java', 'backend'],
        '.go': ['golang', 'backend'],
        '.rs': ['rust', 'backend'],
        '.rb': ['ruby', 'backend'],
        '.php': ['php', 'backend'],
        '.cpp': ['cpp', 'systems'],
        '.c': ['c', 'systems'],
        '.swift': ['swift', 'ios'],
        '.kt': ['kotlin', 'android'],
        '.sql': ['database', 'sql'],
        '.html': ['html', 'frontend'],
        '.css': ['css', 'frontend'],
        '.scss': ['sass', 'frontend'],
        '.md': ['documentation'],
        '.json': ['config'],
        '.yaml': ['config'],
        '.yml': ['config'],
        '.toml': ['config'],
        '.sh': ['devops', 'scripting'],
        '.dockerfile': ['docker', 'devops'],
    }

    # Import pattern matching for frameworks/libraries
    IMPORT_PATTERNS = {
        # Python
        r'from\s+django': 'django',
        r'from\s+flask': 'flask',
        r'from\s+fastapi': 'fastapi',
        r'import\s+pytest': 'testing',
        r'from\s+sqlalchemy': 'sqlalchemy',
        r'import\s+pandas': 'data-science',
        r'import\s+numpy': 'data-science',
        r'from\s+tensorflow': 'ml',
        r'from\s+torch': 'ml',

        # JavaScript/TypeScript
        r'from\s+[\'"]react': 'react',
        r'from\s+[\'"]next': 'nextjs',
        r'from\s+[\'"]express': 'express',
        r'from\s+[\'"]vue': 'vue',
        r'from\s+[\'"]@angular': 'angular',
        r'from\s+[\'"]jest': 'testing',

        # General
        r'import.*axios': 'api',
        r'import.*graphql': 'graphql',
        r'import.*prisma': 'prisma',
        r'import.*mongodb': 'mongodb',
        r'import.*postgres': 'postgresql',
    }

    # Directory-based tags
    DIRECTORY_TAGS = {
        'api': 'api',
        'backend': 'backend',
        'frontend': 'frontend',
        'components': 'ui',
        'pages': 'ui',
        'routes': 'routing',
        'models': 'database',
        'migrations': 'database',
        'tests': 'testing',
        'test': 'testing',
        'docs': 'documentation',
        'scripts': 'automation',
        'deploy': 'devops',
        'docker': 'docker',
        'k8s': 'kubernetes',
        'kubernetes': 'kubernetes',
        'ci': 'ci-cd',
        'auth': 'authentication',
        'admin': 'admin',
    }

    # Keyword-based tags (case-insensitive)
    KEYWORD_TAGS = {
        'authentication': 'auth',
        'authorization': 'auth',
        'jwt': 'auth',
        'oauth': 'auth',
        'login': 'auth',
        'database': 'database',
        'migration': 'database',
        'schema': 'database',
        'api': 'api',
        'rest': 'rest-api',
        'graphql': 'graphql',
        'websocket': 'websockets',
        'cache': 'caching',
        'redis': 'redis',
        'queue': 'message-queue',
        'celery': 'celery',
        'worker': 'background-jobs',
        'cron': 'scheduling',
        'payment': 'payments',
        'stripe': 'payments',
        'email': 'email',
        'notification': 'notifications',
        'upload': 'file-upload',
        'download': 'file-download',
        'search': 'search',
        'elasticsearch': 'elasticsearch',
        'monitoring': 'monitoring',
        'logging': 'logging',
        'error': 'error-handling',
        'security': 'security',
        'performance': 'performance',
        'optimization': 'performance',
        'refactor': 'refactoring',
        'bugfix': 'bugfix',
        'feature': 'feature',
    }

    def __init__(self):
        """Initialize auto-tagger."""
        self.logger = structlog.get_logger()

    def suggest_tags(self, session: Session, max_tags: int = 10) -> List[str]:
        """Suggest tags for a session based on content analysis.

        Args:
            session: Session to analyze.
            max_tags: Maximum number of tags to return.

        Returns:
            List of suggested tags, ordered by relevance.
        """
        if not session.working_directory or not os.path.isdir(session.working_directory):
            logger.debug("no_working_directory", session_id=session.id)
            return []

        tag_counter = Counter()

        # Analyze file extensions
        extension_tags = self._analyze_extensions(session.working_directory)
        tag_counter.update(extension_tags)

        # Analyze directory structure
        directory_tags = self._analyze_directories(session.working_directory)
        tag_counter.update(directory_tags)

        # Analyze file content (imports, keywords)
        content_tags = self._analyze_content(session.working_directory)
        tag_counter.update(content_tags)

        # Use description if available
        if session.description:
            desc_tags = self._analyze_text(session.description)
            tag_counter.update(desc_tags)

        # Get most common tags
        suggested_tags = [tag for tag, count in tag_counter.most_common(max_tags)]

        logger.info("tags_suggested",
                   session_id=session.id,
                   count=len(suggested_tags),
                   tags=suggested_tags)

        return suggested_tags

    def _analyze_extensions(self, directory: str) -> Counter:
        """Analyze file extensions in directory.

        Args:
            directory: Directory to analyze.

        Returns:
            Counter of tags found.
        """
        tags = Counter()

        try:
            for root, dirs, files in os.walk(directory):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {
                    '__pycache__', 'node_modules', '.git', 'venv', 'env', 'build', 'dist'
                }]

                for filename in files:
                    ext = Path(filename).suffix.lower()
                    if ext in self.EXTENSION_TAGS:
                        for tag in self.EXTENSION_TAGS[ext]:
                            tags[tag] += 1

        except Exception as e:
            logger.debug("extension_analysis_error", error=str(e))

        return tags

    def _analyze_directories(self, directory: str) -> Counter:
        """Analyze directory names for patterns.

        Args:
            directory: Directory to analyze.

        Returns:
            Counter of tags found.
        """
        tags = Counter()

        try:
            for root, dirs, files in os.walk(directory):
                for dir_name in dirs:
                    dir_lower = dir_name.lower()
                    if dir_lower in self.DIRECTORY_TAGS:
                        tags[self.DIRECTORY_TAGS[dir_lower]] += 2  # Weight directory names higher

        except Exception as e:
            logger.debug("directory_analysis_error", error=str(e))

        return tags

    def _analyze_content(self, directory: str, sample_files: int = 50) -> Counter:
        """Analyze file content for imports and keywords.

        Args:
            directory: Directory to analyze.
            sample_files: Maximum number of files to sample.

        Returns:
            Counter of tags found.
        """
        tags = Counter()
        files_analyzed = 0

        try:
            for root, dirs, files in os.walk(directory):
                if files_analyzed >= sample_files:
                    break

                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {
                    '__pycache__', 'node_modules', '.git', 'venv', 'env', 'build', 'dist'
                }]

                for filename in files:
                    if files_analyzed >= sample_files:
                        break

                    file_path = os.path.join(root, filename)
                    ext = Path(filename).suffix.lower()

                    # Only analyze text files
                    if ext not in {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php'}:
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(50000)  # Read first 50KB

                            # Check for import patterns
                            for pattern, tag in self.IMPORT_PATTERNS.items():
                                if re.search(pattern, content, re.IGNORECASE):
                                    tags[tag] += 3  # Weight imports highly

                            # Check for keywords
                            content_lower = content.lower()
                            for keyword, tag in self.KEYWORD_TAGS.items():
                                if keyword in content_lower:
                                    tags[tag] += 1

                            files_analyzed += 1

                    except (UnicodeDecodeError, IOError):
                        continue

        except Exception as e:
            logger.debug("content_analysis_error", error=str(e))

        return tags

    def _analyze_text(self, text: str) -> Counter:
        """Analyze text (like description) for keywords.

        Args:
            text: Text to analyze.

        Returns:
            Counter of tags found.
        """
        tags = Counter()
        text_lower = text.lower()

        for keyword, tag in self.KEYWORD_TAGS.items():
            if keyword in text_lower:
                tags[tag] += 2  # Weight description matches

        return tags

    def auto_tag_session(self, session: Session, min_confidence: int = 3) -> List[str]:
        """Automatically tag a session (only high-confidence tags).

        Args:
            session: Session to tag.
            min_confidence: Minimum count for a tag to be included.

        Returns:
            List of auto-assigned tags.
        """
        if not session.working_directory or not os.path.isdir(session.working_directory):
            return []

        tag_counter = Counter()

        # Analyze everything
        tag_counter.update(self._analyze_extensions(session.working_directory))
        tag_counter.update(self._analyze_directories(session.working_directory))
        tag_counter.update(self._analyze_content(session.working_directory))

        if session.description:
            tag_counter.update(self._analyze_text(session.description))

        # Only return tags with high confidence
        confident_tags = [tag for tag, count in tag_counter.items() if count >= min_confidence]

        return confident_tags[:10]  # Max 10 auto-tags

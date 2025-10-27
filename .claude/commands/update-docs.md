Update project documentation automatically.

This command invokes the doc-generator skill to update documentation.

Steps:
1. Detect what has changed (git diff if available)
2. Identify documentation that needs updating
3. Generate/update relevant docs
4. Validate all links and examples
5. Provide summary of changes

Documentation types to update:
- README.md (if new features added)
- API.md (if API endpoints changed)
- CLI.md (if CLI commands changed)
- CHANGELOG.md (based on commits)

If specific documentation type is requested, focus on that.

Options:
- --all: Update all documentation
- --api: Update API docs only
- --cli: Update CLI docs only
- --changelog: Update changelog only

Use the doc-generator skill for detailed implementation.

from django.apps import AppConfig


class ChangelogConfig(AppConfig):
    name = 'changelog'

    def ready(self):
        # We need to import signals but Ruff (python linter) gets angry about unused imports
        from . import signals  # noqa: F401

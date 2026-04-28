from django.apps import AppConfig
from django.conf import settings


class ChangelogConfig(AppConfig):
    name = 'changelog'

    def ready(self):
        # We need to import signals but Ruff (python linter) gets angry about unused imports
        if not getattr(settings, 'RABBITMQ_ENABLED', False):
            return
        from . import signals  # noqa: F401

# user_app/apps.py
from django.apps import AppConfig

class UserAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_app"

    def ready(self):
        try:
            from . import signals  # noqa: F401
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to import user_app.signals")
